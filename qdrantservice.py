"""Qdrant vector database service."""
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import uuid
from dotenv import load_dotenv

load_dotenv()

class QdrantService:
    """Handle vector storage and retrieval."""
    
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.collection = "pdf_docs"
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self._init_collection()
    
    def _init_collection(self):
        """Create collection if not exists."""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection for c in collections):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
    
    def add_documents(self, texts, metadata):
        """Add documents to vector database."""
        try:
            if not texts or not metadata:
                raise ValueError("Texts or metadata is empty.")
            embeddings = self.embedding_model.encode(texts)
            
            points = []
            for i, (text, meta, emb) in enumerate(zip(texts, metadata, embeddings)):
                if not isinstance(meta, dict):
                    raise ValueError(f"Metadata at index {i} is not a dict: {meta}")
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=emb.tolist(),
                        payload={"text": text, **meta}
                    )
                )
            
            if not points:
                raise ValueError("No points to upsert.")
            
            self.client.upsert(collection_name=self.collection, points=points)
        except Exception as e:
            print(f"Error in add_documents: {e}")
            raise
    
    def search(self, query, top_k=5):
        """Search for similar documents."""
        query_vector = self.embedding_model.encode(query).tolist()
        
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
        )
        
        return [
            {
                "text": r.payload["text"],
                "filename": r.payload.get("filename", ""),
                "page": r.payload.get("page", 0),
                "score": r.score
            }
            for r in results
        ]