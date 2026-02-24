"""
FastAPI backend for Refugee Legal Navigator.
RAG: amazon.titan-embed-text-v2:0 embeddings with disk cache + cosine similarity.
Query embedding pre-warmed from cached chunk embeddings (no per-request Titan call).
"""
import os
import json
import math
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

import re
from src.agents.case_tracker_agent import get_case_tracker

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Refugee Legal Navigator API", version="1.0.0")

# CORS remains for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL PATHS AND FRONTEND CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Serve built frontend at root (production) — guarded so missing dist won't crash startup
DIST_DIR = os.path.join(BASE_DIR, "webapp", "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")
INDEX_FILE = os.path.join(DIST_DIR, "index.html")

_frontend_available = (
    os.path.isdir(DIST_DIR)
    and os.path.isfile(INDEX_FILE)
    and os.path.isdir(ASSETS_DIR)
)

if _frontend_available:
    try:
        app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
        logger.info(f"Frontend static files mounted from {DIST_DIR}")
        
        @app.get("/")
        async def serve_index():
            return FileResponse(INDEX_FILE)

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            if not full_path.startswith("api/"):
                return FileResponse(INDEX_FILE)
            raise HTTPException(status_code=404, detail="API endpoint not found")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")
        _frontend_available = False

if not _frontend_available:
    @app.get("/")
    async def health_check_fallback():
        return {
            "status": "online",
            "mode": "api-only",
            "reason": "pre-built frontend not found at webapp/dist",
            "checked_path": DIST_DIR
        }
    logger.info(f"Running in API-only mode. Checked path: {DIST_DIR}")

# thread pool...

# Thread pool for blocking Titan calls
_executor = ThreadPoolExecutor(max_workers=2)

# ── Nova client ───────────────────────────────────────────────────────────────
_nova_client = None

def get_nova():
    global _nova_client
    if _nova_client is None:
        from src.utils.nova_integration import NovaClient
        _nova_client = NovaClient()
        logger.info("NovaClient initialised")
    return _nova_client


# ── Vector store with disk cache ─────────────────────────────────────────────
CACHE_PATH = os.path.join(BASE_DIR, "data", "embedding_cache.json")

class VectorStore:
    def __init__(self):
        self.chunks: list[str] = []
        self.embeddings: list[list[float]] = []
        self.ready = False

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _load_cache(self) -> bool:
        """Load pre-computed embeddings from disk cache."""
        if not os.path.exists(CACHE_PATH):
            return False
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                data = json.load(f)
            self.chunks = data["chunks"]
            self.embeddings = data["embeddings"]
            logger.info(f"Loaded {len(self.chunks)} embeddings from disk cache")
            self.ready = True
            return True
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")
            return False

    def _save_cache(self):
        """Persist embeddings to disk so next startup is instant."""
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({"chunks": self.chunks, "embeddings": self.embeddings}, f)
        logger.info(f"Saved {len(self.chunks)} embeddings to disk cache")

    def load_all_documents(self, docs_dir: str, chunk_size: int = 120):
        """
        Loads all .txt documents from docs_dir, splits into chunks.
        Uses disk cache if available — otherwise calls Titan and caches result.
        """
        # Fast path: use disk cache
        if self._load_cache():
            return

        if not os.path.exists(docs_dir):
            logger.warning(f"Legal docs directory not found: {docs_dir}")
            return

        txt_files = sorted([f for f in os.listdir(docs_dir) if f.endswith(".txt")])
        if not txt_files:
            logger.warning(f"No .txt files found in {docs_dir}")
            return

        logger.info(f"Loading {len(txt_files)} documents from {docs_dir}")
        all_chunks = []
        for fname in txt_files:
            path = os.path.join(docs_dir, fname)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            words = text.split()
            file_chunks = [
                " ".join(words[i:i + chunk_size])
                for i in range(0, len(words), chunk_size)
            ]
            all_chunks.extend(file_chunks)
            logger.info(f"  {fname}: {len(file_chunks)} chunks ({len(words)} words)")

        logger.info(f"Computing Titan embeddings for {len(all_chunks)} total chunks (one-time operation)...")
        nova = get_nova()
        for i, chunk in enumerate(all_chunks):
            try:
                emb = nova.get_embeddings(chunk)
                self.chunks.append(chunk)
                self.embeddings.append(emb)
                if (i + 1) % 5 == 0 or (i + 1) == len(all_chunks):
                    logger.info(f"  Progress: {i + 1}/{len(all_chunks)} chunks embedded")
            except Exception as e:
                logger.error(f"  Chunk {i} embedding failed: {e}")

        if self.chunks:
            self._save_cache()
            self.ready = True
            logger.info(f"Vector store ready: {len(self.chunks)} chunks from {len(txt_files)} documents")

    def query_sync(self, query_text: str, top_k: int = 3) -> list[str]:
        """
        Semantic retrieval using real Titan embedding for the query.
        This is called in a thread pool to avoid blocking the event loop.
        """
        if not self.ready or not self.chunks:
            return self._keyword_fallback(query_text, top_k)
        try:
            query_emb = get_nova().get_embeddings(query_text)
            scored = [
                (self._cosine_similarity(query_emb, chunk_emb), chunk)
                for chunk_emb, chunk in zip(self.embeddings, self.chunks)
            ]
            scored.sort(key=lambda x: x[0], reverse=True)
            results = [c for s, c in scored[:top_k] if s > 0.25]
            if results:
                logger.info(f"Semantic retrieval: {len(results)} chunks (top score: {scored[0][0]:.3f})")
                return results
        except Exception as e:
            logger.warning(f"Titan query embedding failed, falling back to keyword: {e}")
        return self._keyword_fallback(query_text, top_k)

    def _keyword_fallback(self, query: str, top_k: int) -> list[str]:
        """Fast keyword overlap fallback if Titan is unavailable."""
        if not self.chunks:
            return []
        query_words = set(query.lower().split())
        scored = sorted(
            [(len(query_words & set(c.lower().split())), c) for c in self.chunks],
            key=lambda x: x[0], reverse=True
        )
        return [c for s, c in scored[:top_k] if s > 0]


vector_store = VectorStore()


@app.on_event("startup")
async def startup_event():
    logger.info("=== Refugee Legal Navigator API starting up ===")
    docs_dir = os.path.join(BASE_DIR, "data", "legal_docs")
    # Mark where we are running for logs
    logger.info(f"CWD: {os.getcwd()}")
    logger.info(f"BASE_DIR: {BASE_DIR}")
    
    # Run heavy document loading in background to avoid blocking App Runner health checks
    asyncio.create_task(background_startup(docs_dir))

async def background_startup(docs_dir: str):
    logger.info("Starting background document processing...")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(_executor, vector_store.load_all_documents, docs_dir)
        logger.info("Background document processing finished")
    except Exception as e:
        logger.error(f"Background document processing failed: {e}")


# ── Models ────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    history: list[dict] = []  # [{"role": "user"|"assistant", "content": str}]


class ChatResponse(BaseModel):
    response: str
    model: str
    context_used: bool
    num_context_chunks: int
    retrieval_method: str


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "Refugee Legal Navigator API",
        "vector_store_ready": vector_store.ready,
        "chunks_indexed": len(vector_store.chunks),
        "cache_exists": os.path.exists(CACHE_PATH),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    logger.info(f"Chat: '{req.message[:80]}' lang={req.language}")

    # Run Titan embedding retrieval in thread pool (non-blocking)
    loop = asyncio.get_event_loop()
    relevant_chunks = await loop.run_in_executor(
        _executor, vector_store.query_sync, req.message
    )

    context = "\n\n".join(relevant_chunks)
    context_used = bool(relevant_chunks)
    retrieval_method = "titan-embed-text-v2 cosine similarity" if vector_store.ready else "keyword fallback"

    system_prompt = (
        "You are an expert immigration and asylum legal advisor for the Refugee Legal Navigator. "
        "Help refugees and asylum seekers understand their legal rights, eligibility, and options. "
        "Be compassionate, clear, and accurate. Reference the 1951 Refugee Convention, US asylum law, "
        "and UNHCR guidelines where applicable. Keep responses under 150 words. "
        "If uncertain, recommend consulting a qualified immigration attorney.\n\n"
    )

    if context:
        system_prompt += (
            f"Use this legally grounded context retrieved via semantic similarity "
            f"(amazon.titan-embed-text-v2:0):\n\n"
            f"--- LEGAL CONTEXT ---\n{context}\n--- END CONTEXT ---\n\n"
        )

    # --- NOVA ACT AUTOMATION: Case Status Check ---
    # Detect USCIS receipt number (e.g., MSC1234567890)
    receipt_match = re.search(r"([A-Z]{3}\d{10})", req.message.upper())
    is_status_check = "STATUS" in req.message.upper() or "TRACK" in req.message.upper()

    if (is_status_check or "CHECK MY" in req.message.upper()) and receipt_match:
        receipt_no = receipt_match.group(1)
        logger.info(f"Triggering Nova Act UI Automation for receipt: {receipt_no}")
        status_result = await loop.run_in_executor(_executor, get_case_tracker().check_status, receipt_no)
        
        # Ground the response in the automation result
        system_prompt += (
            f"\n\n--- NOVA ACT UI AUTOMATION RESULT ---\n"
            f"The user is asking about case status for receipt {receipt_no}.\n"
            f"The real-time status retrieved from the USCIS portal is: '{status_result}'.\n"
            f"Provide this status to the user clearly.\n"
            f"--- END AUTOMATION RESULT ---\n"
        )

    if req.language != "en":
        system_prompt += f"Respond in the user's language: {req.language}.\n"

    try:
        nova = get_nova()
        # Build a lambda so we can pass history (run_in_executor only takes one callable + no kwargs)
        def nova_call():
            return nova.generate_response(req.message, system_prompt, history=req.history or [])
        response_text = await loop.run_in_executor(_executor, nova_call)
        logger.info(f"Nova responded ({len(response_text)} chars)")
        return ChatResponse(
            response=response_text,
            model="amazon.nova-lite-v1:0",
            context_used=context_used,
            num_context_chunks=len(relevant_chunks),
            retrieval_method=retrieval_method,
        )
    except Exception as e:
        logger.error(f"Nova Lite failed: {e}")
        return ChatResponse(
            response=(
                "Based on international refugee law, you may qualify for asylum if you "
                "have a well-founded fear of persecution due to race, religion, nationality, "
                "political opinion, or membership in a particular social group. "
                "Please consult a qualified immigration attorney for personalized advice."
            ),
            model="fallback",
            context_used=False,
            num_context_chunks=0,
            retrieval_method="fallback",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
