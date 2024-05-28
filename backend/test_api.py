from typing import Optional, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from engine import get_response, get_empty_query

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:8081"],  # Adjust this to match your frontend's origin
  allow_credentials=True,
  allow_methods=["GET", "POST", "OPTIONS"],
  allow_headers=["*"],
)

class Query(BaseModel):
    current_query: Optional[str] = None
    message: Optional[str] = None
    is_return: Optional[bool] = None
    time: Optional[str] = None
    date: Optional[str] = None
    departure: Optional[str] = None
    destination: Optional[str] = None
    return_time: Optional[str] = None
    return_date: Optional[str] = None
    history: List[Any] = []

@app.get("/user/hello")
def hello():
    try:
        return get_response(get_empty_query())
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND) 
    
@app.post("/send-chat")
async def send_chat(query: Query):
  query_dict = query.dict()
  print(query_dict)
  response_query = get_response(query_dict)
  return response_query

if __name__ == "__main__":
    uvicorn.run("test_api:app", host="localhost", port=8000, reload=True)

