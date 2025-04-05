# CRL Podcast Lookup – Technical Documentation

This document outlines the architecture, workflows, and components of the CRL Podcast Lookup application.

---

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **LLM**: OpenAI GPT (gpt-3.5-turbo)
- **Embeddings**: OpenAI Embeddings (via LangChain)
- **Vector Store**: FAISS (stored locally)
- **Transcript Format**: .docx
- **Metadata**: CSV file with episode details

---

## 🗂️ Key Components

- `app.py`: Streamlit UI for search and results
- `query_module.py`: RAG pipeline for retrieval and response
- `index_transcripts.py`: Embeds and indexes all transcripts
- `data/transcripts/`: Folder for `.docx` transcripts
- `data/episode_metadata.csv`: Metadata for each episode

---

## 📥 Ingestion & Indexing Workflow

```{mermaid}
graph TD
    A[.docx transcripts] --> B[Docx2txtLoader (LangChain)]
    B --> C[Split into Chunks (1000 tokens, 200 overlap)]
    C --> D[Attach Metadata from CSV]
    D --> E[Embed Chunks using OpenAI Embeddings]
    E --> F[Store in FAISS Vector Index]
```

Run via:
```bash
python index_transcripts.py
```

---

## 🤖 Query & RAG Workflow

```mermaid
graph TD
    U[User Enters Query] --> R[FAISS Similarity Search (Top 3)]
    R --> C[Concatenate Context Chunks]
    C --> P[Prompt Template with Context + Question]
    P --> G[GPT (gpt-3.5-turbo) Generates Answer]
    G --> UI[Streamlit UI Displays Answer + Video Embeds]
```

- Matching documents contain metadata with:
  - YouTube URL
  - Episode title, date, description
  - Estimated timestamp (based on chunk index)

---

## 🧠 Retrieval-Augmented Generation (RAG)

- Uses `langchain` retriever to get relevant chunks
- Injects these into a prompt template
- GPT responds based on real transcript content

---

## 💸 Cost Optimization

- Uses **gpt-3.5-turbo** instead of GPT-4
- Responses are **cached** using `st.cache_data`
- Only indexes episodes that exist in metadata CSV

---

## 📺 Timestamp Grouping

- Multiple matching chunks from the same episode are grouped
- UI displays **jump-to timestamp links**
- Only one embedded player per episode

---

## 🔐 Deployment Notes

- Environment variables (like `OPENAI_API_KEY`) are loaded via `.env` or `st.secrets`
- Can be deployed on:
  - Streamlit Community Cloud (with Secrets Manager)
  - Internal servers with Python/Streamlit

---

## ✅ Future Enhancements

- Real timestamps from `.srt` files
- Tag- or topic-based filters
- Admin UI to upload new transcripts and reindex
- Search query logging and analytics

---

## 📬 Contact

For technical issues, reach out to the CRL development team.

