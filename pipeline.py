from agents.collector import collector_agent
from agents.extractor import extractor_agent
from agents.impact import impact_agent
from agents.writer import writer_agent
def dedupe_items(items):
    seen = set()
    out = []
    for it in items:
        key = (it.get("title"), it.get("url"))
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def dedupe_impacts(impacts, max_items=5):
    seen = set()
    unique = []

    for imp in impacts:
        key = (
            imp.get("impact_level"),
            imp.get("score"),
            tuple(imp.get("why", []))
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(imp)

        if len(unique) >= max_items:
            break

    return unique


def run_pipeline(industry):
    # 1️⃣ Collect URLs
    urls = collector_agent(industry)

    # 🔥 DEDUPE + HARD LIMIT
    urls = dedupe_items(urls)[:5]

    # 2️⃣ Safety checks
    if not urls or not isinstance(urls, list):
        raise ValueError("Collector agent returned no URLs")

    first_url = urls[0].get("url")
    if not first_url:
        raise ValueError("No URL found in collector output")

    # 3️⃣ Entity extraction (ONLY ONCE)
    entities = extractor_agent(first_url)

    # 4️⃣ Impact analysis (LIMITED)
    impacts = []

    for u in urls[:3]:  # 🔥 MAX 3 IMPACT CALLS
        item = {
            "title": u.get("title", "Unknown event"),
            "url": u.get("url"),
            "signals": {
                "industry": industry,
                "competitors": entities.get("competitors", []),
                "themes": entities.get("emerging_themes", [])
            },
            "key_points": entities.get("key_points", [])
        }

        context = {
            "industry": industry,
            "focus": "market intelligence"
        }

        impacts.append(impact_agent(item, context))

    # 🔥 REMOVE DUPLICATE IMPACTS
    impacts = dedupe_impacts(impacts, max_items=5)

    # 5️⃣ Final payload (LIMIT SOURCES)
    data = {
        "context": industry,
        "competitors": entities.get("competitors", []),
        "impacts": impacts,
        "sources": list(dict.fromkeys(
            [u.get("url") for u in urls if u.get("url")]
        ))[:4]  # 🔥 MAX 4 SOURCES
    }

    return writer_agent(data)
