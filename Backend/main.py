# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import shutil, os, traceback
from src.ingestion import ingest_pdf, create_faiss_index, load_faiss_index
from src.retrieval import get_ollama_qa_chain

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend running 🚀"}

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        os.makedirs("uploads", exist_ok=True)

        # Save PDF
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"📂 Saved file to: {file_path}")

        # Ingest and index
        docs = ingest_pdf(file_path)
        create_faiss_index(docs)

        return {"message": f"PDF '{file.filename}' ingested successfully"}

    except Exception as e:
        print("❌ Error during PDF upload:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/ask/")
async def ask_question(query: str = Form(...)):
    """Ask a question from the ingested PDF"""
    try:
        db = load_faiss_index()
        qa_chain = get_ollama_qa_chain(db)

        # Use invoke instead of deprecated .run
        result = qa_chain.invoke({"query": query})

        # RetrievalQA returns dict with 'result'
        return {"answer": result["result"]}

    except Exception as e:
        print("❌ Error during query:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
