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
        for card in cards:
            if card.status == "new":
                new_count += 1
            if new_count > self.new_cards_limit:
                continue
            pool.append(card)

        for i, card in enumerate(pool):
            review = ReviewOut(
                id=i + 1, card=card, time_created=timestamp(), time_completed=-1, review_status="not_reviewed", correct=-1
            )
            reviews.append(review)
        return reviews
