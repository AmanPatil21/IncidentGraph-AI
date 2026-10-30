from fastapi import FastAPI
from pydantic import BaseModel , Field
from Retriever import ask_question
from agent.gemini_agent import investigate
from fastapi import HTTPException
from langchain_google_genai.chat_models import GoogleRateLimitError, GoogleAPIError

app = FastAPI(title= "IncidentGraph AI")

class AskRequest(BaseModel) :
    question : str = Field(min_length=1)
    session_id : str ="default"

class InvestigateRequest(BaseModel) :
    question : str = Field(min_length=1)
    max_steps : int = Field(default=3, ge=1, le=5)


@app.get("/health")
def health() :
    return {"status" : "ok"}

@app.post("/ask") 
def ask(request : AskRequest) :
    return ask_question(question = request.question ,
                        session_id = request.session_id)


@app.post("/investigate") 
def investigate_incident(request: InvestigateRequest) :
    try :
        return investigate(question= request.question , max_steps = request.max_steps)
    except GoogleRateLimitError :
        raise HTTPException(
            status_code=429,
            detail = "Gemini API quota exceeded. Please retry after the quota resets."
        )
    except GoogleAPIError as error:
        if "503" in str(error):
            raise HTTPException(status_code=503, detail="Gemini is temporarily unavailable. Please retry later.")
        raise HTTPException(status_code=502, detail="Gemini API request failed.")