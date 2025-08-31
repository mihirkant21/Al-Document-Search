# src/retrieval.py
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA

OLLAMA_MODEL = "glm4"  # make sure you have run `ollama pull glm4`

def get_ollama_qa_chain(vectorstore):
    llm = OllamaLLM(model=OLLAMA_MODEL)
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        chain_type="stuff"
    )
