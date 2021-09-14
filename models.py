from dataclasses import dataclass
from typing import List

from pydantic import BaseModel


class DeckIn(BaseModel):
    name: str


class DeckOut(BaseModel):
    id: int  # From database
    name: str  # From database
    notes_total: int  # Calculated
    cards_total: int  # Calculated
    time_created: int  # From database
    count_reviews_due: int  # Calculated
    count_new_cards: int  # Calculated


class NoteIn(BaseModel):
    deck_id: int
    text_front: str
    text_back: str


class NoteOut(BaseModel):
    id: int  # From database
    deck_id: int  # From database
    text_front: str  # From database
    text_back: str  # From database
    audio_front: str  # From database
    audio_back: str  # From database
    image_front: str  # From database
    image_back: str  # From database
    time_created: int  # From database
    # cards_total: int # Calculated


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
    id: int  # From database
    deck_id: int  # Calculated
    note_id: int  # From database
    direction: str  # From database
    question: str  # From database
    answer: str  # From database
    status: str  # From database
    time_created: int  # From database
    time_latest_review: int  # Calculated
    current_review_interval: int  # From database
    dispersal_groups: List[int] = []  # From database


class ReviewOut(BaseModel):
    id: int  # From database
    card: CardOut  # Calculated
    time_created: int  # From database
    time_completed: int  # From database
    review_status: str  # From database
    correct: int  # From database
