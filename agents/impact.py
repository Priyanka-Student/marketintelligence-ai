import requests

def impact_agent(event, industry):
    response = requests.post(
        "http://localhost:8001/tool/impact_score",
        json={"item": event, "context": industry}
    )
    return response.json()