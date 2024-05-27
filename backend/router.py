from fastapi import FastAPI, HTTPException, status, Request, Response, Depends, Header, Body
from fastapi.middleware.cors import CORSMiddleware

from typing import Union
from typing_extensions import Annotated
from pydantic import BaseModel
from datetime import datetime
import uuid
import json

from database import engine, SessionLocal
from sqlalchemy import func
from sqlalchemy.orm import Session
import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SessionBody(BaseModel):
    session_ID: str
    chat_hist: list
    context: dict
    timestamp: str
    user_ID: str
    session_active: bool

def getDb():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Depends(getDb)

def saveResponse(response: str):
    #TODO: Add logic to save response to db
    pass

def generateResponse(user_message: str):
    return "Response from Backend"

@app.get("/user/hello")
def hello():
    try:
        return {"message": "Hello. How can I help? :)"}
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

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
        response.set_cookie("user_ID", value=new_ID, max_age=9999, httponly=True)
        return response


@app.post("/user/send-chat/")
def chat(session_ID: Annotated[Union[str, None], Body()] = None, 
         user_message: Annotated[Union[str, None], Body()] = None, 
         context: Annotated[Union[dict, None], Body()] = None, 
         db: Session = db_dependency):
    
    session = db.query(models.Session).filter(models.Session.session_id == session_ID).first()
    
    #* Check if session exsists
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    #* Check that session is active
    if not session.session_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session is inactive")
    
    new_timestamp = datetime.now().isoformat()
    
    exisiting_history = session.chat_history
    
    exisiting_history.append({
        "user": True,
        "message": user_message,
        "timestamp": new_timestamp
    })
    
    #* Update chat history
    db.query(models.Session).filter(models.Session.session_id == session.session_id).update({'chat_history': exisiting_history})
        
    #* Update the session's timestamp
    db.query(models.Session).filter(models.Session.session_id == session.session_id).update({'timestamp': new_timestamp})
    
    db.commit()
    db.refresh(session)
    
    return {"message": "Message recieved and processed successfully"}

@app.get("/session")
def getSession(db: Session = db_dependency):
    #* Checks for the latest session that is still active
    session = db.query(models.Session).filter(models.Session.session_active == True).first()
    
    #* Check if active session exists
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active sessions found")
    
    print(session.chat_history)
    
    return {"message": "Session found", "session_data": session}

@app.get("/session/{session_ID}")
def getSession(session_ID: str, db: Session = db_dependency):
    #* Query the database for a session by session ID
    session = db.query(models.Session).filter(models.Session.session_id == session_ID).first()
    
    #* Check if session exists
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    return {"message": "Session found", "data": session}

@app.post("/session/start/{user_ID}/")
def startSession(user_ID: str, db: Session = db_dependency):

    #* Generate unique session ID
    session_ID = f"{user_ID}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    #* Establish a new SessionBody object
    session_data = SessionBody(
        session_ID=session_ID,
        chat_hist=[],
        context={},
        timestamp=datetime.now().isoformat(),
        user_ID=user_ID,
        session_active=True
    )
    
    #* Add newly created session data to database
    db_session = models.Session(session_id=session_data.session_ID, chat_history=session_data.chat_hist, 
                                timestamp=session_data.timestamp, user_id=session_data.user_ID, 
                                session_active=session_data.session_active)
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return {"message": "Session started successfully", "session_ID": session_ID}

@app.post("/session/end/")
def endSession(db: Session = db_dependency):
    #* Get the latest active session
    session = db.query(models.Session).filter(models.Session.session_active == True).first()
    
    #* Check if active session exists
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active sessions found")
        
    #* Set session to inactive
    db.query(models.Session).filter(models.Session.session_id == session.session_id).update({'session_active': False})
    db.commit()
    db.refresh(session)
    
    return {"message": "Session ended successfully"}

@app.post("/session/end/{session_ID}")
def endSession(session_ID: str, db: Session = db_dependency):
    #* Get session by session ID
    session = db.query(models.Session).filter(models.Session.session_id == session_ID).first()
    
    #* Check if active session exists
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active sessions found")
        
    #* Set session to inactive
    db.query(models.Session).update({'session_active': False})
    db.commit()
    db.refresh(session)
    
    return {"message": "Session ended successfully"}

@app.post("/session/reset/")
def resetSession(db: Session = db_dependency):
    #* Get the latest active session
    session = db.query(models.Session).filter(models.Session.session_active == True).first()
    
    #* Check if active session exists
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active sessions found")

    new_timestamp = datetime.now().isoformat()
    
    db.query(models.Session).filter(models.Session.session_id == session.session_id).update({'chat_history': []})
    db.query(models.Session).filter(models.Session.session_id == session.session_id).update({'timestamp': new_timestamp})   
    db.commit()
    db.refresh(session)
     
    return {"message": "Session reset successfully"}
    
    
@app.post("/session/reset/{session_ID}")
def resetSession(session_ID: str, db: Session = db_dependency):
    #* Get session by session ID
    session = db.query(models.Session).filter(models.Session.session_id == session_ID).first()
    
    #* Check if active session exists
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active sessions found")
    
    new_timestamp = datetime.now().isoformat()
    
    #* Set session to inactive
    db.query(models.Session).filter(models.Session.session_id == session.session_id).update({'chat_history': []})
    db.query(models.Session).filter(models.Session.session_id == session.session_id).update({'timestamp': new_timestamp})
    db.commit()
    db.refresh(session)
    
    return {"message": "Session reset successfully"}
