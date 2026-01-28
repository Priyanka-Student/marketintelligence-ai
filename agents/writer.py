import requests

def writer_agent(data):
    response = requests.post(
        "http://localhost:8001/tool/generate_market_report",
        json={"data": data}
    )
    return response.json()