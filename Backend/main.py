import os
import traceback
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import our new modules from the src directory
from src.ingestion import ingest_pdf, create_faiss_index, load_faiss_index
from src.retrieval import get_answer

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
db = None

@app.get("/")
def read_root():
    """Returns a status message to indicate the backend is running."""
    return {"message": "Backend is running 🚀"}

@app.post("/upload_pdf/")
async def upload_pdf_endpoint(file: UploadFile):
    """
    API endpoint to handle PDF uploads, ingesting the file and creating a FAISS index.
    """
    global db
    print(f"📂 Received file: {file.filename}")
    print(f"Current System PATH: {os.environ.get('PATH')}")
    try:
        # Add a check for the Poppler path in the .env file
        poppler_path = os.getenv("POPPLER_PATH")
        if not poppler_path or not os.path.exists(poppler_path):
            raise ValueError("Poppler path not set in .env file or directory does not exist.")
        
        docs = await ingest_pdf(file.file, poppler_path=poppler_path)
        db = create_faiss_index(docs)
        print("✅ FAISS index created and saved")
        return {"message": f"PDF '{file.filename}' processed and stored successfully."}
    except ValueError as e:
        # A specific check for the Poppler error
        if "poppler installed and in PATH" in str(e):
            print(f"❌ Document ingestion failed: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": "Poppler is not installed or not in your system PATH. Please install Poppler to process scanned PDFs."}
            )
        else:
            print(f"❌ Document ingestion failed: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": str(e)}
            )
    except Exception as e:
        print(f"❌ Unexpected error during PDF upload: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected server error occurred: {str(e)}"}
        )


@app.post("/ask/")
async def ask_question_endpoint(query: str = Form(...)):
    """
    API endpoint to handle questions and retrieve answers from the FAISS index.
    """
    global db
    try:
        if db is None:
            # Check if an index exists on disk
            try:
                db = load_faiss_index()
                print("✅ FAISS index loaded from disk")
            except Exception:
                raise HTTPException(status_code=400, detail="No PDF has been uploaded yet or FAISS index is missing.")
        
        answer = get_answer(db, query)
        print(f"🤖 Query: {query}")
        print(f"💡 Answer: {answer}")
        return {"answer": answer}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Unexpected error during query: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected server error occurred: {str(e)}"}
        )
