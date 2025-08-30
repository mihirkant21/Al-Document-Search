# 📄 AI Document Search (RAG Chatbot)

Chat with your **PDF documents** using an AI-powered chatbot.  
This project uses **Retrieval-Augmented Generation (RAG)** so the answers are based on your uploaded files, not just the model’s memory.  

---

## ✨ Features
- 📂 Upload PDF documents  
- 🔎 Semantic search with embeddings (finds meaning, not just keywords)  
- 💬 Ask natural questions and get accurate, context-aware answers  
- 📑 Source citations from the original document  
- ⚡ Lightweight frontend (HTML, CSS, JS) + FastAPI backend  
- 🧠 Powered by OpenAI + LangChain  
- 📦 Vector database with FAISS (local) or Pinecone (cloud)  

---

## 🛠️ Tech Stack
- **Frontend**: HTML, CSS, JavaScript  
- **Backend**: FastAPI (Python)  
- **AI**: OpenAI (Chat + Embeddings), LangChain  
- **Vector DB**: FAISS (default) / Pinecone (optional)  
- **Deployment**: Docker (backend), Vercel/Static hosting (frontend)  

---

## ⚙️ How It Works
1. **Upload PDF** → Extract text → Chunk into small sections  
2. **Embed chunks** → Convert into vectors using OpenAI embeddings  
3. **Store vectors** → In FAISS or Pinecone  
4. **User asks a question** → Query gets embedded → Retrieve top relevant chunks  
5. **LLM answers** → OpenAI generates a response using those chunks  
6. **Return answer + citations** → Displayed in chatbot UI  

---

## 📂 Project Structure
