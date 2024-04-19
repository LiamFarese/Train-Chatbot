from fastapi import FastAPI, HTTPException, status, Path, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware

from typing import List, Annotated
from pydantic import BaseModel
from datetime import datetime
import uuid
import json

from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

#* temporary db
sessions = {}

origins = [
    "http://localhost:8081", 
    "localhost:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class SessionBody(BaseModel):
    session_ID: str
    chat_hist: list
    timestamp: str
    user_ID: str
    session_active: bool

def getDb():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(getDb)]

def saveResponse(response: str):
    #TODO: Add logic to save response to db
    pass

def generateResponse(user_message: str):
    #TODO: Add response generation logic
    pass

@app.get("/user/ID")
def getUserID(request: Request):
    #* Check if user ID cookie exists
    user_ID = request.cookies.get("user_ID")
    if user_ID:
        return {"user_ID": user_ID}
    else:
        #* Generate new unique user ID
        new_ID = str(uuid.uuid4())
        
        #* Return the new user ID and set it as a cookie
        response = Response(json.dumps({"user_ID": new_ID}))
        response.set_cookie("user_ID", value=new_ID, max_age=3600, httponly=True)
        return response


@app.post("/user/send-chat/")
def chat(session_ID: str, user_message: str):
    
    #* Check if session exsists
    if session_ID not in sessions:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    session = sessions[session_ID]
    
    if not session.session_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session is inactive")
        
    #* Get the session from database
    session = sessions[session_ID]
    
    #* Append user's message to chat history
    session.chat_hist.append({"user": True, "message": user_message, "timestamp": datetime.now().isoformat()})
    
    #* Update the session's timestamp
    session.timestamp = datetime.now().isoformat()
    
    return {"message": "Message recieved and processed successfully"}

@app.get("/session")
def getSession():
    
    for session_ID in sessions.keys():
        session = sessions[session_ID]
        
        #* Check if session is active
        if session.session_active:
            return {"message": "Session found", "data": sessions[session_ID]}
    
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active sessions found")

@app.get("/session/{session_ID}")
def getSession(session_ID: str):
    
    #* Check if session exists
    if session_ID not in sessions:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")

    return {"message": "Session found", "data": sessions[session_ID]}

@app.post("/session/start/")
def startSession(user_ID: str, db: db_dependency):
    
    #* Generate unique session ID
    session_ID = f"{user_ID}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    #* Establish a new SessionBody object
    session_data = SessionBody(
        session_ID=session_ID,
        chat_hist=[],
        timestamp=datetime.now().isoformat(),
        user_ID=user_ID,
        session_active=True
    )
    
    #* Add newly created session data to database
    #sessions[session_ID] = session_data
    db_session = models.Session(session_id=session_data.session_ID, chat_history=session_data.chat_hist, 
                                timestamp=session_data.timestamp, user_id=session_data.user_ID, 
                                session_active=session_data.session_active)
    
    db.add(db_session)
    db.commit()
    db.refresh()
    
    
    return {"message": "Session started successfully", "session_ID": session_ID}

@app.post("/session/end/")
def endSession():
    for session_ID in sessions.keys():
        session = sessions[session_ID]
        
        #* Check if session is active
        if session.session_active:
            
            #* Set session to inactive
            session.session_active = False
            
            return {"message": "Session ended successfully"}
    
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active sessions found")

@app.post("/session/end/{session_ID}")
def endSession(session_ID: str):
    
    #* Check if session exists
    if session_ID not in sessions:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")

    session = sessions[session_ID]
    
    #* Set session to inactive
    session.session_active = False
    
    return {"message": "Session ended"}

@app.post("/session/reset/")
def resetSession():
    for session_ID in sessions.keys():
        session = sessions[session_ID]
        
        #* Check if session is active
        if session.session_active:
            
            #* Reset all variable values in the session's SessionBody
            session.chat_hist = []
            session.timestamp = datetime.now().isoformat()
            
            return {"message": "Session reset successfully"}
    
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active session found")

@app.post("/session/reset/{session_ID}")
def resetSession(session_ID: str):
    
    #* Check if session exists
    if session_ID not in sessions:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active session found")
    
    session = session[session_ID]
    
    #* Reset all variable values in the session's SessionBody
    session.chat_hist = []
    session.timestamp = datetime.now().isoformat()
    
    return {"message": "Session reset successfully"}
 
