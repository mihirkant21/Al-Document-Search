# src/retrieval.py
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

OLLAMA_MODEL = "glm4"  # must match ollama list

def get_ollama_qa_chain(vectorstore):
    """Create a QA chain using Ollama locally"""
    llm = Ollama(model=OLLAMA_MODEL)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        chain_type="stuff",
        return_source_documents=True  # so you also get context
    )
    return qa
