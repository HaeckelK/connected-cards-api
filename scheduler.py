from typing import List

from utils import timestamp

from models import ReviewOut


class Scheduler:
    def __init__(self, new_cards_limit: int) -> None:
        self.new_cards_limit = new_cards_limit
        return

    def create_reviews(self, reviews, cards) -> List[ReviewOut]:
        # TODO should create views by deck
        reviews = []

        pool = []
        # TODO what order? Random? Or Order addded
        new_count = 0
        note_ids = set()
        for card in cards:
            # Don't allow cards from the same note to be reviewed on same day
            # TODO add boolean flag
            if card.note_id in note_ids:
                continue

            # Track number of new cards added to pool
            if card.status == "new":
                new_count += 1
            
            # Limit number of new cards that can be added to pool
            if new_count > self.new_cards_limit:
                continue

            note_ids.add(card.note_id)
            pool.append(card)

        for i, card in enumerate(pool):
            review = ReviewOut(
                id=i + 1, card=card, time_created=timestamp(), time_completed=-1, review_status="not_reviewed", correct=-1
            )
            reviews.append(review)
        return reviews
