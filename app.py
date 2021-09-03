from dataclasses import dataclass, asdict
from typing import List

from flask import Flask, jsonify, request


@dataclass
class DeckIn:
    name: str


@dataclass
class DeckOut:
    id: int
    name: str
    cards_total: int


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


DECKS, NOTES = [], []
CARDS: List[CardOut] = []


app = Flask(__name__)


@app.route("/decks", methods=["GET"])
def get_decks():
    return jsonify([asdict(x) for x in DECKS])


@app.route("/decks", methods=["POST"])
def create_deck():
    name = request.form["name"]
    new_deck = DeckIn(name=name)
    deck = add_new_deck(new_deck)
    return jsonify(asdict(deck))


@app.route("/notes", methods=["GET"])
def get_notes():
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


# Actual CRUD
def add_new_deck(new_deck: DeckIn) -> DeckOut:
    id = len(DECKS) + 1
    deck = DeckOut(id=id, name=new_deck.name, cards_total=0)
    DECKS.append(deck)
    return deck


def add_new_note(new_note: NoteIn) -> NoteOut:
    id = len(NOTES) + 1
    note = NoteOut(**asdict(new_note), id=id)
    NOTES.append(note)
    return note


def add_new_card(new_card: CardIn):
    id = len(CARDS) + 1
    card = CardOut(id=id, **asdict(new_card))
    CARDS.append(card)
    return
