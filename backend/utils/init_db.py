from sqlalchemy import create_engine
from models.table_structure import Basemodel
import os

# Import the ChatLog model so it registers with Basemodel.metadata
from models.chat_history_table import ChatLog  
from models.table_structure import PDFData 

DATABASE_URL = "sqlite:///rag_chatbot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    print(f"Creating tables in database at: {os.path.abspath('rag_chatbot.db')}")
    Basemodel.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()