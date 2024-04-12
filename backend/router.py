from fastapi import FastAPI, HTTPException, status, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

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
    session_id: str
    chat_hist: list
    timestamp: str
    user_ID: str
    session_active: bool

def saveResponse(response: str):
    #TODO: Add logic to save response to db
    pass

def generateResponse(user_message: str):
    #TODO: Add response generation logic
    pass

@app.post("/send-chat/")
def chat(session_ID: str, user_message: str):
    
    #* Check if session exsists
    if session_ID not in sessions:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    
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
def startSession(user_ID: str):
    
    #* Generate unique session ID
    session_ID = f"{user_ID}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    #* Establish a new SessionBody object
    session_data = SessionBody(
        session_id=session_ID,
        chat_hist=[],
        timestamp=datetime.now().isoformat(),
        user_ID=user_ID,
        session_active=True,
        session_variables={}
    )
    
    #* Add newly created session data to database
    sessions[session_ID] = session_data
    
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
 
