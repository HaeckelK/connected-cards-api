import json

from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)

API_URL = "http://127.0.0.1:5000/"

@app.route("/")
def index():
    return redirect(url_for("decks"))


@app.route("/decks")
def decks():
    response = requests.get(API_URL + "decks")
    decks = json.loads(response.content)
    return render_template("decks.html", decks=decks)


@app.route("/create_deck")
def create_deck():
    name = request.args.get("name", None)
    if name:
        response = requests.post(API_URL + "decks", data={"name": name})
        if response.status_code != 200:
            pass
        return redirect(url_for("decks"))
    return render_template("create_deck.html")


@app.route("/deck/<int:id>")
def deck(id: int) -> str:
    response = requests.get(API_URL + f"decks/{id}")
    deck = json.loads(response.content)

    response = requests.get(API_URL + f"notes?deck={id}")
    notes = json.loads(response.content)

    response = requests.get(API_URL + f"reviews?due=1&deck={id}")
    reviews = json.loads(response.content)

    return render_template("deck.html", deck=deck, notes=notes, reviews=reviews)


@app.route("/create_note")
def create_note():
    front = request.args.get("front", None)
    if not front:
        return redirect(request.referrer)
    back = request.args.get("back", None)
    if not front:
        return redirect(request.referrer)
    deck_id = request.args.get("deck", None)
    if not deck_id:
        return redirect(request.referrer)
    response = requests.post(API_URL + "notes", data={"text_front": front, "text_back": back, "deck_id": deck_id})
    if response.status_code != 200:
        pass
    return redirect(request.referrer)


@app.route("/mark_correct/<int:id>")
def mark_correct(id: int) -> str:
    requests.get(f"http://127.0.0.1:5000/reviews/mark_correct/{id}")
    return redirect(url_for("decks"))


@app.route("/mark_incorrect/<int:id>")
def mark_incorrect(id: int) -> str:
    requests.get(f"http://127.0.0.1:5000/reviews/mark_incorrect/{id}")
    return redirect(url_for("decks"))


if __name__ == "__main__":
    app.run(port=5001, debug=True, host="0.0.0.0")
