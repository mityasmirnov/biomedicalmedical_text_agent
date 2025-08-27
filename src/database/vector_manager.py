"""
Vector database manager for semantic search and document indexing.
"""

import json
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# Remove circular imports
# from core.base import Document, ProcessingResult
# from core.logging_config import get_logger

log = logging.getLogger(__name__)

# Simple classes to avoid circular imports
class Document:
    """Simple document class for vector operations."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ProcessingResult:
    """Simple processing result class for vector operations."""
    def __init__(self, success: bool, data: Any = None, error: str = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}

class VectorManager:
    """Manages vector database operations for semantic search."""
    
    def __init__(self, index_path: str = "data/vector_indices"):
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.embeddings_model = None
        self.faiss_index = None
        self.document_metadata = {}
        self.embedding_dim = 384  # Default for sentence-transformers/all-MiniLM-L6-v2
        
        self._initialize_embeddings()
        self._load_or_create_index()
    
    def _initialize_embeddings(self):
        """Initialize the embeddings model."""
        try:
            # Try to import sentence-transformers
            from sentence_transformers import SentenceTransformer
            
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            log.info(f"Loading embeddings model: {model_name}")
            self.embeddings_model = SentenceTransformer(model_name)
            self.embedding_dim = self.embeddings_model.get_sentence_embedding_dimension()
            
            log.info(f"Embeddings model loaded with dimension: {self.embedding_dim}")
            
        except ImportError:
            log.warning("sentence-transformers not available, using simple TF-IDF fallback")
            self._initialize_tfidf_fallback()
        except Exception as e:
            log.error(f"Error initializing embeddings model: {str(e)}")
            self._initialize_tfidf_fallback()
    
    def _initialize_tfidf_fallback(self):
        """Initialize TF-IDF as fallback when sentence-transformers is not available."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            self.use_tfidf = True
            self.embedding_dim = 1000  # Max features for TF-IDF
            log.info("Initialized TF-IDF fallback for embeddings")
            
        except ImportError:
            log.error("Neither sentence-transformers nor scikit-learn available")
            self.embeddings_model = None
            self.use_tfidf = False
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create a new one."""
        try:
            import faiss
            
            index_file = self.index_path / "faiss_index.bin"
            metadata_file = self.index_path / "metadata.json"
            
            if index_file.exists() and metadata_file.exists():
                # Load existing index
                self.faiss_index = faiss.read_index(str(index_file))
                with open(metadata_file, 'r') as f:
                    self.document_metadata = json.load(f)
                log.info(f"Loaded existing FAISS index with {self.faiss_index.ntotal} vectors")
            else:
                # Create new index
                self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
                self.document_metadata = {}
                log.info(f"Created new FAISS index with dimension {self.embedding_dim}")
                
        except ImportError:
            log.warning("FAISS not available, using simple in-memory search")
            self.faiss_index = None
            self.vectors = []
            self.document_metadata = {}
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for a list of texts."""
        if self.embeddings_model:
            # Use sentence-transformers
            embeddings = self.embeddings_model.encode(texts, convert_to_numpy=True)
            # Normalize for cosine similarity
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            return embeddings
        
        elif hasattr(self, 'use_tfidf') and self.use_tfidf:
            # Use TF-IDF fallback
            if not hasattr(self, '_tfidf_fitted'):
                # Fit TF-IDF on the texts
                self.tfidf_vectorizer.fit(texts)
                self._tfidf_fitted = True
            
            embeddings = self.tfidf_vectorizer.transform(texts).toarray()
            return embeddings.astype(np.float32)
        
        else:
            # Simple word count fallback
            log.warning("Using simple word count fallback for embeddings")
            embeddings = []
            for text in texts:
                # Simple bag of words representation
                words = text.lower().split()
                word_counts = {}
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
                
                # Convert to fixed-size vector (top 100 most common words)
                vector = [0] * 100
                for i, (word, count) in enumerate(sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:100]):
                    if i < 100:
                        vector[i] = count
                
                embeddings.append(vector)
            
            return np.array(embeddings, dtype=np.float32)
    
    def add_documents(self, documents: List[Document]) -> ProcessingResult:
        """Add documents to the vector index."""
        try:
            if not documents:
                return ProcessingResult(success=True, data=0)
            
            # Prepare texts for embedding
            texts = []
            metadata = []
            
            for doc in documents:
                # Combine title and content for embedding
                text = f"{getattr(doc, 'title', '')} {getattr(doc, 'content', '')}"
                texts.append(text)
                
                # Store metadata
                doc_metadata = {
                    'id': doc.id,
                    'title': getattr(doc, 'title', ''),
                    'source_path': getattr(doc, 'source_path', ''),
                    'metadata': getattr(doc, 'metadata', {})
                }
                metadata.append(doc_metadata)
            
            # Get embeddings
            embeddings = self.get_embeddings(texts)
            
            if self.faiss_index is not None:
                # Add to FAISS index
                import faiss
                
                # Ensure embeddings are the right dimension
                if embeddings.shape[1] != self.embedding_dim:
                    log.warning(f"Embedding dimension mismatch: {embeddings.shape[1]} vs {self.embedding_dim}")
                    # Pad or truncate as needed
                    if embeddings.shape[1] < self.embedding_dim:
                        padding = np.zeros((embeddings.shape[0], self.embedding_dim - embeddings.shape[1]))
                        embeddings = np.hstack([embeddings, padding])
                    else:
                        embeddings = embeddings[:, :self.embedding_dim]
                
                # Add vectors to index
                start_id = self.faiss_index.ntotal
                self.faiss_index.add(embeddings.astype(np.float32))
                
                # Update metadata
                for i, meta in enumerate(metadata):
                    self.document_metadata[str(start_id + i)] = meta
                
            else:
                # Simple in-memory storage
                if not hasattr(self, 'vectors'):
                    self.vectors = []
                
                start_id = len(self.vectors)
                self.vectors.extend(embeddings.tolist())
                
                for i, meta in enumerate(metadata):
                    self.document_metadata[str(start_id + i)] = meta
            
            # Save index and metadata
            self._save_index()
            
            log.info(f"Added {len(documents)} documents to vector index")
            
            return ProcessingResult(
                success=True,
                data=len(documents),
                metadata={"total_vectors": len(self.document_metadata)}
            )
            
        except Exception as e:
            log.error(f"Error adding documents to vector index: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to add documents: {str(e)}"
            )
    
    def search(self, query: str, top_k: int = 10) -> ProcessingResult:
        """Search for similar documents using vector similarity."""
        try:
            if not self.document_metadata:
                return ProcessingResult(
                    success=True,
                    data=[],
                    metadata={"query": query, "total_found": 0}
                )
            
            # Get query embedding
            query_embedding = self.get_embeddings([query])
            
            if self.faiss_index is not None:
                # Search using FAISS
                import faiss
                
                # Ensure query embedding has the right dimension
                if query_embedding.shape[1] != self.embedding_dim:
                    if query_embedding.shape[1] < self.embedding_dim:
                        padding = np.zeros((1, self.embedding_dim - query_embedding.shape[1]))
                        query_embedding = np.hstack([query_embedding, padding])
                    else:
                        query_embedding = query_embedding[:, :self.embedding_dim]
                
                scores, indices = self.faiss_index.search(query_embedding.astype(np.float32), top_k)
                
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if idx >= 0:  # Valid index
                        metadata = self.document_metadata.get(str(idx), {})
                        results.append({
                            'rank': i + 1,
                            'score': float(score),
                            'document_id': metadata.get('id', ''),
                            'title': metadata.get('title', ''),
                            'source_path': metadata.get('source_path', ''),
                            'metadata': metadata.get('metadata', {})
                        })
                
            else:
                # Simple cosine similarity search
                if not hasattr(self, 'vectors') or not self.vectors:
                    return ProcessingResult(
                        success=True,
                        data=[],
                        metadata={"query": query, "total_found": 0}
                    )
                
                vectors = np.array(self.vectors)
                
                # Calculate cosine similarity
                similarities = np.dot(vectors, query_embedding.T).flatten()
                
                # Get top-k results
                top_indices = np.argsort(similarities)[::-1][:top_k]
                
                results = []
                for i, idx in enumerate(top_indices):
                    metadata = self.document_metadata.get(str(idx), {})
                    results.append({
                        'rank': i + 1,
                        'score': float(similarities[idx]),
                        'document_id': metadata.get('id', ''),
                        'title': metadata.get('title', ''),
                        'source_path': metadata.get('source_path', ''),
                        'metadata': metadata.get('metadata', {})
                    })
            
            return ProcessingResult(
                success=True,
                data=results,
                metadata={"query": query, "total_found": len(results)}
            )
            
        except Exception as e:
            log.error(f"Error searching vector index: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to search: {str(e)}"
            )
    
    def _save_index(self):
        """Save the FAISS index and metadata to disk."""
        try:
            if self.faiss_index is not None:
                import faiss
                index_file = self.index_path / "faiss_index.bin"
                faiss.write_index(self.faiss_index, str(index_file))
            
            # Save metadata
            metadata_file = self.index_path / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(self.document_metadata, f, indent=2)
            
            # Save simple vectors if using fallback
            if hasattr(self, 'vectors'):
                vectors_file = self.index_path / "vectors.pkl"
                with open(vectors_file, 'wb') as f:
                    pickle.dump(self.vectors, f)
            
            log.debug("Saved vector index and metadata")
            
        except Exception as e:
            log.error(f"Error saving vector index: {str(e)}")
    
    def get_statistics(self) -> ProcessingResult:
        """Get vector database statistics."""
        try:
            total_vectors = 0
            if self.faiss_index is not None:
                total_vectors = self.faiss_index.ntotal
            elif hasattr(self, 'vectors'):
                total_vectors = len(self.vectors)
            
            stats = {
                "total_vectors": total_vectors,
                "embedding_dimension": self.embedding_dim,
                "index_path": str(self.index_path),
                "embeddings_model": getattr(self.embeddings_model, 'model_name', 'fallback') if self.embeddings_model else 'none',
                "using_faiss": self.faiss_index is not None,
                "total_documents": len(self.document_metadata)
            }
            
            return ProcessingResult(
                success=True,
                data=stats
            )
            
        except Exception as e:
            log.error(f"Error getting vector database statistics: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get statistics: {str(e)}"
            )
    
    def clear_index(self) -> ProcessingResult:
        """Clear the vector index and metadata."""
        try:
            if self.faiss_index is not None:
                import faiss
                self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)
            
            if hasattr(self, 'vectors'):
                self.vectors = []
            
            self.document_metadata = {}
            
            # Remove saved files
            for file_path in self.index_path.glob("*"):
                file_path.unlink()
            
            log.info("Cleared vector index")
            
            return ProcessingResult(success=True, data=True)
            
        except Exception as e:
            log.error(f"Error clearing vector index: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to clear index: {str(e)}"
            )

