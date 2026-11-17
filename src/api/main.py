"""
Goethe-Zertifikat B1 Master API — FastAPI Gateway.
Provides asynchronous REST endpoints for LSRW exam modules,
machine learning analytics, Ebbinghaus spaced repetition, and daily duels.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import storage
from src.db import is_db_connected
from src.api.schemas import HealthCheckResponse
from src.api.routers.lsrw_router import router as lsrw_router
from src.api.routers.analytics_router import router as analytics_router
from src.api.routers.duel_router import router as duel_router

app = FastAPI(
    title="Goethe-Zertifikat B1 Meister API",
    description="""
    Enterprise-grade asynchronous API for German B1 Exam preparation,
    pedagogical LSRW modules, ML readiness prediction, and bilingual learning analytics.
    
    ### Architecture Highlights:
    * **Multi-Model LLM Cascade**: High-resilience AI failover across Gemini models.
    * **Machine Learning**: Goethe B1 Readiness Index and Ebbinghaus Recall Decay (Pandas & NumPy).
    * **Serverless Cloud Persistence**: Neon PostgreSQL with automatic local circuit breaker fallback.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend clients, local dev, and Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular routers
app.include_router(lsrw_router)
app.include_router(analytics_router)
app.include_router(duel_router)


@app.get("/health", response_model=HealthCheckResponse, tags=["System Health"])
async def health_check():
    """
    Returns system status, active database connectivity, and timestamp.
    """
    db_status = is_db_connected()
    return HealthCheckResponse(
        status="ok",
        app_version="2.0.0",
        database_connected=db_status,
        timestamp=datetime.now().isoformat()
    )


@app.get("/", tags=["System Health"])
async def root():
    return {
        "message": "Welcome to Goethe-Zertifikat B1 Meister API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "version": "2.0.0"
    }
