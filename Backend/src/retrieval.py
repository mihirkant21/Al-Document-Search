import os
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI

def get_answer(db, query):
    """
    Uses the FAISS database to answer a question.

    Args:
        db: The FAISS database instance.
        query: The question to be answered.

    Returns:
        The answer to the query.
    """
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(model=os.getenv("LLM_MODEL", "gpt-3.5-turbo-instruct")),
        retriever=retriever,
        chain_type="stuff"
    )
    result = qa.run(query)
    return result
