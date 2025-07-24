from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from schemas import BugResponse
from llm_chain import explain_bug
from llm_chain1 import explain_bug2

app = FastAPI()

# CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class BugRequest(BaseModel):
    log: str
    lang: str = "en"

@app.post("/api/analyze-log", response_model=BugResponse)
def get_bug_explanation(request: BugRequest):
    print("[INFO] Received log input")
    print(f"[DEBUG] Log content: {request.log}")
    print(f"[DEBUG] Language: {request.lang}")

    if not request.log.strip():
        print("[ERROR] Empty log input received")
        raise HTTPException(status_code=400, detail="Log input cannot be empty.")

    try:
        explanation = explain_bug2(request.log, lang=request.lang)
        print("[INFO] Successfully generated explanation")
        return BugResponse(explanation=explanation)
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error: "+e)
    
