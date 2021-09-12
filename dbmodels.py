from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    time_created = Column(Integer, nullable=False)


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, nullable=False, index=True)
    text_front = Column(String, nullable=False)
    text_back = Column(String, nullable=False)
    time_created = Column(Integer, nullable=False)


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, nullable=False, index=True)
    direction = Column(String, nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    status = Column(String, nullable=False)
    current_review_interval = Column(Integer, nullable=False)
    time_created = Column(Integer, nullable=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, index=True)
    time_created = Column(Integer, nullable=False)
    time_completed = Column(Integer, nullable=False)
    review_status = Column(String, nullable=False)
    correct = Column(Integer, nullable=False)
