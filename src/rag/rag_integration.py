"""
RAG Integration System for Biomedical Text Agent

This module implements RAG (Retrieval-Augmented Generation) integration
that stores examples and rules in vector storage and retrieves relevant
context before LLM calls to improve extraction accuracy.

Location: src/rag/rag_integration.py
"""

import json
import logging
import sqlite3
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RAGExample:
    """Represents a successful extraction example for RAG."""
    example_id: str
    text: str
    extracted_data: Dict[str, Any]
    field_type: str
    confidence: float
    source: str
    created_at: str
    usage_count: int = 0
    success_rate: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RAGRule:
    """Represents an extraction rule learned from errors."""
    rule_id: str
    rule_text: str
    field_name: str
    error_pattern: str
    correction: str
    success_rate: float
    created_at: str
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RAGContext:
    """Context retrieved from RAG system."""
    examples: List[RAGExample]
    rules: List[RAGRule]
    similarity_scores: List[float]
    total_retrieved: int


class VectorStore:
    """Vector storage system for RAG examples and rules."""
    
    def __init__(self, storage_path: str, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector store.
        
        Args:
            storage_path: Path to store vector indices
            embedding_model: Name of the sentence transformer model
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(embedding_model)
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                self.use_sentence_transformers = True
                logging.info(f"Using SentenceTransformer: {embedding_model}")
            except Exception as e:
                logging.warning(f"Failed to load SentenceTransformer: {e}")
                self.use_sentence_transformers = False
        else:
            self.use_sentence_transformers = False
        
        # Fallback to TF-IDF if sentence transformers not available
        if not self.use_sentence_transformers:
            self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.embedding_dim = 1000
            logging.info("Using TF-IDF vectorizer as fallback")
        
        # Initialize FAISS indices
        self.examples_index = None
        self.rules_index = None
        
        # Storage for metadata
        self.examples_metadata = []
        self.rules_metadata = []
        
        # Load existing indices
        self._load_indices()
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for texts."""
        if self.use_sentence_transformers:
            return self.embedding_model.encode(texts)
        else:
            # Use TF-IDF as fallback
            if hasattr(self, '_tfidf_fitted') and self._tfidf_fitted:
                return self.tfidf_vectorizer.transform(texts).toarray()
            else:
                # Fit on the texts if not fitted yet
                embeddings = self.tfidf_vectorizer.fit_transform(texts).toarray()
                self._tfidf_fitted = True
                return embeddings
    
    def _load_indices(self):
        """Load existing FAISS indices and metadata."""
        examples_index_path = self.storage_path / "examples.index"
        rules_index_path = self.storage_path / "rules.index"
        examples_meta_path = self.storage_path / "examples_metadata.pkl"
        rules_meta_path = self.storage_path / "rules_metadata.pkl"
        
        # Load examples
        if examples_index_path.exists() and examples_meta_path.exists():
            try:
                if FAISS_AVAILABLE:
                    self.examples_index = faiss.read_index(str(examples_index_path))
                with open(examples_meta_path, 'rb') as f:
                    self.examples_metadata = pickle.load(f)
                logging.info(f"Loaded {len(self.examples_metadata)} examples")
            except Exception as e:
                logging.warning(f"Failed to load examples index: {e}")
        
        # Load rules
        if rules_index_path.exists() and rules_meta_path.exists():
            try:
                if FAISS_AVAILABLE:
                    self.rules_index = faiss.read_index(str(rules_index_path))
                with open(rules_meta_path, 'rb') as f:
                    self.rules_metadata = pickle.load(f)
                logging.info(f"Loaded {len(self.rules_metadata)} rules")
            except Exception as e:
                logging.warning(f"Failed to load rules index: {e}")
    
    def _save_indices(self):
        """Save FAISS indices and metadata."""
        try:
            # Save examples
            if self.examples_index is not None and FAISS_AVAILABLE:
                faiss.write_index(self.examples_index, str(self.storage_path / "examples.index"))
            
            with open(self.storage_path / "examples_metadata.pkl", 'wb') as f:
                pickle.dump(self.examples_metadata, f)
            
            # Save rules
            if self.rules_index is not None and FAISS_AVAILABLE:
                faiss.write_index(self.rules_index, str(self.storage_path / "rules.index"))
            
            with open(self.storage_path / "rules_metadata.pkl", 'wb') as f:
                pickle.dump(self.rules_metadata, f)
                
        except Exception as e:
            logging.error(f"Failed to save indices: {e}")
    
    def add_example(self, example: RAGExample):
        """Add an example to the vector store."""
        try:
            # Get embedding for the text
            embedding = self._get_embeddings([example.text])[0]
            
            # Initialize or update examples index
            if self.examples_index is None and FAISS_AVAILABLE:
                self.examples_index = faiss.IndexFlatIP(self.embedding_dim)
            
            # Add to index
            if FAISS_AVAILABLE and self.examples_index is not None:
                self.examples_index.add(embedding.reshape(1, -1).astype('float32'))
            
            # Add metadata
            self.examples_metadata.append(example)
            
            # Save indices
            self._save_indices()
            
            logging.debug(f"Added example: {example.example_id}")
            
        except Exception as e:
            logging.error(f"Failed to add example: {e}")
    
    def add_rule(self, rule: RAGRule):
        """Add a rule to the vector store."""
        try:
            # Get embedding for the rule text
            embedding = self._get_embeddings([rule.rule_text])[0]
            
            # Initialize or update rules index
            if self.rules_index is None and FAISS_AVAILABLE:
                self.rules_index = faiss.IndexFlatIP(self.embedding_dim)
            
            # Add to index
            if FAISS_AVAILABLE and self.rules_index is not None:
                self.rules_index.add(embedding.reshape(1, -1).astype('float32'))
            
            # Add metadata
            self.rules_metadata.append(rule)
            
            # Save indices
            self._save_indices()
            
            logging.debug(f"Added rule: {rule.rule_id}")
            
        except Exception as e:
            logging.error(f"Failed to add rule: {e}")
    
    def search_examples(self, query: str, field_type: str = None, k: int = 5) -> List[Tuple[RAGExample, float]]:
        """Search for similar examples."""
        if not self.examples_metadata:
            return []
        
        try:
            # Get query embedding
            query_embedding = self._get_embeddings([query])[0]
            
            if FAISS_AVAILABLE and self.examples_index is not None:
                # Use FAISS for search
                scores, indices = self.examples_index.search(
                    query_embedding.reshape(1, -1).astype('float32'), 
                    min(k * 2, len(self.examples_metadata))  # Get more candidates
                )
                
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(self.examples_metadata):
                        example = self.examples_metadata[idx]
                        # Filter by field type if specified
                        if field_type is None or example.field_type == field_type:
                            results.append((example, float(score)))
                
                # Sort by score and return top k
                results.sort(key=lambda x: x[1], reverse=True)
                return results[:k]
            
            else:
                # Fallback: compute similarities manually
                all_texts = [ex.text for ex in self.examples_metadata]
                all_embeddings = self._get_embeddings(all_texts)
                
                similarities = cosine_similarity(
                    query_embedding.reshape(1, -1), 
                    all_embeddings
                )[0]
                
                # Get top candidates
                top_indices = np.argsort(similarities)[::-1][:k*2]
                
                results = []
                for idx in top_indices:
                    example = self.examples_metadata[idx]
                    if field_type is None or example.field_type == field_type:
                        results.append((example, similarities[idx]))
                
                return results[:k]
                
        except Exception as e:
            logging.error(f"Failed to search examples: {e}")
            return []
    
    def search_rules(self, query: str, field_name: str = None, k: int = 3) -> List[Tuple[RAGRule, float]]:
        """Search for similar rules."""
        if not self.rules_metadata:
            return []
        
        try:
            # Get query embedding
            query_embedding = self._get_embeddings([query])[0]
            
            if FAISS_AVAILABLE and self.rules_index is not None:
                # Use FAISS for search
                scores, indices = self.rules_index.search(
                    query_embedding.reshape(1, -1).astype('float32'), 
                    min(k * 2, len(self.rules_metadata))
                )
                
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(self.rules_metadata):
                        rule = self.rules_metadata[idx]
                        # Filter by field name if specified
                        if field_name is None or rule.field_name == field_name:
                            results.append((rule, float(score)))
                
                # Sort by score and return top k
                results.sort(key=lambda x: x[1], reverse=True)
                return results[:k]
            
            else:
                # Fallback: compute similarities manually
                all_texts = [rule.rule_text for rule in self.rules_metadata]
                all_embeddings = self._get_embeddings(all_texts)
                
                similarities = cosine_similarity(
                    query_embedding.reshape(1, -1), 
                    all_embeddings
                )[0]
                
                # Get top candidates
                top_indices = np.argsort(similarities)[::-1][:k*2]
                
                results = []
                for idx in top_indices:
                    rule = self.rules_metadata[idx]
                    if field_name is None or rule.field_name == field_name:
                        results.append((rule, similarities[idx]))
                
                return results[:k]
                
        except Exception as e:
            logging.error(f"Failed to search rules: {e}")
            return []


class RAGIntegration:
    """Main RAG integration system."""
    
    def __init__(self, storage_path: str = "data/rag"):
        """
        Initialize RAG integration.
        
        Args:
            storage_path: Path to store RAG data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize vector store
        self.vector_store = VectorStore(str(self.storage_path / "vectors"))
        
        # Initialize database for structured storage
        self.db_path = self.storage_path / "rag.db"
        self._init_database()
        
        logging.info("RAG integration initialized")
    
    def _init_database(self):
        """Initialize SQLite database for RAG data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Examples table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_examples (
                    example_id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    extracted_data TEXT NOT NULL,
                    field_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    source TEXT,
                    created_at TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 1.0
                )
            """)
            
            # Rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_rules (
                    rule_id TEXT PRIMARY KEY,
                    rule_text TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    error_pattern TEXT,
                    correction TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.5,
                    created_at TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0
                )
            """)
            
            # Usage tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    query TEXT,
                    similarity_score REAL,
                    used_at TEXT NOT NULL
                )
            """)
            
            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_examples_field ON rag_examples(field_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_field ON rag_rules(field_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_item ON rag_usage(item_id, item_type)")
            
            conn.commit()
    
    def add_example(self, example: RAGExample):
        """Add a successful extraction example."""
        # Add to vector store
        self.vector_store.add_example(example)
        
        # Add to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO rag_examples 
                (example_id, text, extracted_data, field_type, confidence, source, created_at, usage_count, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                example.example_id,
                example.text,
                json.dumps(example.extracted_data),
                example.field_type,
                example.confidence,
                example.source,
                example.created_at,
                example.usage_count,
                example.success_rate
            ))
            conn.commit()
    
    def add_rule(self, rule: RAGRule):
        """Add an extraction rule."""
        # Add to vector store
        self.vector_store.add_rule(rule)
        
        # Add to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO rag_rules 
                (rule_id, rule_text, field_name, error_pattern, correction, success_rate, created_at, usage_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.rule_id,
                rule.rule_text,
                rule.field_name,
                rule.error_pattern,
                rule.correction,
                rule.success_rate,
                rule.created_at,
                rule.usage_count
            ))
            conn.commit()
    
    def get_context(self, query: str, field_type: str = None, max_examples: int = 3, max_rules: int = 2) -> RAGContext:
        """
        Get relevant context for a query.
        
        Args:
            query: Query text
            field_type: Field type to filter examples
            max_examples: Maximum number of examples to retrieve
            max_rules: Maximum number of rules to retrieve
            
        Returns:
            RAGContext with relevant examples and rules
        """
        # Search for examples
        example_results = self.vector_store.search_examples(query, field_type, max_examples)
        examples = [ex for ex, score in example_results]
        example_scores = [score for ex, score in example_results]
        
        # Search for rules
        rule_results = self.vector_store.search_rules(query, field_type, max_rules)
        rules = [rule for rule, score in rule_results]
        rule_scores = [score for rule, score in rule_results]
        
        # Update usage counts
        self._update_usage_counts(examples, rules, query)
        
        return RAGContext(
            examples=examples,
            rules=rules,
            similarity_scores=example_scores + rule_scores,
            total_retrieved=len(examples) + len(rules)
        )
    
    def enhance_prompt(self, base_prompt: str, query: str, field_type: str = None) -> str:
        """
        Enhance a prompt with RAG context.
        
        Args:
            base_prompt: Base prompt to enhance
            query: Query text for context retrieval
            field_type: Field type for filtering
            
        Returns:
            Enhanced prompt with RAG context
        """
        context = self.get_context(query, field_type)
        
        if not context.examples and not context.rules:
            return base_prompt
        
        enhancement = "\n\nRelevant context from previous extractions:\n"
        
        # Add examples
        if context.examples:
            enhancement += "\nSuccessful examples:\n"
            for i, example in enumerate(context.examples, 1):
                enhancement += f"\nExample {i}:\n"
                enhancement += f"Text: {example.text[:200]}...\n"
                enhancement += f"Extracted: {json.dumps(example.extracted_data, indent=2)}\n"
        
        # Add rules
        if context.rules:
            enhancement += "\nExtraction rules to follow:\n"
            for i, rule in enumerate(context.rules, 1):
                enhancement += f"\nRule {i}: {rule.rule_text}\n"
                if rule.correction:
                    enhancement += f"Correction guidance: {rule.correction}\n"
        
        enhancement += "\nUse this context to improve your extraction accuracy.\n"
        
        return base_prompt + enhancement
    
    def _update_usage_counts(self, examples: List[RAGExample], rules: List[RAGRule], query: str):
        """Update usage counts for retrieved items."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update examples
            for example in examples:
                cursor.execute("""
                    UPDATE rag_examples 
                    SET usage_count = usage_count + 1 
                    WHERE example_id = ?
                """, (example.example_id,))
                
                cursor.execute("""
                    INSERT INTO rag_usage (item_id, item_type, query, used_at)
                    VALUES (?, ?, ?, ?)
                """, (example.example_id, 'example', query, datetime.now().isoformat()))
            
            # Update rules
            for rule in rules:
                cursor.execute("""
                    UPDATE rag_rules 
                    SET usage_count = usage_count + 1 
                    WHERE rule_id = ?
                """, (rule.rule_id,))
                
                cursor.execute("""
                    INSERT INTO rag_usage (item_id, item_type, query, used_at)
                    VALUES (?, ?, ?, ?)
                """, (rule.rule_id, 'rule', query, datetime.now().isoformat()))
            
            conn.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count examples by field type
            cursor.execute("""
                SELECT field_type, COUNT(*), AVG(confidence), AVG(success_rate)
                FROM rag_examples 
                GROUP BY field_type
            """)
            
            example_stats = {}
            for field_type, count, avg_confidence, avg_success in cursor.fetchall():
                example_stats[field_type] = {
                    'count': count,
                    'avg_confidence': avg_confidence or 0.0,
                    'avg_success_rate': avg_success or 0.0
                }
            
            # Count rules by field name
            cursor.execute("""
                SELECT field_name, COUNT(*), AVG(success_rate)
                FROM rag_rules 
                GROUP BY field_name
            """)
            
            rule_stats = {}
            for field_name, count, avg_success in cursor.fetchall():
                rule_stats[field_name] = {
                    'count': count,
                    'avg_success_rate': avg_success or 0.0
                }
            
            # Overall statistics
            cursor.execute("SELECT COUNT(*) FROM rag_examples")
            total_examples = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM rag_rules")
            total_rules = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM rag_usage")
            total_usage = cursor.fetchone()[0]
            
            return {
                'total_examples': total_examples,
                'total_rules': total_rules,
                'total_usage': total_usage,
                'example_stats': example_stats,
                'rule_stats': rule_stats
            }


# Utility functions for creating RAG items

def create_example_from_success(text: str, 
                               extracted_data: Dict[str, Any], 
                               field_type: str,
                               confidence: float = 0.8,
                               source: str = "extraction") -> RAGExample:
    """Create a RAG example from successful extraction."""
    example_id = f"{field_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    return RAGExample(
        example_id=example_id,
        text=text,
        extracted_data=extracted_data,
        field_type=field_type,
        confidence=confidence,
        source=source,
        created_at=datetime.now().isoformat()
    )


def create_rule_from_error(error_info: Dict[str, Any]) -> RAGRule:
    """Create a RAG rule from error analysis."""
    rule_id = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    return RAGRule(
        rule_id=rule_id,
        rule_text=error_info.get('rule_text', ''),
        field_name=error_info.get('field_name', ''),
        error_pattern=error_info.get('error_pattern', ''),
        correction=error_info.get('correction', ''),
        success_rate=error_info.get('success_rate', 0.5),
        created_at=datetime.now().isoformat()
    )

