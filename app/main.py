import logging
from typing import Optional
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import insert, text
from sqlalchemy.engine import Engine

from db import create_db_engine
from schema import metadata,requests_table

START_TIME = time.time()

total_requests = 0
total_errors = 0
last_latency_ms = 0.0
total_latency_ms = 0.0

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Logging Setup
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    engine = create_db_engine()
    metadata.create_all(engine)
    logger.info("DB connected and schema ensured.")
    
    yield
    
    if engine:
        engine.dispose()
        logger.info("DB connection closed.")

# App Instantiation
app = FastAPI(lifespan=lifespan)

# Input validation using pydantic
class InputRequest(BaseModel):
    a: float
    b: float

@app.middleware("http")
async def simple_metrics_middleware(request: Request, call_next):
    global total_requests, total_errors, last_latency_ms, total_latency_ms

    t0 = time.time()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        total_errors += 1
        raise
    finally:
        dt_ms = (time.time() - t0) * 1000.0
        total_requests += 1
        last_latency_ms = dt_ms
        total_latency_ms += dt_ms
        if status_code >= 500:
            total_errors += 1


# GET /health
@app.get("/health")
def health_check():
    logger.info("Health check endpoint called.")
    return {"status":"ok"}

# Post /sum
@app.post("/sum")
def sum(payload:InputRequest):
    logger.info(f"Sum request received: a={payload.a}, b={payload.b}")
    result = payload.a + payload.b

    if engine is None:
        raise RuntimeError("DB engine not initialized")
    stmt = insert(requests_table).values(a=payload.a, b=payload.b, result=result)
    with engine.begin() as conn:
        conn.execute(stmt)

    return {"result":result}

@app.get("/monitor")
def monitor():
    uptime_s = time.time() - START_TIME
    avg_ms = (total_latency_ms / total_requests) if total_requests > 0 else 0.0

    # DB probe + pool status
    db_ok = False
    db_error = None
    pool_status = None
    try:
        if engine is None:
            raise RuntimeError("engine not initialized")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
        pool_status = engine.pool.status()
    except Exception as e:
        db_error = str(e)

    return {
        "status": "ok",
        "uptime_seconds": round(uptime_s, 2),
        "requests_total": total_requests,
        "errors_total": total_errors,
        "latency_ms": {
            "last": round(last_latency_ms, 2),
            "avg": round(avg_ms, 2),
        },
        "db": {
            "ok": db_ok,
            "error": db_error,
            "pool": pool_status,
        }
    }


