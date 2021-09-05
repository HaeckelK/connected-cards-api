from typing import List

from utils import timestamp

from models import ReviewOut


class Scheduler:
    def __init__(self) -> None:
        return

    def create_reviews(self, reviews, cards) -> List[ReviewOut]:
        # TODO should create views by deck
        reviews = []
        for i, card in enumerate(cards):
            review = ReviewOut(
                id=i + 1, card=card, time_created=timestamp(), time_completed=-1, review_status="not_reviewed", correct=-1
            )
            reviews.append(review)
        return reviews
