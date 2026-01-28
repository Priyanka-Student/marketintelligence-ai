# Market Intelligence Agentic AI System

## Overview

This project is an **Agentic AI-based Market Intelligence System** built using a
multi-agent architecture and a separate **MCP (Model Context Protocol) Tool Server**.

The system analyzes a given industry (e.g., NBFC) and generates a **structured market
intelligence report** covering:

* Market summary
* Key drivers
* Competitors
* Impact analysis
* Risks & opportunities
* 90-day action plan
* Sources

The architecture strictly follows **agent-tool separation**, as required in the assignment.

---

## High-Level Architecture

Client → API Server → Pipeline → Agents → MCP Tool Server → Data → Final Report

### Key Principle

* **Agents only decide**
* **MCP tools do the actual work**
* Agents NEVER scrape, extract, or compute directly

---

## Project Structure

```
marketintelligence-ai/
│
├── api/
│   └── main.py              # Public API layer
│
├── agents/
│   ├── collector.py         # Finds relevant sources
│   ├── extractor.py         # Extracts entities
│   ├── impact.py            # Scores impact
│   └── writer.py            # Builds final report
│
├── mcp_server/
│   ├── server.py            # MCP FastAPI server
│   └── tools.py             # Actual tool logic
│
├── logs/
│   └── execution.log        # Tool invocation logs
│
├── pipeline.py              # Orchestrates agent flow
├── requirements.txt
└── README.md
```

---

## Tech Stack

* **Python**
* **FastAPI** – REST API & Swagger UI
* **Ollama** – Local LLM runtime (Mistral / Qwen)
* **Requests** – Inter-service communication
* **Trafilatura** – Web content extraction
* **Agent-based orchestration**

---

## How to Run the Project

### 1. Start MCP Tool Server

```bash
uvicorn mcp_server.server:app --port 8001
```

Swagger:
[http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

---

### 2. Start API Server

```bash
uvicorn api.main:app --port 8000
```

Swagger:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Sample API Request

```json
{
  "industry": "NBFC"
}
```

---

## Output

The API returns a structured JSON market intelligence report including:

* Summary
* Drivers
* Competitors
* Impact radar
* Risks & opportunities
* 90-day action plan
* Sources

---

## Logging

All MCP tool calls are logged in:

```
logs/execution.log
```

This proves correct agent–tool separation.

---

## Assignment Compliance Checklist

* ✔ Multi-agent workflow
* ✔ MCP tool separation
* ✔ API-driven orchestration
* ✔ Structured JSON output
* ✔ Open-source LLM usage
* ✔ Logs for evaluation

---

## Conclusion

This project demonstrates a **production-style agentic AI system** rather than a
single-script solution and fully satisfies the assignment requirements.
