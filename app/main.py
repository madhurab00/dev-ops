import logging
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from pathlib import Path

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

# App Instantiation
app = FastAPI()

# Input validation using pydantic
class InputRequest(BaseModel):
    a: float
    b: float

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
    return {"result":result}



