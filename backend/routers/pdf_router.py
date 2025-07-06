from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Path
from fastapi.responses import StreamingResponse
from utils.init_db import init_db
from io import BytesIO 
from models.table_structure import PDFData
from utils.db_connections import get_session
from nodes.pdf_extractor import extract_text_table_data_from_file, chunk_text, get_data_chunks_embeddings



router = APIRouter(prefix="/pdf"
                   , tags=["PDF Processing"])


@router.post("/upload/{UPLOAD_FILE}")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and process it.
    
    Args:
        file (UploadFile): The PDF file to be uploaded.
    
    Returns:
        dict: A message indicating the success of the upload.
    """
    text = await file.read()
    content = BytesIO(text)
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    # Extract text and table data from the PDF file
    get_data_chunks_embeddings(content)

    return {"message": f"File '{file.filename}' uploaded successfully."}