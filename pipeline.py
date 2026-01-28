from agents.collector import collector_agent
from agents.extractor import extractor_agent
from agents.impact import impact_agent
from agents.writer import writer_agent

def run_pipeline(industry):
    urls = collector_agent(industry)

    # SAFETY CHECK
    if not urls or not isinstance(urls, list):
        raise ValueError("Collector agent returned no URLs")

    first_url = urls[0].get("url")
    if not first_url:
        raise ValueError("No URL found in collector output")

    entities = extractor_agent(first_url)

    impacts = []
    for u in urls:
        title = u.get("title", "Unknown event")
        impacts.append(impact_agent(title, industry))

    data = {
        "competitors": entities.get("competitors", []),
        "impacts": impacts,
        "sources": [u.get("url") for u in urls if u.get("url")]
    }

    return writer_agent(data)