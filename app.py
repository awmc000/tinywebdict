"""
Micro dictionary web app, to hook up to Calibre for reading Chinese texts with easy lookup.
Inspired by ads on MDBG which had gross warts and stuff on them.
"""
import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from hanzipy.dictionary import HanziDictionary
from hanzipy.exceptions import NotAHanziCharacter

app = FastAPI()
dictionary = HanziDictionary()

def create_database():
    """Create marked words table, to be called once on startup."""
    db_conn = sqlite3.connect("marked_words.db")
    db_conn.cursor().execute("CREATE TABLE IF NOT EXISTS marked_words(word, time)")
    db_conn.commit()

create_database()

def create_page(word: str):
    """Helper to format a basic HTML page with a word's definitions and pinyin."""
    return f"""
        <ul>
        {str('\n'.join([
            '<li>' + 
            d["definition"] +
            ' (' + d["pinyin"] + ') ' +
            '</li>' 
            for d in dictionary.definition_lookup(word)
        ])) + ')'
        }
        </ul>
        <br>
        <a href="/mark/{word}">Mark</a>
    """


@app.get("/define/{word}", response_class=HTMLResponse)
def define_word(word: str):
    """Word definition endpoint, returns a definition page or error msg page."""
    try:
        return create_page(word)
    except KeyError:
        return "not found"
    except NotAHanziCharacter:
        return "invalid string; not hanzi"


@app.get("/mark/{word}", response_class=HTMLResponse)
def mark_word(word: str):
    """Word marking endpoint, adds word to review list."""
    print(f"WORD: {word}")
    db_conn = sqlite3.connect("marked_words.db")
    cur = db_conn.cursor()
    cur.execute("INSERT OR IGNORE INTO marked_words VALUES (?, date())", (word,))
    db_conn.commit()
    return "Marked successfully."


@app.get("/list_words", response_class=HTMLResponse)
def list_words():
    """Review list access endpoint, returns a formatted table of saved words."""
    db_conn = sqlite3.connect("marked_words.db")
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM marked_words")
    rows = cur.fetchall()
    table_rows = []
    for r in rows:
        word = str(r[0])
        definition = dictionary.definition_lookup(word)[0]
        table_rows.append(f"""
            <tr>
                <td>{word}</td>
                <td>{definition['pinyin']}</td>
                <td>{definition['definition']}</td>
            </tr>
        """)
    table_rows_html = "".join(table_rows)
    return f"""
        <table style="border: 1px solid black; border-collapse: collapse" rules="all">
            <tr><th>hanzi</th><th>pinyin</th><th>definition</th></tr>
            {table_rows_html}
        </table>
    """
