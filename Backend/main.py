# main.py
import os, shutil, traceback
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.ingestion import ingest_pdf, create_faiss_index, load_faiss_index
from src.retrieval import get_ollama_qa_chain

app = FastAPI()

# ✅ Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Backend running 🚀"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        docs = ingest_pdf(file_path)
        create_faiss_index(docs)
        return {"message": f"PDF '{file.filename}' ingested successfully"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

@app.post("/ask")
async def ask_question(question: Question):
    try:
        db = load_faiss_index()
        qa = get_ollama_qa_chain(db)
        result = qa.invoke({"query": question.query})

        if isinstance(result, dict):
            answer = result.get("result") or result.get("answer") or str(result)
        else:
            answer = str(result)
        return {"answer": answer}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")
