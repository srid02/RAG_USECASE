from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "sqlite:///rag_chatbot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """
    Creates and returns a new SQLAlchemy session.
    Be sure to call `session.close()` after you're done using it.
    
    Returns:
        session (Session): A new SQLAlchemy session instance.
    """
    print(os.path.abspath("rag_chatbot.db"))
    return SessionLocal()