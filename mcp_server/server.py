from fastapi import FastAPI
from mcp_server.tools import *

app = FastAPI()

@app.post("/tool/search_web")
def search(payload: dict):
    return search_web(payload["query"])

@app.post("/tool/fetch_url")
def fetch(payload: dict):
    return fetch_url(payload["url"])

@app.post("/tool/clean_extract")
def clean(payload: dict):
    return clean_extract(payload["raw_text"])

@app.post("/tool/extract_entities")
def entities(payload: dict):
    return extract_entities(payload["text"])

@app.post("/tool/impact_score")
def impact(payload: dict):
    return impact_score(payload["item"], payload["context"])

@app.post("/tool/generate_market_report")
def report(payload: dict):
    return generate_market_report(payload["data"])