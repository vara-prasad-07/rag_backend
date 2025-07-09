from fastapi import FastAPI, Request
from pydantic import BaseModel
from rag_model import chatbot
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
bot = chatbot("my_resume.pdf")  # Loads model and index once

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask_question(request: QueryRequest):
    answer = bot.query(request.query)
    return {"answer": answer}
    
@app.get("/")
def read_root():
    return {"message": "Hello from Railway!"}
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
