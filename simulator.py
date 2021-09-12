from dataclasses import asdict
from typing import List

from scheduler import Scheduler
from models import CardIn, CardOut
from utils import timestamp


def create_cards(note_id: int, directions: List[str], next_id: int) -> List[CardOut]:
    cards = []
    for i, direction in enumerate(directions):
        new_card = CardIn(note_id=note_id, direction=direction, deck_id=1, question="question", answer="answer")
        card = CardOut(
                id=next_id + i,
                **asdict(new_card),
                status="new",
                time_created=timestamp(),
                time_latest_review=-1,
                current_review_interval=-1
            )
        cards.append(card)
    return cards


def main():
    print("Simulator")
    scheduler = Scheduler(new_cards_limit=100,
                          total_cards_limit=100,
                          allow_cards_from_same_note=False)

    cards = []
    reviews = []
    max_days = 100

    cards.extend(create_cards(note_id=1, directions=["regular", "reverse"], next_id=0))


    for i in range(max_days):
        num_completed_reviews = len(reviews)
        reviews = scheduler.create_reviews(reviews, cards)

        if num_completed_reviews == len(reviews):
            scheduler.review_time += 86400
            continue

        print(f"Day {i}")
        for review in reviews:
            if review.review_status != "not_reviewed":
                continue
            print(review.card.id)
            # Mark correct
            review.correct = True
            review.time_completed = timestamp()
            review.review_status = "reviewed"

            card = cards[review.card.id]
            card.status = "seen"
            card = scheduler.schedule_card(card, correct=True)
        
        scheduler.review_time += 86400
    return

if __name__ == "__main__":
    main()
