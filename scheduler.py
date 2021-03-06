from typing import List

from utils import timestamp, yesterday_midnight

from models import ReviewOut, CardOut


# TODO allow max number of dispersal group cards
class Scheduler:
    def __init__(self, new_cards_limit: int, total_cards_limit: int, allow_cards_from_same_note: bool,
                 success_increment_factor: float, minimum_review_interval: int=86400) -> None:
        self.new_cards_limit = new_cards_limit
        self.allow_cards_from_same_note = allow_cards_from_same_note
        self.total_cards_limit = total_cards_limit
        self.minimum_review_interval = minimum_review_interval
        self.success_increment_factor =success_increment_factor
        self.review_time = -1
        self.set_review_time()
        return

    def set_review_time(self) -> None:
        """Wrapper function to ease test mocking."""
        self.review_time = yesterday_midnight()
        return

    def create_reviews(self, reviews, cards) -> List[ReviewOut]:
        # TODO should create views by deck

        if not cards:
            return reviews

        try:
            next_review_id = max([x.id for x in reviews]) + 1
        except ValueError:
            next_review_id = 1

        # Remove any incomplete reviews
        reviews = [x for x in reviews if x.review_status != "not_reviewed"]

        pool = []
        # TODO what order? Random? Or Order addded
        new_count = 0
        note_ids = set()
        dispersal_group_ids = set()
        for card in cards:
            print(card)
            # Don't allow cards that are not due
            if (card.time_latest_review + card.current_review_interval) > self.review_time:
                print("Rejected: due time > review time")
                continue

            # Don't allow cards from the same note to be reviewed on same day
            if (card.note_id in note_ids) and (self.allow_cards_from_same_note is False):
                print("Rejected: note id already been seen in pool")
                continue
            
            # Don't allow cards from the same group to be reviewed on same day
            skip = False
            for dispersal_group_id in card.dispersal_groups:
                if dispersal_group_id in dispersal_group_ids:
                    print(f"Rejected: group id {dispersal_group_id} already seen in pool")
                    skip = True
                    break
            if skip:
                continue

            # Limit number of new cards that can be added to pool
            if new_count > self.new_cards_limit:
                print("Rejected: new count > new cards limit")
                continue

            # Limit total number of cards
            if len(pool) >= self.total_cards_limit:
                print("Rejected: pool size greate than total cards limit")
                break

            print("Created")
            # Track number of new cards added to pool
            if card.status == "new":
                new_count += 1

            note_ids.add(card.note_id)
            dispersal_group_ids.update(card.dispersal_groups)
            pool.append(card)

        for i, card in enumerate(pool):
            review = ReviewOut(
                id=i + next_review_id, card=card, time_created=timestamp(), time_completed=-1, review_status="not_reviewed", correct=-1
            )
            review.card = card
            reviews.append(review)
        return reviews

    def schedule_card(self, card: CardOut, correct: bool) -> CardOut:
        card.time_latest_review = self.review_time
        if not correct:
            return card
        if card.current_review_interval == -1:
            card.current_review_interval = self.minimum_review_interval
        else:
            card.current_review_interval *= self.success_increment_factor
        return card
