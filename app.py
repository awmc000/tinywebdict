from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from hanzipy.dictionary import HanziDictionary

app = FastAPI()
dictionary = HanziDictionary()

@app.get("/define/{word}", response_class=HTMLResponse)
def define_word(word: str):
    try:
        return str(';'.join([ d["definition"] for d in dictionary.definition_lookup(word)]))
    except KeyError:
        return "not found"
