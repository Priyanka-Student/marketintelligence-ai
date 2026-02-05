import json
import subprocess
from trafilatura import fetch_url as tf_fetch, extract
import requests
from bs4 import BeautifulSoup
from typing import Any, Dict
import re

DEFAULT_MODEL = "qwen2.5:1.5b"


# -----------------------------
# Utility: Logging
# -----------------------------
def log(msg):
    with open("logs/execution.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# -----------------------------
# Utility: Ollama LLM call
# -----------------------------
MODEL = "qwen2.5:1.5b"

def ollama_generate(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="ignore",
            timeout=120
        )

        output = result.stdout.strip()

        if not output:
            log("[LLM] Empty output from Ollama")
            return ""

        return output

    except Exception as e:
        log(f"[LLM] Ollama failed: {str(e)}")
        return ""

def safe_json(text, fallback):
    try:
        return json.loads(text)
    except Exception:
        return fallback

# -----------------------------
# MCP TOOLS
# -----------------------------

def search_web(query):
    log(f"[MCP] search_web called | query={query}")

    results = []

    # ---------------------------
    # 1️⃣ DuckDuckGo
    # ---------------------------
    try:
        url = "https://duckduckgo.com/html/"
        r = requests.post(
            url,
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a.result__a")[:5]:
            title = a.get_text(strip=True)
            link = a.get("href")
            if title and link:
                results.append({"title": title, "url": link})
    except Exception as e:
        log(f"[MCP] DuckDuckGo failed: {e}")

    if results:
        return results

    # ---------------------------
    # 2️⃣ Bing (HTML)
    # ---------------------------
    try:
        log("[MCP] Falling back to Bing")
        url = f"https://www.bing.com/search?q={query}"
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        soup = BeautifulSoup(r.text, "html.parser")
        for li in soup.select("li.b_algo h2 a")[:5]:
            title = li.get_text(strip=True)
            link = li.get("href")
            if title and link:
                results.append({"title": title, "url": link})
    except Exception as e:
        log(f"[MCP] Bing failed: {e}")

    if results:
        return results

    # ---------------------------
    # 3️⃣ Google News RSS
    # ---------------------------
    try:
        log("[MCP] Falling back to Google News RSS")
        rss_url = f"https://news.google.com/rss/search?q={query}"
        r = requests.get(rss_url, timeout=20)
        soup = BeautifulSoup(r.text, "xml")

        for item in soup.find_all("item")[:5]:
            title = item.title.text
            link = item.link.text
            results.append({"title": title, "url": link})
    except Exception as e:
        log(f"[MCP] Google News RSS failed: {e}")

    if results:
        return results

    # ---------------------------
    # 4️⃣ FINAL HARD FALLBACK (Industry News Sites)
    # ---------------------------
    log("[MCP] Final fallback: industry portals")

    return [
        {
            "title": f"{query} industry analysis",
            "url": f"https://www.reuters.com/search/news?blob={query.replace(' ', '%20')}"
        },
        {
            "title": f"{query} market trends",
            "url": f"https://www.bloomberg.com/search?query={query.replace(' ', '%20')}"
        }
    ]


def fetch_url(url):
    log("[MCP] fetch_url called")
    downloaded = tf_fetch(url)
    if not downloaded:
        return ""
    return extract(downloaded) or ""

def clean_extract(raw_text):
    log("[MCP] clean_extract called")

    extracted = extract(
        raw_text,
        include_comments=False,
        include_tables=False
    )
    if extracted and len(extracted.strip()) > 200:
        return extracted.strip()

    text = BeautifulSoup(raw_text, "html.parser").get_text("\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:3000]


# -----------------------------
# 🔥 DYNAMIC ENTITY EXTRACTION (LLM-BASED)
# -----------------------------
def extract_entities(text: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    log("[MCP] extract_entities called")

    prompt = f"""
You are an API.
You MUST return VALID JSON ONLY.
NO explanations.
NO markdown.
NO extra text.

You are an information extraction agent.

Extract structured entities from the text below.

Return EXACT JSON with keys:
{{
  "competitors": [],
  "pricing_models": [],
  "emerging_themes": [],
  "key_points": []
}}

Rules:
- competitors: company names only
- pricing_models: subscription, freemium, licensing, etc (if found)
- emerging_themes: industry or technology trends
- key_points: max 5 concise bullets

TEXT:
{text[:3000]}
"""

    out = out = ollama_generate(prompt)


    try:
        if not out.strip():
            log("[MCP] extract_entities empty output")
            raise ValueError("Empty model output")


        parsed = json.loads(out)

        # 🛡️ Minimal validation + defaults
        parsed.setdefault("competitors", [])
        parsed.setdefault("pricing_models", [])
        parsed.setdefault("emerging_themes", [])
        parsed.setdefault("key_points", [])

        return parsed

    except Exception as e:
        log(f"[MCP] extract_entities JSON parse failed: {str(e)}")
        return {
            "competitors": [],
            "pricing_models": [],
            "emerging_themes": [],
            "key_points": []
        }
# -----------------------------
# 🔥 DYNAMIC IMPACT SCORING (LLM-BASED)
# -----------------------------


def impact_score(
    item: Dict[str, Any],
    context: Dict[str, Any],
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:

    log("[MCP] impact_score called")

    prompt = f"""
You are an API.
You MUST return VALID JSON ONLY.
NO explanations.
NO markdown.
NO extra text.

You are an Impact Analysis agent for market intelligence.

Industry: {context.get("industry")}
Focus: {context.get("focus", "general")}
Date range: {context.get("from")} to {context.get("to")}

Evaluate the EVENT below and assign:
- impact_level: High | Medium | Low
- score: integer 0-100
- why: 2-4 concise bullet points
- actions: 2-4 clear actionable steps

Return EXACT JSON in this format:
{{
  "impact_level": "High | Medium | Low",
  "score": 0,
  "why": ["reason 1", "reason 2"],
  "actions": ["action 1", "action 2"]
}}

EVENT:
Title: {item.get("title")}
URL: {item.get("url")}
Signals: {json.dumps(item.get("signals", {}), ensure_ascii=False)}
Key points: {json.dumps(item.get("key_points", []), ensure_ascii=False)}
"""

    out = out = ollama_generate(prompt)


    try:
        if not out.strip():
            log("[MCP] impact_score empty output")
            raise ValueError("Empty model output")
        parsed = json.loads(out)

        # 🛡️ Minimal validation
        if not isinstance(parsed, dict):
            raise ValueError("Not a JSON object")

        parsed.setdefault("impact_level", "Medium")
        parsed.setdefault("score", 50)
        parsed.setdefault("why", [])
        parsed.setdefault("actions", [])

        return parsed

    except Exception as e:
        log(f"[MCP] impact_score JSON parse failed: {str(e)}")

        return {
            "impact_level": "Medium",
            "score": 50,
            "why": [
                "Impact could not be reliably parsed from model output"
            ],
            "actions": [
                "Manually review this event",
                "Re-run analysis with more context"
            ]
        }
# -----------------------------
# 🔥 DYNAMIC REPORT GENERATION (LLM-BASED)
# -----------------------------
from typing import Dict, Any
import json

def generate_market_report(data: Dict[str, Any], model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    log("[MCP] generate_market_report called")

    # ---------------------------
    # 1️⃣ Filter REAL sources only
    # ---------------------------
    real_sources = []
    for source in data.get("sources", []):
        if source and not any(
            fake in source.lower()
            for fake in [
                "regulatory.gov",
                "privacy.gov",
                "aml.gov",
                "cryptocurrency.gov",
                "fintechregulation.gov",
                "crossborderregulation.gov"
            ]
        ):
            real_sources.append(source)

    # ---------------------------
    # 2️⃣ STRICT JSON prompt
    # ---------------------------
    prompt = f"""
You are an API.
You MUST return VALID JSON ONLY.
NO explanations.
NO markdown.
NO comments.

Return JSON EXACTLY matching this schema:

{{
  "summary": "string",
  "drivers": ["string"],
  "competitors": ["string"],
  "impact_radar": [
    {{
      "event": "string",
      "impact_level": "High|Medium|Low",
      "score": 0,
      "why": ["string"],
      "actions": ["string"],
      "url": "string"
    }}
  ],
  "opportunities": ["string"],
  "risks": ["string"],
  "90_day_plan": {{
    "0_30": ["string"],
    "30_60": ["string"],
    "60_90": ["string"]
  }},
  "sources": ["string"]
}}

Rules:
- - impact_radar: 3–5 items
- opportunities: 3–5 items
- risks: 3–5 items

- drivers 3–7 items
- competitors 5–10 unique names
- ONLY use URLs from REAL SOURCES list
- If no valid URL exists, use empty string

REAL SOURCES:
{real_sources}

INPUT DATA:
{json.dumps(data, ensure_ascii=False)[:14000]}
"""

    out = out = ollama_generate(prompt)

    # ---------------------------
    # 3️⃣ Safe JSON parse
    # ---------------------------
    try:
        report = json.loads(out)
    except Exception:
        log("[MCP] generate_market_report JSON parse failed")
        report = {}

    # ---------------------------
    # 4️⃣ Post-clean enforcement
    # ---------------------------
    if not isinstance(report, dict):
        report = {}

    report.setdefault("sources", real_sources)
    report["sources"] = real_sources

    if "impact_radar" in report:
        for item in report["impact_radar"]:
            if item.get("url") not in real_sources:
                item["url"] = ""

    # ---------------------------
    # 5️⃣ HARD fallback (never empty)
    # ---------------------------
    required_keys = ["summary", "drivers", "impact_radar"]
    if any(k not in report for k in required_keys):
        log("[MCP] generate_market_report fallback used")
        return {
            "summary": f"{data.get('context', 'Industry')} market analysis",
            "drivers": ["Regulation", "Technology adoption", "Market competition"],
            "competitors": data.get("competitors", []),
            "impact_radar": data.get("impacts", []),
            "opportunities": ["Market expansion", "Digital transformation"] * 3,
            "risks": ["Regulatory pressure", "Cost increase"] * 3,
            "90_day_plan": {
                "0_30": ["Assess market"],
                "30_60": ["Optimize operations"],
                "60_90": ["Scale initiatives"]
            },
            "sources": real_sources
        }

    return report
