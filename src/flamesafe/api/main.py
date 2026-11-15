"""Single-worker private API. The Node server holds the backend token."""

import hmac
import os
import threading
from collections import deque
from contextlib import asynccontextmanager
from time import monotonic

from fastapi import Depends, FastAPI, Header, HTTPException

from flamesafe.rag.schemas import AnswerResult, ChatRequest, ToolRequest
from flamesafe.rag.service import RagService
from flamesafe.rag.settings import settings as load_settings


def create_app(settings=None, service=None, token=None):
    settings = settings or load_settings()
    token = token if token is not None else os.getenv("FLAMESAFE_API_TOKEN", "")
    recent, lock, slots = deque(), threading.Lock(), threading.BoundedSemaphore(2)

    @asynccontextmanager
    async def lifespan(app):
        app.state.service = service
        if service is None:
            try:
                app.state.service = RagService(settings)
            except (OSError, ValueError, ImportError):
                app.state.service = None
        yield

    app = FastAPI(
        title="FlameSafe evidence API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    def authorize(authorization: str = Header(default="")):
        if not token or not hmac.compare_digest(authorization, "Bearer " + token):
            raise HTTPException(401, "Backend authorization required")

    def ready():
        instance = getattr(app.state, "service", None)
        if instance is None:
            raise HTTPException(503, "Build and validate an evidence snapshot first")
        return instance

    @app.get("/health/live")
    def live():
        return {"status": "live"}

    @app.get("/health/ready")
    def health():
        ready()
        return {"status": "ready"}

    private = [Depends(authorize)]

    @app.get("/v1/status", dependencies=private)
    def status():
        s = ready()
        return {
            "build_id": s.manifest.build_id,
            "source_mode": s.manifest.source_mode,
            "retrieval_mode": s.manifest.retrieval_mode,
            "row_counts": s.manifest.row_counts,
            "generation_enabled": settings.generation_enabled,
            "model_readings_enabled": False,
        }

    @app.get("/v1/investigations", dependencies=private)
    def investigations():
        return ready().tools.execute(ToolRequest(tool="find_investigations"))

    @app.get("/v1/investigations/{psi_id}", dependencies=private)
    def investigation(psi_id: str):
        return ready().tools.execute(
            ToolRequest(tool="get_investigation", arguments={"psi_id": psi_id})
        )

    @app.get("/v1/variables/{variable}", dependencies=private)
    def variable(variable: str):
        if len(variable) > 80:
            raise HTTPException(422, "Variable name too long")
        return ready().tools.execute(
            ToolRequest(tool="get_variable_definition", arguments={"variable": variable})
        )

    @app.post("/v1/data/query", dependencies=private)
    def query(request: ToolRequest):
        try:
            return ready().tools.execute(request)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.post("/v1/chat", response_model=AnswerResult, dependencies=private)
    def chat(request: ChatRequest):
        s = ready()
        with lock:
            now = monotonic()
            while recent and now - recent[0] >= 60:
                recent.popleft()
            if len(recent) >= 20:
                raise HTTPException(429, "Instance rate limit reached")
            recent.append(now)
        if not slots.acquire(blocking=False):
            raise HTTPException(429, "Instance is busy")
        try:
            return s.ask(request)
        finally:
            slots.release()

    @app.get("/v1/sources/{source_id}", dependencies=private)
    def source(source_id: str):
        for item in ready().retriever.sources:
            if item.source_id == source_id:
                return item
        raise HTTPException(404, "Source not found")

    @app.get("/v1/evidence/{chunk_id}", dependencies=private)
    def evidence(chunk_id: str):
        retained = ready().tools.retained(chunk_id)
        if retained is not None:
            return retained
        for item in ready().retriever.chunks:
            if item.chunk_id == chunk_id:
                return item
        raise HTTPException(404, "Evidence not found")

    return app


app = create_app()
