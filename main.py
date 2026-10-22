from fastapi import FastAPI
from pydantic import BaseModel , Field
from Retriver import ask_question

app = FastAPI(title= "IncidentGraph AI")

class AskRequest(BaseModel) :
    question : str = Field(min_length=1)
    session_id : str ="default"



@app.get("/health")
def health() :
    return {"status" : "ok"}

@app.post("/ask") 
def ask(request : AskRequest) :
    return ask_question(question = request.question ,
                        session_id = request.session_id)