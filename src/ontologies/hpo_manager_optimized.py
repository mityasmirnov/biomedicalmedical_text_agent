"""
Optimized HPO Manager for Official HPO JSON Ontology

This module provides an optimized implementation for working with the official
HPO (Human Phenotype Ontology) JSON format. It includes efficient search,
normalization, and mapping capabilities for phenotype terms.

Location: src/ontologies/hpo_manager.py
"""

import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import re
from difflib import SequenceMatcher
import pickle


@dataclass
class HPOTerm:
    """Represents an HPO term with its metadata."""
    hpo_id: str
    name: str
    definition: str
    synonyms: List[str]
    parents: List[str]
    children: List[str]
    is_obsolete: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'hpo_id': self.hpo_id,
            'name': self.name,
            'definition': self.definition,
            'synonyms': self.synonyms,
            'parents': self.parents,
            'children': self.children,
            'is_obsolete': self.is_obsolete
        }


@dataclass
class HPOMatch:
    """Represents a match between text and HPO term."""
    hpo_term: HPOTerm
    confidence: float
    match_type: str  # 'exact', 'synonym', 'partial', 'fuzzy'
    matched_text: str


class OptimizedHPOManager:
    """
    Optimized HPO Manager for working with official HPO JSON ontology.
    Provides fast search, normalization, and mapping capabilities.
    """
    
    def __init__(self, hpo_json_path: str, cache_dir: str = "data/ontologies/hpo_cache"):
        """
        Initialize HPO Manager with official HPO JSON file.
        
        Args:
            hpo_json_path: Path to the official hp.json file
            cache_dir: Directory to store processed cache files
        """
        self.hpo_json_path = Path(hpo_json_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage for HPO terms
        self.terms: Dict[str, HPOTerm] = {}
        self.name_to_id: Dict[str, str] = {}
        self.synonym_to_id: Dict[str, List[str]] = {}
        
        # Search indices
        self.word_index: Dict[str, Set[str]] = {}
        self.ngram_index: Dict[str, Set[str]] = {}
        
        # Database for fast queries
        self.db_path = self.cache_dir / "hpo.db"
        
        # Load and process HPO data
        self._load_hpo_data()
    
    def _load_hpo_data(self):
        """Load and process HPO data from JSON file."""
        cache_file = self.cache_dir / "hpo_processed.pkl"
        
        # Check if cache exists and is newer than source
        if (cache_file.exists() and 
            cache_file.stat().st_mtime > self.hpo_json_path.stat().st_mtime):
            logging.info("Loading HPO data from cache...")
            self._load_from_cache(cache_file)
        else:
            logging.info("Processing HPO JSON file...")
            self._process_hpo_json()
            self._save_to_cache(cache_file)
        
        # Initialize database
        self._init_database()
        logging.info(f"Loaded {len(self.terms)} HPO terms")
    
    def _process_hpo_json(self):
        """Process the official HPO JSON file."""
        with open(self.hpo_json_path, 'r', encoding='utf-8') as f:
            hpo_data = json.load(f)
        
        # Extract nodes from the graph structure
        graphs = hpo_data.get('graphs', [])
        if not graphs:
            raise ValueError("No graphs found in HPO JSON file")
        
        nodes = graphs[0].get('nodes', [])
        edges = graphs[0].get('edges', [])
        
        # Build relationships map
        relationships = self._build_relationships(edges)
        
        # Process each node
        for node in nodes:
            hpo_term = self._process_node(node, relationships)
            if hpo_term:
                self.terms[hpo_term.hpo_id] = hpo_term
                
                # Build search indices
                self._index_term(hpo_term)
    
    def _build_relationships(self, edges: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[str]]]:
        """Build parent-child relationships from edges."""
        relationships = {}
        
        for edge in edges:
            subject = edge.get('sub')
            object_id = edge.get('obj')
            predicate = edge.get('pred')
            
            if subject and object_id and predicate:
                # Convert to HPO ID format
                subject_id = self._extract_hpo_id(subject)
                object_hpo_id = self._extract_hpo_id(object_id)
                
                if subject_id and object_hpo_id:
                    if subject_id not in relationships:
                        relationships[subject_id] = {'parents': [], 'children': []}
                    if object_hpo_id not in relationships:
                        relationships[object_hpo_id] = {'parents': [], 'children': []}
                    
                    # is_a relationship means subject is a child of object
                    if 'is_a' in predicate or 'subClassOf' in predicate:
                        relationships[subject_id]['parents'].append(object_hpo_id)
                        relationships[object_hpo_id]['children'].append(subject_id)
        
        return relationships
    
    def _extract_hpo_id(self, uri: str) -> Optional[str]:
        """Extract HPO ID from URI."""
        if not uri:
            return None
        
        # Handle different URI formats
        if 'HP_' in uri:
            match = re.search(r'HP_(\d+)', uri)
            if match:
                return f"HP:{match.group(1)}"
        
        return None
    
    def _process_node(self, node: Dict[str, Any], relationships: Dict[str, Dict[str, List[str]]]) -> Optional[HPOTerm]:
        """Process a single node from the HPO JSON."""
        node_id = node.get('id')
        if not node_id:
            return None
        
        hpo_id = self._extract_hpo_id(node_id)
        if not hpo_id:
            return None
        
        # Extract basic properties
        meta = node.get('meta', {})
        
        # Get name (label)
        name = node.get('lbl', '')
        if not name:
            return None
        
        # Get definition
        definition = ''
        basic_props = meta.get('basicPropertyValues', [])
        for prop in basic_props:
            if 'definition' in prop.get('pred', '').lower():
                definition = prop.get('val', '')
                break
        
        # Get synonyms
        synonyms = []
        synonym_props = meta.get('synonyms', [])
        for syn in synonym_props:
            syn_val = syn.get('val')
            if syn_val and syn_val != name:
                synonyms.append(syn_val)
        
        # Check if obsolete
        is_obsolete = meta.get('deprecated', False)
        
        # Get relationships
        rel_data = relationships.get(hpo_id, {'parents': [], 'children': []})
        
        return HPOTerm(
            hpo_id=hpo_id,
            name=name,
            definition=definition,
            synonyms=synonyms,
            parents=rel_data['parents'],
            children=rel_data['children'],
            is_obsolete=is_obsolete
        )
    
    def _index_term(self, term: HPOTerm):
        """Build search indices for a term."""
        # Name index
        self.name_to_id[term.name.lower()] = term.hpo_id
        
        # Synonym index
        for synonym in term.synonyms:
            synonym_lower = synonym.lower()
            if synonym_lower not in self.synonym_to_id:
                self.synonym_to_id[synonym_lower] = []
            self.synonym_to_id[synonym_lower].append(term.hpo_id)
        
        # Word index
        all_text = [term.name] + term.synonyms
        for text in all_text:
            words = self._extract_words(text)
            for word in words:
                if word not in self.word_index:
                    self.word_index[word] = set()
                self.word_index[word].add(term.hpo_id)
        
        # N-gram index for fuzzy matching
        for text in all_text:
            ngrams = self._extract_ngrams(text, n=3)
            for ngram in ngrams:
                if ngram not in self.ngram_index:
                    self.ngram_index[ngram] = set()
                self.ngram_index[ngram].add(term.hpo_id)
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text for indexing."""
        # Remove punctuation and split
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out very short words
        return [word for word in words if len(word) > 2]
    
    def _extract_ngrams(self, text: str, n: int = 3) -> List[str]:
        """Extract n-grams from text for fuzzy matching."""
        text = text.lower()
        return [text[i:i+n] for i in range(len(text) - n + 1)]
    
    def _save_to_cache(self, cache_file: Path):
        """Save processed data to cache."""
        cache_data = {
            'terms': self.terms,
            'name_to_id': self.name_to_id,
            'synonym_to_id': self.synonym_to_id,
            'word_index': self.word_index,
            'ngram_index': self.ngram_index
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
    
    def _load_from_cache(self, cache_file: Path):
        """Load processed data from cache."""
        with open(cache_file, 'rb') as f:
            cache_data = pickle.load(f)
        
        self.terms = cache_data['terms']
        self.name_to_id = cache_data['name_to_id']
        self.synonym_to_id = cache_data['synonym_to_id']
        self.word_index = cache_data['word_index']
        self.ngram_index = cache_data['ngram_index']
    
    def _init_database(self):
        """Initialize SQLite database for fast queries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hpo_terms (
                    hpo_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    definition TEXT,
                    synonyms TEXT,
                    parents TEXT,
                    children TEXT,
                    is_obsolete BOOLEAN DEFAULT 0
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hpo_search (
                    term_text TEXT,
                    hpo_id TEXT,
                    match_type TEXT,
                    FOREIGN KEY (hpo_id) REFERENCES hpo_terms (hpo_id)
                )
            """)
            
            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hpo_name ON hpo_terms(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_text ON hpo_search(term_text)")
            
            # Clear existing data
            cursor.execute("DELETE FROM hpo_terms")
            cursor.execute("DELETE FROM hpo_search")
            
            # Insert terms
            for term in self.terms.values():
                cursor.execute("""
                    INSERT INTO hpo_terms 
                    (hpo_id, name, definition, synonyms, parents, children, is_obsolete)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    term.hpo_id,
                    term.name,
                    term.definition,
                    json.dumps(term.synonyms),
                    json.dumps(term.parents),
                    json.dumps(term.children),
                    term.is_obsolete
                ))
                
                # Insert search entries
                cursor.execute("""
                    INSERT INTO hpo_search (term_text, hpo_id, match_type)
                    VALUES (?, ?, ?)
                """, (term.name.lower(), term.hpo_id, 'name'))
                
                for synonym in term.synonyms:
                    cursor.execute("""
                        INSERT INTO hpo_search (term_text, hpo_id, match_type)
                        VALUES (?, ?, ?)
                    """, (synonym.lower(), term.hpo_id, 'synonym'))
            
            conn.commit()
    
    def search_terms(self, query: str, max_results: int = 10) -> List[HPOMatch]:
        """
        Search for HPO terms matching the query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of HPOMatch objects sorted by confidence
        """
        query_lower = query.lower().strip()
        if not query_lower:
            return []
        
        matches = []
        
        # 1. Exact name match
        if query_lower in self.name_to_id:
            hpo_id = self.name_to_id[query_lower]
            term = self.terms[hpo_id]
            matches.append(HPOMatch(
                hpo_term=term,
                confidence=1.0,
                match_type='exact',
                matched_text=term.name
            ))
        
        # 2. Exact synonym match
        if query_lower in self.synonym_to_id:
            for hpo_id in self.synonym_to_id[query_lower]:
                term = self.terms[hpo_id]
                # Find which synonym matched
                matched_synonym = next(
                    syn for syn in term.synonyms 
                    if syn.lower() == query_lower
                )
                matches.append(HPOMatch(
                    hpo_term=term,
                    confidence=0.95,
                    match_type='synonym',
                    matched_text=matched_synonym
                ))
        
        # 3. Partial matches
        partial_matches = self._find_partial_matches(query_lower)
        matches.extend(partial_matches)
        
        # 4. Fuzzy matches
        if len(matches) < max_results:
            fuzzy_matches = self._find_fuzzy_matches(query_lower, max_results - len(matches))
            matches.extend(fuzzy_matches)
        
        # Remove duplicates and sort by confidence
        seen_ids = set()
        unique_matches = []
        for match in matches:
            if match.hpo_term.hpo_id not in seen_ids:
                seen_ids.add(match.hpo_term.hpo_id)
                unique_matches.append(match)
        
        unique_matches.sort(key=lambda x: x.confidence, reverse=True)
        return unique_matches[:max_results]
    
    def _find_partial_matches(self, query: str) -> List[HPOMatch]:
        """Find partial matches using word overlap."""
        query_words = set(self._extract_words(query))
        if not query_words:
            return []
        
        candidate_ids = set()
        
        # Find terms that share words with the query
        for word in query_words:
            if word in self.word_index:
                candidate_ids.update(self.word_index[word])
        
        matches = []
        for hpo_id in candidate_ids:
            term = self.terms[hpo_id]
            
            # Calculate word overlap with name
            name_words = set(self._extract_words(term.name))
            name_overlap = len(query_words & name_words) / len(query_words | name_words)
            
            if name_overlap > 0.3:  # Threshold for partial match
                matches.append(HPOMatch(
                    hpo_term=term,
                    confidence=0.7 * name_overlap,
                    match_type='partial',
                    matched_text=term.name
                ))
            
            # Check synonyms
            for synonym in term.synonyms:
                syn_words = set(self._extract_words(synonym))
                syn_overlap = len(query_words & syn_words) / len(query_words | syn_words)
                
                if syn_overlap > 0.3:
                    matches.append(HPOMatch(
                        hpo_term=term,
                        confidence=0.65 * syn_overlap,
                        match_type='partial',
                        matched_text=synonym
                    ))
        
        return matches
    
    def _find_fuzzy_matches(self, query: str, max_results: int) -> List[HPOMatch]:
        """Find fuzzy matches using n-gram similarity."""
        query_ngrams = set(self._extract_ngrams(query))
        if not query_ngrams:
            return []
        
        candidate_scores = {}
        
        # Calculate n-gram overlap scores
        for ngram in query_ngrams:
            if ngram in self.ngram_index:
                for hpo_id in self.ngram_index[ngram]:
                    if hpo_id not in candidate_scores:
                        candidate_scores[hpo_id] = 0
                    candidate_scores[hpo_id] += 1
        
        # Convert to similarity scores and filter
        matches = []
        for hpo_id, score in candidate_scores.items():
            term = self.terms[hpo_id]
            
            # Calculate similarity with name
            name_similarity = SequenceMatcher(None, query, term.name.lower()).ratio()
            
            if name_similarity > 0.6:  # Threshold for fuzzy match
                matches.append(HPOMatch(
                    hpo_term=term,
                    confidence=0.5 * name_similarity,
                    match_type='fuzzy',
                    matched_text=term.name
                ))
        
        # Sort by confidence and return top results
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches[:max_results]
    
    def normalize_phenotype(self, phenotype_text: str) -> Optional[HPOMatch]:
        """
        Normalize a phenotype text to the best matching HPO term.
        
        Args:
            phenotype_text: Text describing a phenotype
            
        Returns:
            Best matching HPOMatch or None if no good match found
        """
        matches = self.search_terms(phenotype_text, max_results=1)
        
        if matches and matches[0].confidence > 0.7:
            return matches[0]
        
        return None
    
    def batch_normalize_phenotypes(self, phenotype_texts: List[str]) -> List[Dict[str, Any]]:
        """
        Normalize a batch of phenotype texts.
        
        Args:
            phenotype_texts: List of phenotype descriptions
            
        Returns:
            List of normalization results
        """
        results = []
        
        for text in phenotype_texts:
            result = {
                'original_text': text,
                'best_match': None,
                'all_matches': []
            }
            
            matches = self.search_terms(text, max_results=5)
            if matches:
                result['best_match'] = {
                    'hpo_id': matches[0].hpo_term.hpo_id,
                    'hpo_name': matches[0].hpo_term.name,
                    'confidence': matches[0].confidence,
                    'match_type': matches[0].match_type
                }
                
                result['all_matches'] = [
                    {
                        'hpo_id': match.hpo_term.hpo_id,
                        'hpo_name': match.hpo_term.name,
                        'confidence': match.confidence,
                        'match_type': match.match_type
                    }
                    for match in matches
                ]
            
            results.append(result)
        
        return results
    
    def get_term_by_id(self, hpo_id: str) -> Optional[HPOTerm]:
        """Get HPO term by ID."""
        return self.terms.get(hpo_id)
    
    def get_term_hierarchy(self, hpo_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get the hierarchy (parents and children) for an HPO term.
        
        Args:
            hpo_id: HPO term ID
            max_depth: Maximum depth to traverse
            
        Returns:
            Dictionary with hierarchy information
        """
        term = self.get_term_by_id(hpo_id)
        if not term:
            return {}
        
        def get_hierarchy_recursive(term_id: str, depth: int, direction: str) -> List[Dict[str, Any]]:
            if depth >= max_depth:
                return []
            
            current_term = self.get_term_by_id(term_id)
            if not current_term:
                return []
            
            related_ids = current_term.parents if direction == 'up' else current_term.children
            related_terms = []
            
            for related_id in related_ids:
                related_term = self.get_term_by_id(related_id)
                if related_term:
                    term_info = {
                        'hpo_id': related_term.hpo_id,
                        'name': related_term.name,
                        'depth': depth + 1
                    }
                    
                    # Recursively get next level
                    next_level = get_hierarchy_recursive(related_id, depth + 1, direction)
                    if next_level:
                        term_info['children' if direction == 'down' else 'parents'] = next_level
                    
                    related_terms.append(term_info)
            
            return related_terms
        
        return {
            'term': {
                'hpo_id': term.hpo_id,
                'name': term.name,
                'definition': term.definition
            },
            'parents': get_hierarchy_recursive(hpo_id, 0, 'up'),
            'children': get_hierarchy_recursive(hpo_id, 0, 'down')
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded HPO data."""
        total_terms = len(self.terms)
        obsolete_terms = sum(1 for term in self.terms.values() if term.is_obsolete)
        
        # Count terms with synonyms
        terms_with_synonyms = sum(1 for term in self.terms.values() if term.synonyms)
        
        # Count root terms (no parents)
        root_terms = sum(1 for term in self.terms.values() if not term.parents)
        
        # Count leaf terms (no children)
        leaf_terms = sum(1 for term in self.terms.values() if not term.children)
        
        return {
            'total_terms': total_terms,
            'active_terms': total_terms - obsolete_terms,
            'obsolete_terms': obsolete_terms,
            'terms_with_synonyms': terms_with_synonyms,
            'root_terms': root_terms,
            'leaf_terms': leaf_terms,
            'total_synonyms': sum(len(term.synonyms) for term in self.terms.values()),
            'indexed_words': len(self.word_index),
            'indexed_ngrams': len(self.ngram_index)
        }

