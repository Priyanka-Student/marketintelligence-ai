import requests

def impact_agent(event, industry):
    context = {
        "industry": industry,
        "event_type": "regulatory / market signal"
    }

    response = requests.post(
        "http://localhost:8001/tool/impact_score",
        json={
            "item": event,
            "context": context
        }
    )
    return response.json()
