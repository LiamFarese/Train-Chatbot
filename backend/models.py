from sqlalchemy import Column, String, JSON, Boolean, ForeignKey
from database import Base

class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True, index=True)
    chat_history = Column(JSON)
    context = Column(JSON) 
    timestamp = Column(String)
    user_id = Column(String)
    session_active = Column(Boolean)
    
