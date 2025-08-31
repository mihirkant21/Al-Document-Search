from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
db = None
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile):
    """
    Upload a PDF, process into chunks, embed with OpenAI, store in FAISS
    """
    global db
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    db = FAISS.from_documents(docs, embeddings)
    db.save_local("faiss_index")

    return {"message": f"PDF '{file.filename}' processed and stored."}

@app.post("/ask/")
async def ask_question(query: str = Form(...)):
    """
    Ask a question to the uploaded PDF
    """
    global db
    if db is None:
        db = FAISS.load_local("faiss_index", embeddings)

    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(model=os.getenv("LLM_MODEL", "gpt-3.5-turbo")),
        retriever=retriever,
        chain_type="stuff"
    )

    result = qa.run(query)
    return {"answer": result}
