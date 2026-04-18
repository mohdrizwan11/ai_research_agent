"""
api/main.py
-----------
FastAPI server exposing the research pipeline as an HTTP endpoint.

Endpoints:
    GET  /research?topic=...  → run full pipeline
    GET  /cached              → list all cached topics
    GET  /health              → health check

Run:
    uvicorn src.api.main:app --reload
"""

import sys, os
from pathlib import Path

# Add the backend root directory to sys.path
backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

import logging
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.pipeline.research_pipeline import run as run_pipeline
from src.memory.retriever import list_cached_topics

logging.basicConfig(level=logging.INFO)
app = FastAPI(
    title="AI Research Agent",
    description="Autonomous research report generator powered by Groq LLM",
    version="1.0.0",
)

# Add CORS Middleware to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL e.g. ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


from pydantic import BaseModel
from typing import List, Dict, Any
from src.core.llm_client import generate_response

class ResearchRequest(BaseModel):
    topic: str
    mode: str = "concise"
    deep_research: bool = False
    force_refresh: bool = False

class ChatRequest(BaseModel):
    topic: str
    messages: List[Dict[str, str]]

@app.post("/research")
def research(req: ResearchRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    result = run_pipeline(
        req.topic.strip(), 
        force_refresh=req.force_refresh,
        mode=req.mode,
        deep_research=req.deep_research
    )
    return JSONResponse(content=result)

@app.post("/chat")
def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")
        
    system_prompt = f"You are a helpful research assistant. The user is asking follow-up questions about a report on '{req.topic}'. Provide clear, concise answers. Use markdown formatting where appropriate."
    
    try:
        # We need to format the prompt. We'll just pass the entire conversation history.
        # generate_response currently takes a single string prompt. We need to adapt the last message as prompt and the rest as context or adjust generate_response.
        # For simplicity, we'll serialize the history into the prompt text since generate_response is simple.
        history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in req.messages[:-1]])
        current_query = req.messages[-1]["content"]
        
        full_prompt = f"Previous conversation:\n{history_text}\n\nUser Question: {current_query}"
        
        reply = generate_response(
            full_prompt,
            system=system_prompt,
            max_tokens=1000
        )
        return {"reply": reply}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cached")
def cached_topics():
    return {"topics": list_cached_topics()}
