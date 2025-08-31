from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA

OLLAMA_MODEL = "glm4"  # replace with your model

def get_ollama_qa_chain(vectorstore):
    llm = OllamaLLM(model=OLLAMA_MODEL)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        chain_type="stuff"
    )
    return qa
