from trafilatura import fetch_url as tf_fetch, extract

def log(msg):
    with open("logs/execution.log", "a") as f:
        f.write(msg + "\n")

def search_web(query):
    log("[MCP] search_web called")
    return [{
        "title": f"{query} regulatory update",
        "url": "https://www.rbi.org.in"
    }]

def fetch_url(url):
    log("[MCP] fetch_url called")
    downloaded = tf_fetch(url)

    if not downloaded:
        return ""

    return extract(downloaded) or ""

def clean_extract(raw_text):
    log("[MCP] clean_extract called")
    return raw_text[:2000] if raw_text else ""

def extract_entities(text):
    log("[MCP] extract_entities called")
    return {
        "competitors": ["Company A", "Company B"],
        "themes": ["Regulatory Change", "Digital Lending"]
    }

def impact_score(item, context):
    log("[MCP] impact_score called")
    return {
        "event": item,
        "impact_level": "High",
        "score": 85,
        "why": [
            "Direct regulatory compliance required",
            "Operational changes needed"
        ],
        "actions": [
            "Audit compliance",
            "Update internal processes"
        ]
    }

def generate_market_report(data):
    log("[MCP] generate_market_report called")
    return {
        "summary": "Industry is undergoing regulatory-driven changes.",
        "drivers": ["Policy updates", "Digital adoption"],
        "competitors": data.get("competitors", []),
        "impact_radar": data.get("impacts", []),
        "opportunities": ["Fintech partnerships"] * 5,
        "risks": ["Compliance cost increase"] * 5,
        "90_day_plan": {
            "0_30": ["Gap analysis"],
            "30_60": ["Policy updates"],
            "60_90": ["Automation"]
        },
        "sources": data.get("sources", [])
    }