from dataclasses import asdict

from scheduler import Scheduler
from models import CardOut, CardIn, ReviewOut
import scheduler as module


def test_scheduler_init():
    scheduler = Scheduler(new_cards_limit=100, allow_cards_from_same_note=True, total_cards_limit=100)


# create_reviews
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


def test_scheduler_create_reviews_dispersal_group(monkeypatch):
    monkeypatch.setattr(module, "timestamp", lambda: 0)
    # Given a scheduler, empty reviews and multiple cards, and some with same dispersal group
    scheduler = Scheduler(new_cards_limit=100, allow_cards_from_same_note=True, total_cards_limit=100)
    # TODO connect new card creation to app.py functions
    # TODO options on regular
    new_card = CardIn(note_id=1, direction="regular", deck_id=1, question="Hello", answer="Bonjour")
    card_template = CardOut(
            id=1,
            **asdict(new_card),
            status="new",
            time_created=0,
            time_latest_review=-1,
            current_review_interval=-1
        )
    card1 = card_template.copy()
    card2 = card_template.copy()
    card3 = card_template.copy()

    card1.id = 1
    card2.id = 2
    card3.id = 3

    card2.note_id = 2
    card2.dispersal_groups = [1]  # TODO make this a random number

    card3.note_id = 3
    card3.dispersal_groups = [1]

    cards = [card1, card2, card3]
    reviews = []
    # When creating reviews
    reviews = scheduler.create_reviews(reviews=reviews, cards=cards)
    # Then review created with expected attributes
    assert len(reviews) == 2
    assert set([review.card.id for review in reviews]) == set([1,2])


def test_scheduler_create_reviews_dispersal_groups_all_distinct():
    # Given a scheduler, empty reviews and multiple cards, with no common dispersal group ids
    scheduler = Scheduler(new_cards_limit=100, allow_cards_from_same_note=True, total_cards_limit=100)
    # TODO connect new card creation to app.py functions
    # TODO options on regular
    new_card = CardIn(note_id=1, direction="regular", deck_id=1, question="Hello", answer="Bonjour")
    card_template = CardOut(
            id=1,
            **asdict(new_card),
            status="new",
            time_created=0,
            time_latest_review=-1,
            current_review_interval=-1
        )
    card1 = card_template.copy()
    card2 = card_template.copy()
    card3 = card_template.copy()

    card1.id = 1
    card2.id = 2
    card3.id = 3

    card1.dispersal_groups = [1]

    card2.note_id = 2
    card2.dispersal_groups = [2]

    card3.note_id = 3
    card3.dispersal_groups = [3]

    cards = [card1, card2, card3]
    reviews = []
    # When creating reviews
    reviews = scheduler.create_reviews(reviews=reviews, cards=cards)
    # Then review created with expected attributes
    assert len(reviews) == 3
    assert set([review.card.id for review in reviews]) == set([1,2,3])


# TODO need to check what happens when running for multiple days
# card scheduling
def test_schedule_schedule_card_new_correct(monkeypatch):
    monkeypatch.setattr(module, "timestamp", lambda: 0)
    # Given a scheduler and a new card
    scheduler = Scheduler(new_cards_limit=100, allow_cards_from_same_note=True, total_cards_limit=100)
    # TODO connect new card creation to app.py functions
    new_card = CardIn(note_id=1, direction="regular", deck_id=1, question="Hello", answer="Bonjour")
    card = CardOut(
            id=1,
            **asdict(new_card),
            status="new",
            time_created=0,
            time_latest_review=-1,
            current_review_interval=-1
        )
    # When scheduling next review for correct answer
    card = scheduler.schedule_card(card, correct=True)
    # Then card time_latest_review updated
    assert card.time_latest_review == scheduler.review_time
    # Then current_review_interval is scheduler minimum
    assert card.current_review_interval == scheduler.minimum_review_interval


def test_schedule_schedule_card_new_incorrect(monkeypatch):
    monkeypatch.setattr(module, "timestamp", lambda: 0)
    # Given a scheduler and a new card
    scheduler = Scheduler(new_cards_limit=100, allow_cards_from_same_note=True, total_cards_limit=100)
    # TODO connect new card creation to app.py functions
    new_card = CardIn(note_id=1, direction="regular", deck_id=1, question="Hello", answer="Bonjour")
    card = CardOut(
            id=1,
            **asdict(new_card),
            status="new",
            time_created=0,
            time_latest_review=-1,
            current_review_interval=-1
        )
    # When scheduling next review for incorrect answer
    card = scheduler.schedule_card(card, correct=False)
    # Then card time_latest_review updated
    assert card.time_latest_review == scheduler.review_time
    # Then current_review_interval not updated
    assert card.current_review_interval == -1
