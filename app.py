from dataclasses import asdict
from typing import List, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException

from utils import timestamp
from scheduler import Scheduler
from models import DeckIn, DeckOut, NoteIn, NoteOut, CardIn, CardOut, ReviewOut
import dbmodels
from database import engine, SessionLocal
from dbmodels import Deck, Note, Card, Review, DispersalGroup, NoteConnection
from sqlalchemy.orm import Session

MINIMUM_INTERVAL = 86400

CARDS: List[CardOut] = []
REVIEWS: List[ReviewOut] = []

dbmodels.Base.metadata.create_all(bind=engine)

app = FastAPI()

scheduler = Scheduler(new_cards_limit=100,
                      total_cards_limit=100,
                      allow_cards_from_same_note=True,
                      success_increment_factor=2.0)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/decks", response_model=List[DeckOut])
async def get_decks(db: Session = Depends(get_db)):
    query = db.query(Deck).all()
    db_decks = []
    for deck in query:
        data = deck.__dict__
        data.pop('_sa_instance_state')
        data["notes_total"] = -1
        data["cards_total"] = -1
        data["count_reviews_due"] = -1
        data["count_new_cards"] = -1

        db_decks.append(DeckOut(**data))

    # Update deck stats
    card_count = get_count_cards_by_deck(status="new")

    for deck in db_decks:
        deck.count_new_cards = card_count.get(deck.id, 0)
    return db_decks


@app.get("/decks/{id}", response_model=DeckOut)
async def get_deck_by_id(id: int, db: Session = Depends(get_db)):
    db_deck = db.query(Deck).filter(Deck.id == id).first()
    if db_deck:
        # TODO DRY see GET
        data = db_deck.__dict__
        data.pop('_sa_instance_state')
        data["notes_total"] = -1
        data["cards_total"] = -1
        data["count_reviews_due"] = -1
        data["count_new_cards"] = -1

        deck = DeckOut(**data)
        return deck
    else:
        raise HTTPException(status_code=400, detail=f"Deck not found for id: {id}")


@app.post("/decks", response_model=DeckOut)
async def create_deck(new_deck: DeckIn, db: Session = Depends(get_db)):
    db_deck = Deck(name=new_deck.name, time_created=timestamp())
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)

    # TODO DRY see GET
    data = db_deck.__dict__
    data.pop('_sa_instance_state')
    data["notes_total"] = -1
    data["cards_total"] = -1
    data["count_reviews_due"] = -1
    data["count_new_cards"] = -1

    deck = DeckOut(**data)
    return deck


@app.get("/notes", response_model=List[NoteOut])
async def get_notes(deck_id: Optional[str]=None, db: Session = Depends(get_db)):
    if deck_id:
        db_notes = db.query(Note).filter(Note.deck_id == deck_id).all()
        if db_notes:
            output = []
            for db_note in db_notes:
                # TODO DRY see below
                data = db_note.__dict__
                data.pop('_sa_instance_state')
                output.append(NoteOut(**data))
            return output
        else:
            raise HTTPException(status_code=400, detail=f"Note not found for deck id: {deck_id}")
    else:
        output = []
        notes = db.query(Note).all()
        for note in notes:
            data = note.__dict__
            data.pop('_sa_instance_state')
            output.append(NoteOut(**data))
        return output


@app.post("/notes", response_model=NoteOut)
async def create_note(new_note: NoteIn, db: Session = Depends(get_db)):
    note = add_new_note(new_note, db)

    # Add cards from note
    add_new_card(
        CardIn(
            note_id=note.id, direction="regular", deck_id=note.deck_id, question=note.text_front, answer=note.text_back
        ),
        db
    )
    add_new_card(
        CardIn(
            note_id=note.id, direction="reverse", deck_id=note.deck_id, question=note.text_back, answer=note.text_front
        ),
        db
    )

    return note


@app.get("/cards", response_model=List[CardOut])
async def get_cards():
    return CARDS


@app.get("/reviews", response_model=List[ReviewOut])
async def get_reviews(due: int=0, deck_id:int=None):
    reviews = [x for x in REVIEWS]
    if due == 1:
        reviews = [x for x in reviews if x.review_status == "not_reviewed"]

    if deck_id:
        reviews = [x for x in reviews if int(x.card.deck_id) == int(deck_id)]
    return reviews


@app.get("/reviews/mark_correct/{id}")
async def mark_review_correct(id: int):
    # TODO DRY see mark_review_incorrect
    for review in REVIEWS:
        if review.id == id:
            review.correct = True
            review.time_completed = timestamp()
            review.review_status = "reviewed"
            review.card.status = "seen"
            scheduler.schedule_card(card=review.card, correct=True)
            review.card = grade_card(card=review.card)
    return "done"


@app.get("/reviews/mark_incorrect/{id}")
async def mark_review_incorrect(id: int):
    for review in REVIEWS:
        if review.id == id:
            review.correct = False
            review.time_completed = timestamp()
            review.review_status = "reviewed"
            review.card.status = "seen"
            scheduler.schedule_card(card=review.card, correct=False)
            review.card = grade_card(card=review.card)
    return "done"

# Temporary scoffolding
@app.get("/save")
def save_memory_to_database(db: Session = Depends(get_db)):
    # Currently deletes all data from db - obviously not safe
    dbmodels.Base.metadata.drop_all(bind=engine)
    dbmodels.Base.metadata.create_all(bind=engine)


    for review in REVIEWS:
        db_review = Review(id=review.id, card_id=review.card.id, time_created=review.time_created, time_completed=review.time_completed, review_status=review.review_status, correct=review.correct)
        db.add(db_review)
    db.commit()
    return "Success"


# Actions that should be behind worker
@app.get("/generate_reviews")
def generate_reviews():
    global REVIEWS
    REVIEWS = scheduler.create_reviews(reviews=REVIEWS, cards=CARDS)
    return f"Reviews Generated {len(REVIEWS)}"


@app.get("/wipe")
def wipe_data():
    dbmodels.Base.metadata.drop_all(bind=engine)
    dbmodels.Base.metadata.create_all(bind=engine)
    global CARDS, REVIEWS
    CARDS = []
    REVIEWS = []
    return "wiped"


@app.get("/wipe/reviews")
def wipe_reviews():
    global REVIEWS, CARDS
    REVIEWS = []
    for card in CARDS:
        card.status = "new"
    return "reviews wiped"


@app.get("/increment_scheduler")
def increment_scheduler():
    scheduler.review_time += 86400
    return f"New time: {scheduler.review_time}"


# Actual CRUD
def add_new_note(new_note: NoteIn, db: Session) -> NoteOut:
    db_note = Note(deck_id=new_note.deck_id, text_front=new_note.text_front, text_back=new_note.text_back, time_created=timestamp(),
                    audio_front="", audio_back="", image_front="", image_back="")
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    # TODO DRY see GET notes
    data = db_note.__dict__
    data.pop('_sa_instance_state')
    note = NoteOut(**data)

    return note


def add_new_card(new_card: CardIn, db: Session):
    id = len(CARDS) + 1
    card = CardOut(id=id, **asdict(new_card), status="new", time_created=timestamp(), time_latest_review=-1, current_review_interval=-1, grade="GRADE_NOT_ADDED")
    card = grade_card(card)
    CARDS.append(card)

    # TODO disconnect from CARDS
    db_card = Card(id=card.id, note_id=card.note_id, direction=card.direction,question=card.question, answer=card.answer, status=card.status, current_review_interval=card.current_review_interval, time_created=card.time_created,
                    grade=card.grade)
    db.add(db_card)
    db.commit()
    return


def change_card_status(id: int, status: str):
    for card in CARDS:
        if int(card.id) == int(id):
            card.status = status
            return
    return


def grade_card(card: CardOut) -> CardOut:
    # TODO add actual boundary based functionality
    card.grade = str(card.current_review_interval)[::-1]
    return card


# Under the hood data store work
def get_count_cards_by_deck(status="all") -> Dict[int, int]:
    count = {}
    if status == "all":
        cards = [x for x in CARDS]
    else:
        cards = [x for x in CARDS if x.status == status]
    for card in cards:
        try:
            count[card.deck_id] += 1
        except  KeyError:
            count[card.deck_id] = 1
    return count
