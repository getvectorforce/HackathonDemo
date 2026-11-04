"""ChromaDB Vector Store management and retrieval for Banking Policies and SOPs."""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from config import CHROMA_PERSIST_DIR, DOCUMENTS_DIR


class BankingVectorStore:
    """Manages the banking policies and SOP knowledge base using ChromaDB."""

    COLLECTION_NAME = "banking_knowledge_base"

    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR, docs_dir: str = DOCUMENTS_DIR):
        self.persist_dir = persist_dir
        self.docs_dir = Path(docs_dir)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "Banking Regulations, SOPs, and Operations Knowledge Base"}
        )
        self._ensure_documents_indexed()

    def _ensure_documents_indexed(self):
        """Indexes markdown policy documents if collection is empty."""
        count = self.collection.count()
        if count > 0:
            return  # Already populated

        if not self.docs_dir.exists():
            return

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        chunk_counter = 0
        for file_path in self.docs_dir.glob("*.md"):
            category = file_path.stem.replace("_", " ").title()
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split document by sections (Markdown headers)
            sections = content.split("## ")
            doc_title = sections[0].replace("#", "").strip()

            for idx, section in enumerate(sections[1:], start=1):
                lines = section.split("\n", 1)
                section_title = lines[0].strip()
                section_body = lines[1].strip() if len(lines) > 1 else ""

                full_chunk = f"Document: {doc_title}\nSection: {section_title}\nCategory: {category}\n\n{section_body}"
                
                chunk_id = f"{file_path.stem}_sec_{idx}_{chunk_counter}"
                chunk_counter += 1

                documents.append(full_chunk)
                metadatas.append({
                    "source": file_path.name,
                    "category": file_path.stem,
                    "section": section_title,
                    "doc_title": doc_title,
                })
                ids.append(chunk_id)

        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

    def query(self, query_text: str, n_results: int = 2, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries the vector store for relevant banking policies and SOPs."""
        where_clause = {"category": category} if category else None
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_clause
        )

        formatted: List[Dict[str, Any]] = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                formatted.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                })
        return formatted


_store_instance: Optional[BankingVectorStore] = None


def get_banking_vector_store() -> BankingVectorStore:
    """Singleton getter for the BankingVectorStore."""
    global _store_instance
    if _store_instance is None:
        _store_instance = BankingVectorStore()
    return _store_instance


def retrieve_banking_knowledge(query: str, n_results: int = 2, category: Optional[str] = None) -> str:
    """Helper tool function used by agents to search the ChromaDB knowledge base."""
    store = get_banking_vector_store()
    records = store.query(query_text=query, n_results=n_results, category=category)
    if not records:
        return "No relevant banking policies found in knowledge base."
    
    parts = []
    for r in records:
        src = r["metadata"].get("source", "Policy Doc")
        sec = r["metadata"].get("section", "General")
        parts.append(f"--- [Source: {src} | Section: {sec}] ---\n{r['content']}")
    return "\n\n".join(parts)

