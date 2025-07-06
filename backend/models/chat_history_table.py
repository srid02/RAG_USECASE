
from sqlalchemy import Column, Integer, String, LargeBinary, text, DateTime, Text
from models.table_structure import Basemodel 
from datetime import datetime
from utils.db_connections import  get_session
from fastapi import HTTPException
from models.table_structure import PDFData


class ChatLog(Basemodel):
    __tablename__ = 'chat_logs'
    id = Column(Integer, primary_key=True)
    user_query = Column(Text)
    bot_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.now())
    

def get_all_chat_logs():
    """
    Retrieve all chat logs from the database.
    
    Returns:
        list: A list of dictionaries containing chat log details.
    """
    session = get_session()  
    logs = session.query(ChatLog).all()
    return [
        {
            "id": log.id,
            "user_query": log.user_query,
            "bot_response": log.bot_response,
            "timestamp": log.timestamp,
            "matched_source": log.matched_source
        }
        for log in logs
    ]

def get_chat_log_by_id(log_id: int):
    """
    Retrieve a chat log by its ID.
    Args:
        log_id (int): The ID of the chat log.
    Returns:
        dict: A dictionary containing the chat log details.
    """
    session = get_session()  
    log = session.query(ChatLog).filter_by(id=log_id).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Chat log not found")
    
    return {
        "id": log.id,
        "user_query": log.user_query,
        "bot_response": log.bot_response,
        "timestamp": log.timestamp,
        "matched_source": log.matched_source
    }

def store_chat_log(user_query: str, bot_response: str):
    """
    Store a chat log in the database.
    
    Args:
        user_query (str): The user's query.
        bot_response (str): The bot's response.
        matched_source (str): The source that matched the query.
    """
    session = get_session()  
    new_log = ChatLog(
        user_query=user_query,
        bot_response=bot_response,
    )
    
    session.add(new_log)
    session.commit()
    session.refresh(new_log)
    
    return {
        "id": new_log.id,
        "user_query": new_log.user_query,
        "bot_response": new_log.bot_response,
        "timestamp": new_log.timestamp,
    }