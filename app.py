from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from hanzipy.dictionary import HanziDictionary
from hanzipy.exceptions import NotAHanziCharacter
import sqlite3


app = FastAPI()
dictionary = HanziDictionary()
db_conn = sqlite3.connect('marked_words.db')
db_conn.cursor().execute("CREATE TABLE IF NOT EXISTS marked_words(word, time)")
db_conn.commit()

def create_page(word: str):
    return f"""
        <ul>
        {str('\n'.join([ '<li>' + d["definition"] + ' (' + d["pinyin"] + '</li>' for d in dictionary.definition_lookup(word)])) + ')'}
        </ul>
        <br>
        <a href="/mark/{word}">Mark</a>
    """

@app.get("/define/{word}", response_class=HTMLResponse)
def define_word(word: str):
    try:
        return create_page(word)
    except KeyError:
        return "not found"
    except NotAHanziCharacter:
        return "invalid string; not hanzi"

@app.get("/mark/{word}", response_class=HTMLResponse)
def mark_word(word: str):
    print(f"WORD: {word}")
    db_conn = sqlite3.connect('marked_words.db')
    cur = db_conn.cursor()
    cur.execute("INSERT OR IGNORE INTO marked_words VALUES (?, date())", (word,))
    db_conn.commit()
    return "Marked successfully."

@app.get("/list_words", response_class=HTMLResponse)
def list_words():
    db_conn = sqlite3.connect('marked_words.db')
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
