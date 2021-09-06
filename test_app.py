"""
Temporary testing setup to check that all endpoints acting as expected, before making the shift
from Flask to FastAPI.
"""
import json

import pytest
import requests

from models import DeckOut


BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture
def clean_data():
    requests.get(BASE_URL + "/wipe")
    return


@pytest.fixture
def some_data():
    requests.get(BASE_URL + "/wipe")
    requests.post(BASE_URL + "/decks", data={"name": "French"})
    requests.post(BASE_URL + "/decks", data={"name": "German"})
    return


def test_get_decks_empty(clean_data):
    # Given an empty dataset
    # When GET /decks
    response = requests.get(BASE_URL + "/decks")
    # Then ok status
    assert response.status_code == 200
    # Then empty list returned
    assert json.loads(response.content) == []


def test_get_decks_not_empty(some_data):
    # Given a dataset which contains a deck
    # When GET / decks
    response = requests.get(BASE_URL + "/decks")
    # Then ok status
    assert response.status_code == 200
    # Then length of response is correct
    assert len(json.loads(response.content)) == 2
    # Then each item returned is of type DeckOut
    for item in json.loads(response.content):
        DeckOut(**item)


def test_post_decks_empty(clean_data):
    # Given an empty dataset
    # When POST /decks
    response = requests.post(BASE_URL + "/decks", data={"name": "French"})
    # Then ok status
    assert response.status_code == 200
    # Then DeckOut returned
    DeckOut(**json.loads(response.content))


def test_post_decks_empty_duplicate(clean_data):
    # Given a dataset with an existing deck
    requests.post(BASE_URL + "/decks", data={"name": "French"})
    # When adding deck of same name
    response = requests.post(BASE_URL + "/decks", data={"name": "French"})
    # Then ok status
    assert response.status_code == 200
    # Then duplicate deck added
    assert len(json.loads(requests.get(BASE_URL + "/decks").content)) == 2
