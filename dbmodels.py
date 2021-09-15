from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    time_created = Column(Integer, nullable=False)
    notes = relationship("Note")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey('decks.id'))
    text_front = Column(String, nullable=False)
    text_back = Column(String, nullable=False)
    audio_front = Column(String, nullable=False)
    audio_back = Column(String, nullable=False)
    image_front = Column(String, nullable=False)
    image_back = Column(String, nullable=False)
    time_created = Column(Integer, nullable=False)
    cards = relationship("Card")


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey('notes.id'))
    direction = Column(String, nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    status = Column(String, nullable=False)
    current_review_interval = Column(Integer, nullable=False)
    time_created = Column(Integer, nullable=False)
    reviews = relationship("Review")
    grade = Column(String, nullable=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey('cards.id'))
    time_created = Column(Integer, nullable=False)
    time_completed = Column(Integer, nullable=False)
    review_status = Column(String, nullable=False)
    correct = Column(Integer, nullable=False)


class NoteConnection(Base):
    __tablename__ = "note_connections"

    id = Column(Integer, primary_key=True, index=True)
    dependent_note_id = Column(Integer, ForeignKey('notes.id'))
    required_note_id = Column(Integer, ForeignKey('notes.id'))


class DispersalGroup(Base):
    __tablename__ = "dispersal_groups"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey('cards.id'))
    group_id = Column(Integer, nullable=False)
