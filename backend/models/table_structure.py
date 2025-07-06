import sqlalchemy
from sqlalchemy import Column, Integer, String, LargeBinary,DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from utils.db_connections import get_session
from fastapi import HTTPException

Basemodel = declarative_base()

class PDFData(Basemodel):
    __tablename__ = 'pdf_data'
    pdf_id = Column(Integer, primary_key=True, autoincrement=True)
    chunk = Column(String, nullable=False)
    embeddings = Column(LargeBinary, nullable=False)  
    uploaded_at = Column(DateTime, default=datetime.utcnow)


def get_pdf_data_by_id(pdf_id: int):
    """
    Retrieve PDF data by its ID.
    
    Args:
        pdf_id (int): The ID of the PDF document.
    
    Returns:
        dict: A dictionary containing the PDF data.
    """
    session = get_session()
    pdf_data = session.query(PDFData).filter_by(pdf_id=pdf_id).first()
    
    if not pdf_data:
        raise HTTPException(status_code=404, detail="PDF data not found")
    
    return {
        "pdf_id": pdf_data.pdf_id,
        "content": pdf_data.chunk,
        "embeddings": pdf_data.embeddings
    }

def populate_embeddings_in_db(session ,chunk: str, embeddings: bytes):
    """
    Store the PDF content and its embeddings in the database.
    
    Args:
        content (str): The extracted content from the PDF.
        embeddings (bytes): The generated embeddings for the content.
    
    Returns:
        bool: True if the data was successfully stored, False otherwise.
    """
    
    pdf_data = PDFData(chunk=chunk, embeddings=embeddings)
    
    try:
        session.add(pdf_data)
        session.commit()
        print(f"Data stored successfully with ID: {pdf_data.pdf_id}")
        print('location: ', pdf_data.chunk)
        return True
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error storing data: {str(e)}")
    
    return True


