import requests

def collector_agent(industry: str):
    """
    Collector Agent:
    - Builds multiple search queries for an industry
    - Calls MCP search_web tool
    - Aggregates and deduplicates results
    - Ensures pipeline never breaks
    """

    queries = [
        f"{industry} industry news",
        f"{industry} regulatory updates",
        f"{industry} market trends",
        f"{industry} latest developments"
    ]

    collected = []

    for q in queries:
        try:
            response = requests.post(
                "http://localhost:8001/tool/search_web",
                json={"query": q},
                timeout=20
            )

            results = response.json()
            if isinstance(results, list):
                collected.extend(results)

        except Exception:
            # Ignore failed query and continue
            continue

    # Deduplicate by URL
    seen = set()
    unique_results = []
    for item in collected:
        url = item.get("url")
        if url and url not in seen:
            seen.add(url)
            unique_results.append(item)

    # 🔥 FINAL SAFETY FALLBACK
    if not unique_results:
        unique_results = [{
            "title": f"{industry} industry overview",
            "url": f"https://en.wikipedia.org/wiki/{industry.replace(' ', '_')}"
        }]

    return unique_results
