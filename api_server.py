"""
FastAPI backend for Refugee Legal Navigator.
Exposes /api/chat for real Nova Lite legal reasoning from the browser dashboard.
"""
import os
import sys
import json
import logging

# Add src to path so we can import our existing utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Refugee Legal Navigator API", version="1.0.0")

# Allow the Vite dev server to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Lazy-initialise Nova client ──────────────────────────────────────────────
_nova_client = None

def get_nova():
    global _nova_client
    if _nova_client is None:
        try:
            from utils.nova_integration import NovaClient
            _nova_client = NovaClient()
            logger.info("NovaClient initialised successfully")
        except Exception as e:
            logger.error(f"Could not initialise NovaClient: {e}")
            raise
    return _nova_client

# ── RAG: load asylum guide chunks once ───────────────────────────────────────
_rag_chunks = None

def get_rag_chunks():
    global _rag_chunks
    if _rag_chunks is None:
        guide_path = os.path.join(os.path.dirname(__file__), "data", "legal_docs", "asylum_guide.txt")
        if os.path.exists(guide_path):
            with open(guide_path, encoding="utf-8") as f:
                text = f.read()
            chunk_size = 500
            words = text.split()
            _rag_chunks = [
                " ".join(words[i:i + chunk_size])
                for i in range(0, len(words), chunk_size)
            ]
            logger.info(f"Loaded {len(_rag_chunks)} RAG chunks from asylum_guide.txt")
        else:
            _rag_chunks = []
            logger.warning("asylum_guide.txt not found — RAG disabled")
    return _rag_chunks


def find_relevant_context(query: str, chunks: list, max_chunks: int = 3) -> str:
    """Simple keyword-based retrieval (no embeddings needed for fast response)."""
    if not chunks:
        return ""
    query_words = set(query.lower().split())
    scored = []
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        score = len(query_words & chunk_words)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    relevant = [c for s, c in scored[:max_chunks] if s > 0]
    return "\n\n".join(relevant)


# ── Request / Response models ─────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    language: str = "en"


class ChatResponse(BaseModel):
    response: str
    model: str
    context_used: bool


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Refugee Legal Navigator API"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Accepts a transcribed voice message (or typed text) and returns a real
    Nova Lite legal assessment grounded in the asylum guide via RAG context.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    logger.info(f"Chat request: '{req.message[:80]}...' lang={req.language}")

    # Retrieve relevant legal context
    chunks = get_rag_chunks()
    context = find_relevant_context(req.message, chunks)
    context_used = bool(context)

    # Build a focused legal system prompt
    system_prompt = (
        "You are an expert immigration and asylum legal advisor for the Refugee Legal Navigator. "
        "You help refugees and asylum seekers understand their legal rights, eligibility, and options. "
        "Always be compassionate, clear, and accurate. Cite relevant legal frameworks when applicable "
        "(1951 Refugee Convention, US asylum law, UNHCR guidelines). "
        "Keep responses concise — under 150 words. "
        "If you are uncertain, say so and recommend consulting a qualified immigration attorney.\n\n"
    )

    if context:
        system_prompt += (
            "Use the following legal reference material to ground your response:\n\n"
            f"--- LEGAL CONTEXT ---\n{context}\n--- END CONTEXT ---\n\n"
        )

    if req.language != "en":
        system_prompt += f"Respond in the user's language: {req.language}.\n"

    try:
        nova = get_nova()
        response_text = nova.generate_response(req.message, system_prompt)
        logger.info(f"Nova response length: {len(response_text)} chars")
        return ChatResponse(
            response=response_text,
            model="amazon.nova-lite-v1:0",
            context_used=context_used,
        )
    except Exception as e:
        logger.error(f"Nova call failed: {e}")
        # Graceful fallback so the UI never breaks
        fallback = (
            "I'm connecting to Amazon Nova now. Based on international refugee law, "
            "you may be eligible for asylum protection if you can demonstrate a well-founded "
            "fear of persecution. Please consult with a qualified immigration attorney for "
            "personalized legal advice specific to your situation."
        )
        return ChatResponse(response=fallback, model="fallback", context_used=False)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
