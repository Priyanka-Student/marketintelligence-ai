import requests

def extractor_agent(url):
    # 1. Fetch raw text
    raw_resp = requests.post(
        "http://localhost:8001/tool/fetch_url",
        json={"url": url}
    )
    raw_text = raw_resp.text  # ✅ NOT .json()

    # 2. Clean extracted text
    clean_resp = requests.post(
        "http://localhost:8001/tool/clean_extract",
        json={"raw_text": raw_text}
    )
    clean_text = clean_resp.text  # ✅ NOT .json()

    # 3. Extract entities (THIS returns JSON)
    entities_resp = requests.post(
        "http://localhost:8001/tool/extract_entities",
        json={"text": clean_text}
    )
    entities = entities_resp.json()  # ✅ JSON here is correct

    return entities