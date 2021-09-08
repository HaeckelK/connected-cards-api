from dataclasses import asdict

from scheduler import Scheduler
from models import CardOut, CardIn, ReviewOut
import scheduler as module


def test_scheduler_init():
    scheduler = Scheduler(new_cards_limit=100, allow_cards_from_same_note=True, total_cards_limit=100)


def test_scheduler_create_reviews_empty():
    # Given a scheduler and empty cards and reviews
    scheduler = Scheduler(new_cards_limit=100, allow_cards_from_same_note=True, total_cards_limit=100)
    cards = []
    reviews = []
    # When creating reviews
    reviews = scheduler.create_reviews(reviews=reviews, cards=cards)
    # Then no reviews created
    assert not reviews


def test_scheduler_create_reviews_properties(monkeypatch):
    monkeypatch.setattr(module, "timestamp", lambda: 0)
    # Given a scheduler, empty reviews and a card
    scheduler = Scheduler(new_cards_limit=100, allow_cards_from_same_note=True, total_cards_limit=100)
    # TODO connect new card creation to app.py functions
    # TODO options on regular
    new_card = CardIn(note_id=1, direction="regular", deck_id=1, question="Hello", answer="Bonjour")
    cards = [
        CardOut(
            id=1,
            **asdict(new_card),
            status="new",
            time_created=0,
            time_latest_review=-1,
            current_review_interval=-1
        )
    ]
    reviews = []
    # When creating reviews
    reviews = scheduler.create_reviews(reviews=reviews, cards=cards)
    # Then review created with expected attributes
    assert reviews == [
        ReviewOut(
            id=1,
            card=CardOut(
                id=1,
                deck_id=1,
                note_id=1,
                direction="regular",
                question="Hello",
                answer="Bonjour",
                status="new",
                time_created=0,
                time_latest_review=-1,
                current_review_interval=-1,
            ),
            time_created=0,
            time_completed=-1,
            review_status="not_reviewed",
            correct=-1,
        )
    ]


# TODO need to check what happens when running for multiple days
