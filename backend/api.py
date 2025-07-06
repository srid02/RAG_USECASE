from fastapi import FastAPI
from contextlib import asynccontextmanager
from utils.init_db import init_db
from routers.question_answer_router import router as qa_router
from routers.pdf_router import router as pdf_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  
    yield
    

app = FastAPI(lifespan=lifespan)
app.include_router(pdf_router)
app.include_router(qa_router)