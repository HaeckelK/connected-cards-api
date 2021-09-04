from dataclasses import dataclass, asdict
from typing import List
import time

from flask import Flask, jsonify, request
from flask_cors import CORS


@dataclass
class DeckIn:
    name: str


@dataclass
class DeckOut:
    id: int
    name: str
    cards_total: int
    time_created: int
    count_reviews_due: int


@dataclass
class NoteIn:
    deck_id: int
    text_front: str
    text_back: str


@dataclass
class NoteOut:
    id: int
    deck_id: int
    text_front: str
    text_back: str
    time_created: int


# TODO remove question and answer, these are only to be stored in Note
# e.g. what happens when Note content gets edited? You have to edit all the cards too with this current setup.
@dataclass
class CardIn:
    note_id: int
    direction: str
    # TODO remove all below
    deck_id: int
    question: str
    answer: str


# @dataclass
# class CardModel:
#     id: str
#     note_id: int
#     direction: str


@dataclass
class CardOut:
    id: int
    deck_id: int
    note_id: int
    direction: str
    question: str
    answer: str
    status: str
    time_created: int


@dataclass
class ReviewOut:
    id: int
    card: CardOut
    time_created: int
    time_completed: int
    review_status: str
    correct: int


DECKS, NOTES = [], []
CARDS: List[CardOut] = []
REVIEWS: List[ReviewOut] = []


app = Flask(__name__)
# TODO limit to correct origin etc
CORS(app)


@app.route("/decks", methods=["GET"])
def get_decks():
    return jsonify([asdict(x) for x in DECKS])


@app.route("/decks/<int:id>", methods=["GET"])
def get_deck_by_id(id: int):
    for deck in DECKS:
        if deck.id == id:
            return jsonify(asdict(deck))
    return f"Deck not found for id: {id}", 400


@app.route("/decks", methods=["POST"])
def create_deck():
    name = request.form["name"]
    new_deck = DeckIn(name=name)
    deck = add_new_deck(new_deck)
    return jsonify(asdict(deck))


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
    for review in REVIEWS:
        if review.id == id:
            review.correct = True
            review.time_completed = timestamp()
            review.review_status = "reviewed"
    return "done"


@app.route("/reviews/mark_incorrect/<int:id>", methods=["GET"])
def mark_review_incorrect(id: int):
    for review in REVIEWS:
        if review.id == id:
            review.correct = False
            review.time_completed = timestamp()
            review.review_status = "reviewed"
    return "done"


# Actions that should be behind worker
@app.route("/generate_reviews", methods=["GET"])
def generate_reviews():
    global REVIEWS
    REVIEWS = []
    for i, card in enumerate(CARDS):
        review = ReviewOut(
            id=i + 1, card=card, time_created=timestamp(), time_completed=-1, review_status="not_reviewed", correct=-1
        )
        REVIEWS.append(review)
    return f"Reviews Generated {len(REVIEWS)}"


@app.route("/wipe", methods=["GET"])
def wipe_data():
    global DECKS, CARDS, REVIEWS, NOTES
    DECKS = []
    CARDS = []
    NOTES = []
    REVIEWS = []
    return "wiped"


# Actual CRUD
def add_new_deck(new_deck: DeckIn) -> DeckOut:
    id = len(DECKS) + 1
    deck = DeckOut(id=id, name=new_deck.name, cards_total=0, time_created=timestamp(), count_reviews_due=123)
    DECKS.append(deck)
    return deck


def add_new_note(new_note: NoteIn) -> NoteOut:
    id = len(NOTES) + 1
    note = NoteOut(**asdict(new_note), id=id, time_created=timestamp())
    NOTES.append(note)
    return note


def add_new_card(new_card: CardIn):
    id = len(CARDS) + 1
    card = CardOut(id=id, **asdict(new_card), status="new", time_created=timestamp())
    CARDS.append(card)
    return


# Utils
def timestamp() -> int:
    return int(time.time())
