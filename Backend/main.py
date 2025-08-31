from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil, os, traceback
from src.ingestion import ingest_pdf, create_faiss_index, load_faiss_index
from src.retrieval import get_ollama_qa_chain

app = FastAPI()

class Question(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Backend running 🚀"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Ensure uploads folder exists
        os.makedirs("uploads", exist_ok=True)

        # Save file locally
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"📂 Saved file to: {file_path}")

        # Ingest PDF
        docs = ingest_pdf(file_path)
        create_faiss_index(docs)

        return {"message": f"PDF '{file.filename}' ingested successfully"}

    except Exception as e:
        print("❌ Error during PDF upload:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/ask/")
async def ask_question(query: str = Form(...)):
    try:
        db = load_faiss_index()
        qa_chain = get_ollama_qa_chain(db)
        result = qa_chain.invoke(query)   # ✅ new way
        return {"answer": result}

    except Exception as e:
        print("❌ Error during query:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
