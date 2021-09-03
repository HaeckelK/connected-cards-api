import json

import requests

from app import DeckOut, NoteOut


def main():
    base_url = "http://localhost:5000/"

    # Create a deck
    print("Create Deck")
    response = requests.post(base_url + "decks", data={"name": "French"})
    deck = DeckOut(**json.loads(response.content))
    print(deck)

    # Create a new note
    print("Create Note")
    response = requests.post(
        base_url + "notes",
        data={"text_front": "Hello", "text_back": "Bonjour", "deck_id": deck.id},
    )
    note = NoteOut(**json.loads(response.content))
    print(note)

    # Trigger Review Generation
    print("Triggering Review Generation")
    response = requests.get(base_url + "generate_reviews")
    print(response.text)

    return


if __name__ == "__main__":
    main()
