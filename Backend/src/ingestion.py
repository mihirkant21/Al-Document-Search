# src/ingestion.py
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def ingest_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)

def create_faiss_index(docs, index_dir="faiss_index"):
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(index_dir)
    return index_dir

def load_faiss_index(index_dir="faiss_index"):
    if not os.path.exists(os.path.join(index_dir, "index.faiss")):
        raise FileNotFoundError("FAISS index not found. Upload a PDF first.")
    return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
