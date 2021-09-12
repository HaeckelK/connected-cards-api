from typing import List

from database import SessionLocal, engine
import dbmodels
from dbmodels import Deck, Note
from models import DeckOut, NoteOut

dbmodels.Base.metadata.drop_all(bind=engine)
dbmodels.Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import Session
from sqlalchemy import text


def get_notes() -> List[NoteOut]:
    # Notes can currently be fetched directly from db using object
    output = []
    with Session(engine) as session:
        notes = session.query(Note).all()
        for note in notes:
            data = note.__dict__
            data.pop('_sa_instance_state')
            output.append(NoteOut(**data))
    return output


def get_decks() -> List[DeckOut]:
    output = []
    statement = """select
	id,
	name,
	time_created,
	case
		when notes_total is null then 0
		else notes_total
	end as notes_total
from
	decks
left join (
	select
		deck_id, count(*) as notes_total
	from
		notes
	group by
		deck_id) f on
	decks.id = f.deck_id;"""
    conn = engine.connect()
    result = conn.execute(statement, {}).fetchall()
    for item in result:
        deck = DeckOut(id=item[0],
                       name=item[1],
                       notes_total=item[3],
                       cards_total=-1,
                       time_created=item[2],
                       count_reviews_due=-1,
                       count_new_cards=-1)
        output.append(deck)
    return output


with Session(engine) as session:
    # Create some decks
    german_deck = Deck(name="German", time_created=0)
    french_deck = Deck(name="French", time_created=0)
    session.add(german_deck)
    session.add(french_deck)
    session.commit()

    # Create some notes
    bonjour_note = Note(deck_id=french_deck.id,
                text_front="hello",
                text_back="bonjour",
                time_created=0)
    rouge_note = Note(deck_id=french_deck.id,
                text_front="red",
                text_back="rouge",
                time_created=0)
    session.add(bonjour_note)
    session.add(rouge_note)
    session.commit()

    # Queries
    decks_out = get_decks()
    print(decks_out)

    # Load notes from database
    notes_out = get_notes()
    print(notes_out)