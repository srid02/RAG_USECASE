from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Path
from fastapi.responses import StreamingResponse
from utils.init_db import init_db
from io import BytesIO 
from models.table_structure import PDFData
from utils.db_connections import get_session
from nodes.pdf_extractor import extract_text_table_data_from_file, chunk_text, get_data_chunks_embeddings
from nodes.question_answer_node import get_answer_from_context,get_similar_chunks_for_the_question


router = APIRouter(prefix="/question_answer"
                   , tags=["Question Answering"])


@router.post("/ask_question/")
async def ask_question(question: str):
    """
    Ask a question and get an answer based on the context from the PDF documents.

    Args:
        question (str): The question to be answered.

    Returns:
        dict: A dictionary containing the answer to the question.
    """
    answer = get_similar_chunks_for_the_question(question)
    return {"answer": answer}