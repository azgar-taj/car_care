from global_helpers import setup_logger
from fastapi import FastAPI
import uvicorn

logger = setup_logger()

app = FastAPI()

@app.get("/")
def read_root():
    logger.debug("Received request")
    return {"Hello": "World"}
