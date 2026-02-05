from fastapi import FastAPI, HTTPException
from pipeline import run_pipeline
import uuid
from mcp_server.llm import ollama_generate
from fastapi.middleware.cors import CORSMiddleware



REPORT_STORE = {}


app = FastAPI(
    title="Market Intelligence API",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all frontends (OK for prototype)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/analyze")
def analyze(req: dict):
    try:
        industry = req["industry"]

        report = run_pipeline(industry)

        report_id = str(uuid.uuid4())

        # 🔥 STORE REPORT FOR CHAT
        REPORT_STORE[report_id] = report

        return {
            "report_id": report_id,
            "industry": industry,
            "report": report
        }

    except KeyError:
        raise HTTPException(status_code=400, detail="Request must contain 'industry'")

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


    except KeyError:
        # Missing field in request
        raise HTTPException(
            status_code=400,
            detail="Request must contain 'industry'"
        )

    except ValueError as ve:
        # Controlled pipeline failure
        raise HTTPException(
            status_code=422,
            detail=str(ve)
        )

    except Exception as e:
        # Unexpected crash
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}"
        )

@app.post("/chat")
def chat(req: dict):
    report_id = req.get("report_id")
    question = req.get("question")

    if not report_id or not question:
        raise HTTPException(status_code=400, detail="report_id and question required")

    if report_id not in REPORT_STORE:
        raise HTTPException(status_code=404, detail="Report not found")

    report = REPORT_STORE[report_id]

    prompt = f"""
Answer the question using ONLY the report below.

REPORT:
{report}

QUESTION:
{question}
"""

    answer = ollama_generate(prompt)

    return {
        "answer": answer,
        "citations": report.get("sources", [])
    }

@app.get("/health")
def health():
    return {"status": "OK"}