"""
FastAPI application — serves the API and the glassmorphism web UI.
"""

from dotenv import load_dotenv
load_dotenv()  # load .env before any module reads os.getenv

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pathlib

from app.router import handle_message

app = FastAPI(
    title="Prompt Router",
    version="1.0.0",
    description="AI-powered intent classification and expert routing service",
)


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={}, status_code=204)

# Serve static assets (CSS / JS)
STATIC_DIR = pathlib.Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    intent: str
    confidence: float
    response: str


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Classify intent, route to expert, return response."""
    message = req.message.strip()
    if not message:
        return JSONResponse(
            content={"intent": "unclear", "confidence": 0.0, "response": "Please enter a message."},
        )
    result = await handle_message(message)
    return JSONResponse(content=result)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Serve the UI
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = pathlib.Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
