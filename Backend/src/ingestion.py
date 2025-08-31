# src/ingestion.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def ingest_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)
    return split_docs

def create_faiss_index(docs):
    db = FAISS.from_documents(docs, embeddings)
    db.save_local("faiss_index")
    return db

def load_faiss_index():
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    return db
