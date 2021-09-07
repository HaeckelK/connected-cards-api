"""
Temporary testing setup to check that all endpoints acting as expected, before making the shift
from Flask to FastAPI.
"""
import json

import pytest
import requests

from models import DeckOut, NoteOut


FASTAPI_URL = "http://127.0.0.1:8000"


@pytest.fixture
def empty_data():
    requests.get(FASTAPI_URL + "/wipe")
    return


@pytest.fixture
def decks_only():
    requests.get(FASTAPI_URL + "/wipe")
    requests.post(FASTAPI_URL + "/decks", data='{ "name": "French" }')
    requests.post(FASTAPI_URL + "/decks", data='{ "name": "German" }')
    return

# /decks
def test_get_decks_empty(empty_data):
    # Given an empty dataset
    # When GET /decks
    response = requests.get(FASTAPI_URL + "/decks")
    # Then ok status
    assert response.status_code == 200
    # Then empty list returned
    assert json.loads(response.content) == []


def test_get_decks_not_empty(decks_only):
    # Given a dataset which contains multiple decks
    # When GET / decks
    response = requests.get(FASTAPI_URL + "/decks")
    # Then ok status
    assert response.status_code == 200
    # Then length of response is correct
    assert len(json.loads(response.content)) == 2
    # Then each item returned is of type DeckOut
    for item in json.loads(response.content):
        DeckOut(**item)


def test_get_decks_by_id_exists(decks_only):
    # Given a dataset which contains multiple decks
    # When GET a deck id that exists
    response = requests.get(FASTAPI_URL + "/decks/1")
    # Then ok status
    assert response.status_code == 200
    # Then item returned is of type DeckOut
    DeckOut(**json.loads(response.content))


def test_get_decks_by_id_not_exists(decks_only):
    # Given a dataset which contains multiple decks
    # When GET a deck id that does not exist
    response = requests.get(FASTAPI_URL + "/decks/99")
    # Then bad status
    assert response.status_code == 400
    # Then error message received
    assert response.text == "{\"detail\":\"Deck not found for id: 99\"}"


def test_post_decks_empty(empty_data):
    # Given an empty dataset
    # When POST /decks
    response = requests.post(FASTAPI_URL + '/decks', data='{ "name": "French" }')
    # Then ok status
    assert response.status_code == 200
    # Then DeckOut returned
    DeckOut(**json.loads(response.content))


def test_post_decks_empty_duplicate(empty_data):
    # Given a dataset with an existing deck
    requests.post(FASTAPI_URL + '/decks', data='{ "name": "French" }')
    # When adding deck of same name
    response = requests.post(FASTAPI_URL + '/decks', data='{ "name": "French" }')
    # Then ok status
    assert response.status_code == 200
    # Then duplicate deck added
    assert len(json.loads(requests.get(FASTAPI_URL + "/decks").content)) == 2

# /notes
def test_get_notes_empty(empty_data):
    # Given an empty dataset
    # When GET /notes
    response = requests.get(FASTAPI_URL + "/notes")
    # Then ok status
    assert response.status_code == 200
    # Then empty list returned
    assert json.loads(response.content) == []

def test_post_notes_empty(empty_data):
    # Given a dataset with no notes
    # When POST /notes
    response = requests.post(
        FASTAPI_URL + "/notes",
        data='{"text_front": "Hello", "text_back": "Bonjour", "deck_id": 1}',
    )
    # Then ok status
    assert response.status_code == 200
    # Then DeckOut returned
    NoteOut(**json.loads(response.content))


def test_post_notes_empty_duplicate(empty_data):
    # Given a dataset with an existing note
    requests.post(
        FASTAPI_URL + "/notes",
        data='{"text_front": "Hello", "text_back": "Bonjour", "deck_id": 1}',
    )
    # When adding deck of same name
    response = requests.post(
        FASTAPI_URL + "/notes",
        data='{"text_front": "Hello", "text_back": "Bonjour", "deck_id": 1}',
    )
    # Then ok status
    assert response.status_code == 200
    # Then duplicate deck added
    assert len(json.loads(requests.get(FASTAPI_URL + "/notes").content)) == 2

# TODO test note creation leads to card creation

# /cards
# TODO test cards once they exist
def test_get_cards_empty(empty_data):
    # Given an empty dataset
    # When GET /cards
    response = requests.get(FASTAPI_URL + "/cards")
    # Then ok status
    assert response.status_code == 200
    # Then empty list returned
    assert json.loads(response.content) == []
