import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey
import unstructured
from unstructured.partition.auto import partition
from unstructured.documents.elements import Table
# from nodes.embedding_generation import generate_embeddings
from utils.db_connections import get_session
from models.table_structure import populate_embeddings_in_db
from sentence_transformers import SentenceTransformer
from models.table_structure import PDFData
import os
import numpy as np


def generate_embeddings(text: str, model_name: str = "all-MiniLM-L6-v2") -> list:
    """
    Generate embeddings for the given text using a specified SentenceTransformer model.

    Args:
        text (str): The input text to generate embeddings for.
        model_name (str): The name of the SentenceTransformer model to use.

    Returns:
        list: A list of embeddings for the input text.
    """
    model = SentenceTransformer(model_name)
    embeddings = model.encode(text, convert_to_tensor=True)
    return embeddings.tolist()  # Convert tensor to list for easier handling



from unstructured.documents.elements import Table

def extract_text_table_data_from_file(file):
    elements = partition(file=file)
    content = []

    for element in elements:
      
        if isinstance(element, Table):
            # Format the table rows
            print(
                'file proceed to table extraction: ',
            )
            table_text = ""
            for row in element.table:
                row_text = "\t".join(cell.text for cell in row)
                table_text += row_text + "\n"
            content.append(table_text.strip())
        else:
            # For any other element, add its text if it exists and non-empty
            print(
                'file proceed to text extraction: ',
            )
            text = getattr(element, "text", None)
            if text:
                content.append(text.strip())
    # print("\n\n".join(content))
    return "\n\n".join(content)



def chunk_text(text, chunk_size=300):
    """
    Chunk text into smaller parts.
    
    Args:
        text (str): The text to be chunked.
        chunk_size (int): The size of each chunk.
    
    Returns:
        list: List of text chunks.
    """
    print(f"Chunking text into parts of size characters.")
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def get_data_chunks_embeddings( file, chunk_size=300):
    
    content = extract_text_table_data_from_file(file)
    chunks = chunk_text(content, chunk_size)
    session = get_session()
    embeddings = []
    for chunk in chunks:
        print(chunk)
        # Assuming a function `generate_embeddings` exists to generate embeddings for the chunk
        embedding = generate_embeddings(chunk)
        print(f"Generated embedding for chunk: {chunk[:50]}...")
        # Store the chunk and its embedding in the database 
        embedding_array = np.array(embedding, dtype=np.float32)
        embedding = embedding_array.tobytes()
        populate_embeddings_in_db(session, chunk, embedding)
        print(f"Stored chunk:  with embedding.")
        session.commit()
    session.close()
    embeddings.append(embedding)
    return {
        "chunks": chunks,
        "embeddings": embeddings,
    }
    
    