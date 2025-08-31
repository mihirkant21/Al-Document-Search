import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Use a chunk size for streaming uploads to avoid memory issues
CHUNK_SIZE = 8192

# Globals for the module
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

async def ingest_pdf(file_stream):
    """
    Saves an uploaded PDF file, processes it, and returns the list of documents.

    Args:
        file_stream: A stream-like object for the uploaded file.

    Returns:
        A list of documents processed from the PDF.
    """
    temp_file_path = None
    try:
        # Save PDF to temporary file in chunks
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_file_path = tmp.name
            while content := await file_stream.read(CHUNK_SIZE):
                tmp.write(content)
        
        # Load PDF using PyPDFLoader
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        if not documents:
            raise ValueError("No readable text found in PDF.")
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        if not docs:
            raise ValueError("No text chunks created from PDF. The PDF may be a scanned image.")
        
        return docs
    finally:
        # Ensure temporary file is deleted even if an error occurs
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def create_faiss_index(docs):
    """
    Creates a FAISS index from a list of documents and saves it locally.

    Args:
        docs: A list of text documents.
    """
    db = FAISS.from_documents(docs, embeddings)
    db.save_local("faiss_index")
    return db

def load_faiss_index():
    """
    Loads a FAISS index from a local file.
    """
    db = FAISS.load_local(
        "faiss_index", embeddings, allow_dangerous_deserialization=True
    )
    return db
