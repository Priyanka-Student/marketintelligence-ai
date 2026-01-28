from fastapi import FastAPI, HTTPException
from pipeline import run_pipeline
import uuid

app = FastAPI(
    title="Market Intelligence API",
    version="1.0"
)

@app.post("/analyze")
def analyze(req: dict):
    try:
        # 1. Validate input
        industry = req["industry"]

        # 2. Run pipeline
        report = run_pipeline(industry)

        # 3. Return success
        return {
            "report_id": str(uuid.uuid4()),
            "industry": industry,
            "report": report
        }

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
    return {
        "answer": "The top risk is regulatory compliance.",
        "citations": ["https://www.rbi.org.in"]
    }

@app.get("/health")
def health():
    return {"status": "OK"}