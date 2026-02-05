import subprocess
import json

MODEL = "qwen2.5:1.5b"

def ollama_generate(prompt: str, temperature: float = 0.2) -> str:
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return result.stdout.strip()

def safe_json(text, fallback):
    try:
        return json.loads(text)
    except Exception:
        return fallback
