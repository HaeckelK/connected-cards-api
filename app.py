from dataclasses import asdict
from typing import List, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS
from fastapi import FastAPI

from utils import timestamp
from scheduler import Scheduler
from models import DeckIn, DeckOut, NoteIn, NoteOut, CardIn, CardOut, ReviewOut

MINIMUM_INTERVAL = 86400


DECKS, NOTES = [], []
CARDS: List[CardOut] = []
REVIEWS: List[ReviewOut] = []


app = Flask(__name__)
# TODO limit to correct origin etc
CORS(app)

fastapp = FastAPI()

scheduler = Scheduler(new_cards_limit=100,
                      total_cards_limit=100,
                      allow_cards_from_same_note=True)


@fastapp.get("/decks", response_model=List[DeckOut])
async def fast_get_decks():
    # TODO should work this out after reviews?
    # Update deck stats
    card_count = get_count_cards_by_deck(status="new")
    for deck in DECKS:
        deck.count_new_cards = card_count.get(deck.id, 0)
    return DECKS


@app.route("/decks", methods=["GET"])
def get_decks():
    # TODO should work this out after reviews?
    # Update deck stats
    card_count = get_count_cards_by_deck(status="new")
    for deck in DECKS:
        deck.count_new_cards = card_count.get(deck.id, 0)
    return jsonify([x.dict() for x in DECKS])


@app.route("/decks/<int:id>", methods=["GET"])
def get_deck_by_id(id: int):
    for deck in DECKS:
        if deck.id == id:
            return jsonify(deck.dict())
    return f"Deck not found for id: {id}", 400


@fastapp.post("/decks", response_model=DeckOut)
async def fast_create_deck(new_deck: DeckIn):
    deck = add_new_deck(new_deck)
    return deck


@app.route("/decks", methods=["POST"])
def create_deck():
    name = request.form["name"]
    new_deck = DeckIn(name=name)
    deck = add_new_deck(new_deck)
    return jsonify(deck.dict())


@app.route("/notes", methods=["GET"])
def get_notes():
    deck_id = request.args.get("deck", None)
    if deck_id:
        return jsonify([asdict(x) for x in NOTES if int(x.deck_id) == int(deck_id)])
    else:
        return jsonify([asdict(x) for x in NOTES])


@app.route("/notes", methods=["POST"])
def create_note():
    text_front = request.form["text_front"]
    text_back = request.form["text_back"]
    deck_id = int(request.form["deck_id"])

    new_note = NoteIn(deck_id=deck_id, text_front=text_front, text_back=text_back)

    note = add_new_note(new_note)

    # Add cards from note
    add_new_card(
        CardIn(
            note_id=note.id, direction="regular", deck_id=note.deck_id, question=note.text_front, answer=note.text_back
        )
    )
    add_new_card(
        CardIn(
            note_id=note.id, direction="reverse", deck_id=note.deck_id, question=note.text_back, answer=note.text_front
        )
    )

    return jsonify(asdict(note))


@app.route("/cards", methods=["GET"])
def get_cards():
    return jsonify([asdict(x) for x in CARDS])


@app.route("/reviews", methods=["GET"])
def get_reviews():
    # TODO check this isn't amending REVIEWs
    reviews = [x for x in REVIEWS]
    if int(request.args.get("due", default=0)) == 1:
        reviews = [x for x in reviews if x.review_status == "not_reviewed"]
    deck_id = request.args.get("deck", None)
    if deck_id:
        reviews = [x for x in reviews if int(x.card.deck_id) == int(deck_id)]
    return jsonify([asdict(x) for x in reviews])


@app.route("/reviews/mark_correct/<int:id>", methods=["GET"])
def mark_review_correct(id: int):
    # TODO DRY see mark_review_incorrect
    for review in REVIEWS:
        if review.id == id:
            review.correct = True
            review.time_completed = timestamp()
            review.review_status = "reviewed"
            change_card_status(review.card.id, status="seen")
            review.card.time_latest_review = scheduler.review_time
            # TODO what's the growth rate - need some class for managing that
            if review.card.current_review_interval == -1:
                review.card.current_review_interval = MINIMUM_INTERVAL
            else:
                review.card.current_review_interval *= 2
    return "done"


@app.route("/reviews/mark_incorrect/<int:id>", methods=["GET"])
def mark_review_incorrect(id: int):
    for review in REVIEWS:
        if review.id == id:
            review.correct = False
            review.time_completed = timestamp()
            review.review_status = "reviewed"
            change_card_status(review.card.id, status="seen")
            review.card.time_latest_review = scheduler.review_time
    return "done"


# Actions that should be behind worker
@app.route("/generate_reviews", methods=["GET"])
def generate_reviews():
    global REVIEWS
    REVIEWS = scheduler.create_reviews(reviews=REVIEWS, cards=CARDS)
    return f"Reviews Generated {len(REVIEWS)}"


@app.route("/wipe", methods=["GET"])
def wipe_data():
    global DECKS, CARDS, REVIEWS, NOTES
    DECKS = []
    CARDS = []
    NOTES = []
    REVIEWS = []
    return "wiped"


@fastapp.get("/wipe")
def fast_wipe_data():
    global DECKS, CARDS, REVIEWS, NOTES
    DECKS = []
    CARDS = []
    NOTES = []
    REVIEWS = []
    return "wiped"


@app.route("/wipe/reviews", methods=["GET"])
def wipe_reviews():
    global REVIEWS, CARDS
    REVIEWS = []
    for card in CARDS:
        card.status = "new"
    return "wiped"


@app.route("/increment_scheduler", methods=["GET"])
def increment_scheduler():
    scheduler.review_time += 86400
    return f"New time: {scheduler.review_time}"


# Actual CRUD
def add_new_deck(new_deck: DeckIn) -> DeckOut:
    id = len(DECKS) + 1
    deck = DeckOut(id=id, name=new_deck.name, notes_total=0, cards_total=0, time_created=timestamp(), count_reviews_due=0, count_new_cards=0)
    DECKS.append(deck)
    return deck


def add_new_note(new_note: NoteIn) -> NoteOut:
    id = len(NOTES) + 1
    note = NoteOut(**asdict(new_note), id=id, time_created=timestamp())
    NOTES.append(note)
    # Update deck stats
    card_count = get_count_notes_by_deck()
    for deck in DECKS:
        deck.notes_total = card_count.get(deck.id, 0)
    return note


def add_new_card(new_card: CardIn):
    id = len(CARDS) + 1
    card = CardOut(id=id, **asdict(new_card), status="new", time_created=timestamp(), time_latest_review=-1, current_review_interval=-1)
    CARDS.append(card)
    # Update deck stats
    card_count = get_count_cards_by_deck()
    for deck in DECKS:
        deck.cards_total = card_count.get(deck.id, 0)
    return


def change_card_status(id: int, status: str):
    for card in CARDS:
        if int(card.id) == int(id):
            card.status = status
            return
    return


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


def get_count_notes_by_deck() -> Dict[int, int]:
    count = {}
    for card in NOTES:
        try:
            count[card.deck_id] += 1
        except  KeyError:
            count[card.deck_id] = 1
    return count
