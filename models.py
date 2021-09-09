from dataclasses import dataclass
from typing import List

from pydantic import BaseModel


class DeckIn(BaseModel):
    name: str


class DeckOut(BaseModel):
    id: int
    name: str
    notes_total: int
    cards_total: int
    time_created: int
    count_reviews_due: int
    count_new_cards: int


class NoteIn(BaseModel):
    deck_id: int
    text_front: str
    text_back: str


class NoteOut(BaseModel):
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


class CardOut(BaseModel):
    id: int
    deck_id: int
    note_id: int
    direction: str
    question: str
    answer: str
    status: str
    time_created: int
    time_latest_review: int
    current_review_interval: int
    dispersal_batch: List[int] = []


class ReviewOut(BaseModel):
    id: int
    card: CardOut
    time_created: int
    time_completed: int
    review_status: str
    correct: int
