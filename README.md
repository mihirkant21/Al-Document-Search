# 📄 AI Document Search (RAG Chatbot)

Chat with your PDF documents using an **AI-powered chatbot**.  
This project uses **Retrieval-Augmented Generation (RAG)** so the answers are based on your uploaded files, not just the model’s memory.

---

## ✨ Features
- 📂 **Upload PDF documents** for ingestion  
- 🔎 **Semantic search with embeddings** (finds meaning, not just keywords)  
- 💬 **Ask natural questions** and get accurate, context-aware answers  
- 📑 **Source citations** from your original documents  
- ⚡ Lightweight **Frontend (HTML, CSS, JS)** + **FastAPI backend**  
- 🧠 Powered by **Ollama LLM + LangChain**  
- 📦 Vector database with **FAISS (local)**  

---

## 🛠️ Tech Stack
**Frontend:** HTML, CSS, JavaScript  
**Backend:** FastAPI (Python)  
**AI Model:** Ollama (LLM) + LangChain (retrieval & QA chain)  
**Vector DB:** FAISS (default)  
**Deployment:** Docker (backend), Vercel/Static hosting (frontend)  

---

## ⚙️ How It Works
1. **Upload PDF** → Extract text with LangChain loaders  
2. **Chunk text** → Split into smaller sections for better retrieval  
3. **Embed chunks** → Convert into vectors using Ollama embeddings  
4. **Store vectors** → Save in **FAISS** database  
5. **Ask a question** → Query is embedded and compared to stored vectors  
6. **Retrieve top matches** → Most relevant document chunks are selected  
7. **Generate answer** → Ollama LLM forms a response using retrieved chunks  
8. **Return results** → Answer is displayed in the chatbot UI  

---

## 📂 Project Structure
