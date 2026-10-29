"""RAG pipeline: HF embeddings + Qdrant + Cohere rerank + Ollama local LLM."""

import cohere
import ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
store = QdrantVectorStore(client=QdrantClient(":memory:"), collection_name="docs", embedding=emb)
co = cohere.Client("COHERE_API_KEY")


def answer(q: str) -> str:
    docs = store.similarity_search(q, k=20)
    ranked = co.rerank(model="rerank-english-v3.0", query=q,
                       documents=[d.page_content for d in docs], top_n=4)
    ctx = "\n".join(docs[r.index].page_content for r in ranked.results)
    return ollama.chat(model="llama3.1:8b",
                       messages=[{"role": "user", "content": f"{ctx}\n\n{q}"}])["message"]["content"]
