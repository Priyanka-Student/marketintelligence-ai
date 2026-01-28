import requests

def collector_agent(industry):
    response = requests.post(
        "http://localhost:8001/tool/search_web",
        json={"query": f"{industry} regulatory news"}
    )
    return response.json()