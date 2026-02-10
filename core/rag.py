import os
import faiss
import numpy as np
from openai import OpenAI

client = OpenAI()

def load_documents(rag_path: str):
    docs = []
    for file in os.listdir(rag_path):
        if file.endswith(".md"):
            with open(os.path.join(rag_path, file), encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    docs.append(content[:4000])  # límite defensivo
    return docs


def embed_texts(texts):
    # Filtramos textos vacíos o inválidos
    clean_texts = [
        t.strip() for t in texts
        if isinstance(t, str) and t.strip()
    ]

    if not clean_texts:
        raise ValueError("No valid texts to embed for RAG")

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=clean_texts
    )

    return np.array([e.embedding for e in response.data]).astype("float32")


def retrieve_context(query: str, rag_path: str, top_k=3):
    docs = load_documents(rag_path)
    embeddings = embed_texts(docs)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    query_embedding = embed_texts([query[:1000]])
    _, indices = index.search(query_embedding, top_k)

    return "\n\n".join(docs[i] for i in indices[0])
