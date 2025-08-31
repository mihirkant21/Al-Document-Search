import os
import tempfile
import traceback
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, OpenAI

# OCR
from pdf2image import convert_from_path
import pytesseract

# Load environment variables
load_dotenv()

# If Tesseract is not in PATH, set it explicitly:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Embedding selection ----------------- #
USE_DUMMY_EMBEDDINGS = True  # Set True to test without OpenAI

if USE_DUMMY_EMBEDDINGS:
    class DummyEmbeddings:
        def embed_documents(self, texts):
            return [[0.0]*1536 for _ in texts]  # fixed-length dummy vectors
    embeddings = DummyEmbeddings()
else:
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Globals
db = None
all_chunks_text = []  # Store text chunks for preview

@app.get("/")
def read_root():
    return {"message": "Backend is running 🚀"}

# ----------------- Upload PDF ----------------- #
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile):
    global db, all_chunks_text
    print(f"📂 Received file: {file.filename}")
    all_chunks_text = []

    try:
        # Save PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            file_path = tmp.name
        print(f"✅ Saved file at: {file_path}")

        # Try loading text normally
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"📄 Pages loaded by PyPDFLoader: {len(documents)}")

        # If no text, do OCR
        if not documents or all(not doc.page_content.strip() for doc in documents):
            print("⚠️ No text found, performing OCR...")
            documents = []
            pages = convert_from_path(file_path)
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                if text.strip():
                    documents.append(type('Doc', (object,), {"page_content": text})())
            print(f"📄 Pages loaded by OCR: {len(documents)}")

        if not documents:
            return {"error": "No text found in PDF even after OCR. Cannot process."}

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        if not docs:
            return {"error": "No text chunks could be created from PDF."}
        print(f"🔎 Split into {len(docs)} chunks")

        # Save chunks text for preview
        all_chunks_text = [doc.page_content for doc in docs]

        # Create FAISS index
        try:
            db = FAISS.from_documents(docs, embeddings)
            db.save_local("faiss_index")
            print("✅ FAISS index created and saved")
        except Exception as e:
            print(f"❌ FAISS creation failed: {e}")
            traceback.print_exc()
            return {"error": f"Failed to create FAISS index: {str(e)}"}

        os.remove(file_path)
        print(f"🗑️ Temporary file deleted: {file_path}")

        return {"message": f"PDF '{file.filename}' processed successfully.", "total_chunks": len(all_chunks_text)}

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return {"error": f"Unexpected error: {str(e)}"}

# ----------------- Ask Question ----------------- #
@app.post("/ask/")
async def ask_question(query: str = Form(...)):
    global db
    try:
        if db is None:
            if not os.path.exists("faiss_index"):
                return {"error": "No PDF has been uploaded yet or FAISS index missing."}
            db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            print("✅ FAISS index loaded from disk")

        retriever = db.as_retriever()
        qa = RetrievalQA.from_chain_type(
            llm=OpenAI(model=os.getenv("LLM_MODEL", "gpt-3.5-turbo")),
            retriever=retriever,
            chain_type="stuff"
        )
        result = qa.run(query)
        print(f"🤖 Query: {query}")
        print(f"💡 Answer: {result}")
        return {"answer": result}

    except Exception as e:
        print(f"❌ Error answering query: {e}")
        traceback.print_exc()
        return {"error": f"Unexpected error: {str(e)}"}

# ----------------- Preview PDF Chunks ----------------- #
@app.get("/preview_pdf/")
def preview_pdf(num_chunks: int = 3):
    """
    Preview first few chunks of the uploaded PDF.
    """
    global all_chunks_text
    if not all_chunks_text:
        return {"error": "No PDF has been uploaded yet."}

    preview = all_chunks_text[:num_chunks]
    return {
        "message": "Preview of uploaded PDF chunks",
        "total_chunks": len(all_chunks_text),
        "preview_chunks": preview
    }
