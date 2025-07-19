from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow frontend origin (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LogInput(BaseModel):
    log: str

@app.post("/analyze-log")
async def analyze_log(data: LogInput):
    return {"message": f"Received log of length {len(data.log)} chars"}
