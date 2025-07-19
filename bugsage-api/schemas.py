from pydantic import BaseModel

class BugRequest(BaseModel):
    error: str

class BugResponse(BaseModel):
    explanation: str
