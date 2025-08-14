"""
Document Deduplicator with Content Hashing

This module provides document deduplication functionality using content hashing,
fuzzy matching, and similarity detection for biomedical literature.
"""

import hashlib
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher
import unicodedata


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate documents."""
    group_id: str
    primary_pmid: str
    duplicate_pmids: List[str]
    similarity_scores: Dict[str, float]
    duplicate_type: str  # 'exact', 'near_exact', 'similar'
    reasoning: str


@dataclass
class DeduplicationResult:
    """Result of deduplication process."""
    total_documents: int
    unique_documents: int
    duplicate_groups: List[DuplicateGroup]
    deduplication_rate: float
    statistics: Dict[str, Any]


class DocumentDeduplicator:
    """
    Document deduplicator using multiple strategies for detecting duplicates.
    """
    
    def __init__(self, 
                 similarity_threshold: float = 0.85,
                 title_threshold: float = 0.90,
                 abstract_threshold: float = 0.80):
        """
        Initialize the document deduplicator.
        
        Args:
            similarity_threshold: Overall similarity threshold for duplicates
            title_threshold: Title similarity threshold
            abstract_threshold: Abstract similarity threshold
        """
        self.similarity_threshold = similarity_threshold
        self.title_threshold = title_threshold
        self.abstract_threshold = abstract_threshold
        
        self.logger = logging.getLogger(__name__)
        
        # Compiled regex patterns for text normalization
        self.normalization_patterns = {
            'whitespace': re.compile(r'\s+'),
            'punctuation': re.compile(r'[^\w\s]'),
            'numbers': re.compile(r'\d+'),
            'special_chars': re.compile(r'[^\x00-\x7F]+')  # Non-ASCII characters
        }
    
    def normalize_text(self, text: str, aggressive: bool = False) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Input text
            aggressive: Whether to apply aggressive normalization
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        normalized = text.lower()
        
        # Remove accents and special characters
        normalized = unicodedata.normalize('NFKD', normalized)
        normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
        
        if aggressive:
            # Remove all punctuation
            normalized = self.normalization_patterns['punctuation'].sub(' ', normalized)
            # Remove numbers
            normalized = self.normalization_patterns['numbers'].sub('', normalized)
        else:
            # Keep basic punctuation, just normalize spaces
            normalized = re.sub(r'[^\w\s\-\.]', ' ', normalized)
        
        # Normalize whitespace
        normalized = self.normalization_patterns['whitespace'].sub(' ', normalized)
        
        return normalized.strip()
    
    def calculate_content_hash(self, 
                             title: str, 
                             abstract: str,
                             authors: str = "",
                             hash_type: str = "md5") -> str:
        """
        Calculate content hash for a document.
        
        Args:
            title: Document title
            abstract: Document abstract
            authors: Document authors
            hash_type: Hash algorithm ('md5', 'sha256')
            
        Returns:
            Content hash string
        """
        # Normalize content
        norm_title = self.normalize_text(title, aggressive=True)
        norm_abstract = self.normalize_text(abstract, aggressive=True)
        norm_authors = self.normalize_text(authors, aggressive=True)
        
        # Combine content
        content = f"{norm_title}|{norm_abstract}|{norm_authors}"
        
        # Calculate hash
        if hash_type == "sha256":
            hash_obj = hashlib.sha256(content.encode('utf-8'))
        else:
            hash_obj = hashlib.md5(content.encode('utf-8'))
        
        return hash_obj.hexdigest()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using sequence matching.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        norm_text1 = self.normalize_text(text1)
        norm_text2 = self.normalize_text(text2)
        
        # Calculate similarity
        matcher = SequenceMatcher(None, norm_text1, norm_text2)
        return matcher.ratio()
    
    def calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate Jaccard similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Jaccard similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # Tokenize and normalize
        words1 = set(self.normalize_text(text1).split())
        words2 = set(self.normalize_text(text2).split())
        
        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def are_documents_similar(self, 
                            doc1: Dict[str, Any], 
                            doc2: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Check if two documents are similar.
        
        Args:
            doc1: First document dictionary
            doc2: Second document dictionary
            
        Returns:
            Tuple of (is_similar, similarity_score, reasoning)
        """
        title1 = doc1.get('title', '')
        title2 = doc2.get('title', '')
        abstract1 = doc1.get('abstract', '')
        abstract2 = doc2.get('abstract', '')
        
        # Check for exact matches first
        if title1 and title2 and title1.strip() == title2.strip():
            return True, 1.0, "Exact title match"
        
        # Calculate title similarity
        title_sim = self.calculate_similarity(title1, title2)
        
        # Calculate abstract similarity
        abstract_sim = self.calculate_similarity(abstract1, abstract2)
        
        # Calculate Jaccard similarity for abstracts
        jaccard_sim = self.calculate_jaccard_similarity(abstract1, abstract2)
        
        # Combined similarity score
        if title1 and title2 and abstract1 and abstract2:
            # Weight title and abstract similarity
            combined_sim = (title_sim * 0.4 + abstract_sim * 0.4 + jaccard_sim * 0.2)
        elif title1 and title2:
            # Only title available
            combined_sim = title_sim
        elif abstract1 and abstract2:
            # Only abstract available
            combined_sim = (abstract_sim * 0.7 + jaccard_sim * 0.3)
        else:
            return False, 0.0, "Insufficient content for comparison"
        
        # Determine if similar
        is_similar = False
        reasoning = ""
        
        if combined_sim >= self.similarity_threshold:
            is_similar = True
            if combined_sim >= 0.95:
                reasoning = f"Very high similarity ({combined_sim:.3f})"
            else:
                reasoning = f"High similarity ({combined_sim:.3f})"
        elif title_sim >= self.title_threshold:
            is_similar = True
            reasoning = f"High title similarity ({title_sim:.3f})"
        elif abstract_sim >= self.abstract_threshold and jaccard_sim >= 0.7:
            is_similar = True
            reasoning = f"High abstract similarity (seq: {abstract_sim:.3f}, jaccard: {jaccard_sim:.3f})"
        else:
            reasoning = f"Low similarity (combined: {combined_sim:.3f}, title: {title_sim:.3f}, abstract: {abstract_sim:.3f})"
        
        return is_similar, combined_sim, reasoning
    
    def find_exact_duplicates(self, documents: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """
        Find exact duplicates using content hashing.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Dictionary mapping hash to list of document indices
        """
        hash_to_indices = defaultdict(list)
        
        for i, doc in enumerate(documents):
            title = doc.get('title', '')
            abstract = doc.get('abstract', '')
            authors = doc.get('authors', '')
            
            content_hash = self.calculate_content_hash(title, abstract, authors)
            hash_to_indices[content_hash].append(i)
        
        # Filter to only groups with duplicates
        duplicate_groups = {
            hash_val: indices 
            for hash_val, indices in hash_to_indices.items() 
            if len(indices) > 1
        }
        
        return duplicate_groups
    
    def find_near_duplicates(self, 
                           documents: List[Dict[str, Any]],
                           exclude_indices: Set[int] = None) -> List[Tuple[int, int, float, str]]:
        """
        Find near-duplicate documents using similarity comparison.
        
        Args:
            documents: List of document dictionaries
            exclude_indices: Set of indices to exclude from comparison
            
        Returns:
            List of tuples (index1, index2, similarity_score, reasoning)
        """
        if exclude_indices is None:
            exclude_indices = set()
        
        near_duplicates = []
        
        # Compare all pairs
        for i in range(len(documents)):
            if i in exclude_indices:
                continue
                
            for j in range(i + 1, len(documents)):
                if j in exclude_indices:
                    continue
                
                is_similar, similarity, reasoning = self.are_documents_similar(
                    documents[i], documents[j]
                )
                
                if is_similar:
                    near_duplicates.append((i, j, similarity, reasoning))
        
        return near_duplicates
    
    def create_duplicate_groups(self, 
                              documents: List[Dict[str, Any]],
                              exact_duplicates: Dict[str, List[int]],
                              near_duplicates: List[Tuple[int, int, float, str]]) -> List[DuplicateGroup]:
        """
        Create duplicate groups from exact and near duplicates.
        
        Args:
            documents: List of document dictionaries
            exact_duplicates: Exact duplicate groups
            near_duplicates: Near duplicate pairs
            
        Returns:
            List of DuplicateGroup objects
        """
        groups = []
        processed_indices = set()
        
        # Process exact duplicates first
        for group_hash, indices in exact_duplicates.items():
            if len(indices) > 1:
                # Choose primary document (prefer one with PMID, then first)
                primary_idx = indices[0]
                for idx in indices:
                    if documents[idx].get('pmid'):
                        primary_idx = idx
                        break
                
                duplicate_indices = [idx for idx in indices if idx != primary_idx]
                
                # Create similarity scores
                similarity_scores = {}
                for idx in duplicate_indices:
                    pmid = documents[idx].get('pmid', str(idx))
                    similarity_scores[pmid] = 1.0  # Exact match
                
                group = DuplicateGroup(
                    group_id=f"exact_{group_hash[:8]}",
                    primary_pmid=documents[primary_idx].get('pmid', str(primary_idx)),
                    duplicate_pmids=[documents[idx].get('pmid', str(idx)) for idx in duplicate_indices],
                    similarity_scores=similarity_scores,
                    duplicate_type='exact',
                    reasoning=f"Exact content hash match ({len(indices)} documents)"
                )
                
                groups.append(group)
                processed_indices.update(indices)
        
        # Process near duplicates
        # Group connected components
        near_duplicate_graph = defaultdict(set)
        for idx1, idx2, similarity, reasoning in near_duplicates:
            if idx1 not in processed_indices and idx2 not in processed_indices:
                near_duplicate_graph[idx1].add((idx2, similarity, reasoning))
                near_duplicate_graph[idx2].add((idx1, similarity, reasoning))
        
        # Find connected components
        visited = set()
        for start_idx in near_duplicate_graph:
            if start_idx in visited:
                continue
            
            # BFS to find connected component
            component = set()
            queue = [start_idx]
            component_similarities = {}
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                
                visited.add(current)
                component.add(current)
                
                for neighbor, similarity, reasoning in near_duplicate_graph[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)
                        component_similarities[f"{current}-{neighbor}"] = (similarity, reasoning)
            
            if len(component) > 1:
                # Choose primary document
                component_list = list(component)
                primary_idx = component_list[0]
                for idx in component_list:
                    if documents[idx].get('pmid'):
                        primary_idx = idx
                        break
                
                duplicate_indices = [idx for idx in component_list if idx != primary_idx]
                
                # Create similarity scores
                similarity_scores = {}
                reasoning_parts = []
                for idx in duplicate_indices:
                    pmid = documents[idx].get('pmid', str(idx))
                    # Find best similarity score for this document
                    best_sim = 0.0
                    for key, (sim, reason) in component_similarities.items():
                        if str(idx) in key:
                            if sim > best_sim:
                                best_sim = sim
                    similarity_scores[pmid] = best_sim
                    reasoning_parts.append(f"{pmid}: {best_sim:.3f}")
                
                group = DuplicateGroup(
                    group_id=f"near_{primary_idx}_{len(component)}",
                    primary_pmid=documents[primary_idx].get('pmid', str(primary_idx)),
                    duplicate_pmids=[documents[idx].get('pmid', str(idx)) for idx in duplicate_indices],
                    similarity_scores=similarity_scores,
                    duplicate_type='near_exact',
                    reasoning=f"Near duplicates: {'; '.join(reasoning_parts)}"
                )
                
                groups.append(group)
                processed_indices.update(component)
        
        return groups
    
    def deduplicate_documents(self, 
                            documents: List[Dict[str, Any]],
                            save_report: bool = True,
                            output_dir: str = "data/deduplication") -> DeduplicationResult:
        """
        Perform complete deduplication of documents.
        
        Args:
            documents: List of document dictionaries
            save_report: Whether to save deduplication report
            output_dir: Output directory for reports
            
        Returns:
            DeduplicationResult object
        """
        self.logger.info(f"Starting deduplication of {len(documents)} documents")
        
        if save_report:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Step 1: Find exact duplicates
        exact_duplicates = self.find_exact_duplicates(documents)
        exact_duplicate_indices = set()
        for indices in exact_duplicates.values():
            exact_duplicate_indices.update(indices)
        
        self.logger.info(f"Found {len(exact_duplicates)} exact duplicate groups")
        
        # Step 2: Find near duplicates (excluding exact duplicates)
        near_duplicates = self.find_near_duplicates(documents, exact_duplicate_indices)
        
        self.logger.info(f"Found {len(near_duplicates)} near duplicate pairs")
        
        # Step 3: Create duplicate groups
        duplicate_groups = self.create_duplicate_groups(
            documents, exact_duplicates, near_duplicates
        )
        
        # Step 4: Calculate statistics
        total_duplicates = sum(len(group.duplicate_pmids) for group in duplicate_groups)
        unique_documents = len(documents) - total_duplicates
        deduplication_rate = total_duplicates / len(documents) if len(documents) > 0 else 0
        
        # Detailed statistics
        statistics = {
            'exact_duplicate_groups': len([g for g in duplicate_groups if g.duplicate_type == 'exact']),
            'near_duplicate_groups': len([g for g in duplicate_groups if g.duplicate_type == 'near_exact']),
            'total_duplicate_documents': total_duplicates,
            'largest_duplicate_group': max(len(g.duplicate_pmids) for g in duplicate_groups) if duplicate_groups else 0,
            'average_group_size': sum(len(g.duplicate_pmids) for g in duplicate_groups) / len(duplicate_groups) if duplicate_groups else 0,
            'similarity_distribution': self._calculate_similarity_distribution(duplicate_groups)
        }
        
        result = DeduplicationResult(
            total_documents=len(documents),
            unique_documents=unique_documents,
            duplicate_groups=duplicate_groups,
            deduplication_rate=deduplication_rate,
            statistics=statistics
        )
        
        # Save report
        if save_report:
            self._save_deduplication_report(result, documents, output_dir)
        
        self.logger.info(f"Deduplication completed: {unique_documents}/{len(documents)} unique documents")
        
        return result
    
    def _calculate_similarity_distribution(self, groups: List[DuplicateGroup]) -> Dict[str, int]:
        """Calculate distribution of similarity scores."""
        distribution = {
            '0.95-1.00': 0,
            '0.90-0.95': 0,
            '0.85-0.90': 0,
            '0.80-0.85': 0,
            'below_0.80': 0
        }
        
        for group in groups:
            for similarity in group.similarity_scores.values():
                if similarity >= 0.95:
                    distribution['0.95-1.00'] += 1
                elif similarity >= 0.90:
                    distribution['0.90-0.95'] += 1
                elif similarity >= 0.85:
                    distribution['0.85-0.90'] += 1
                elif similarity >= 0.80:
                    distribution['0.80-0.85'] += 1
                else:
                    distribution['below_0.80'] += 1
        
        return distribution
    
    def _save_deduplication_report(self, 
                                 result: DeduplicationResult,
                                 documents: List[Dict[str, Any]],
                                 output_dir: str) -> None:
        """Save detailed deduplication report."""
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        
        # Save summary report
        summary_path = Path(output_dir) / f"deduplication_summary_{timestamp}.json"
        summary_data = {
            'total_documents': result.total_documents,
            'unique_documents': result.unique_documents,
            'duplicate_groups_count': len(result.duplicate_groups),
            'deduplication_rate': result.deduplication_rate,
            'statistics': result.statistics
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        # Save detailed duplicate groups
        groups_path = Path(output_dir) / f"duplicate_groups_{timestamp}.csv"
        groups_data = []
        
        for group in result.duplicate_groups:
            for duplicate_pmid in group.duplicate_pmids:
                groups_data.append({
                    'GroupID': group.group_id,
                    'PrimaryPMID': group.primary_pmid,
                    'DuplicatePMID': duplicate_pmid,
                    'SimilarityScore': group.similarity_scores.get(duplicate_pmid, 0.0),
                    'DuplicateType': group.duplicate_type,
                    'Reasoning': group.reasoning
                })
        
        if groups_data:
            groups_df = pd.DataFrame(groups_data)
            groups_df.to_csv(groups_path, index=False)
        
        # Save unique documents list
        unique_path = Path(output_dir) / f"unique_documents_{timestamp}.csv"
        
        # Identify unique documents
        all_duplicate_pmids = set()
        for group in result.duplicate_groups:
            all_duplicate_pmids.update(group.duplicate_pmids)
        
        unique_docs = []
        for doc in documents:
            pmid = doc.get('pmid', '')
            if pmid not in all_duplicate_pmids:
                unique_docs.append({
                    'PMID': pmid,
                    'Title': doc.get('title', ''),
                    'Journal': doc.get('journal', ''),
                    'PubDate': doc.get('pub_date', ''),
                    'HasAbstract': bool(doc.get('abstract', ''))
                })
        
        unique_df = pd.DataFrame(unique_docs)
        unique_df.to_csv(unique_path, index=False)
        
        self.logger.info(f"Saved deduplication reports to {output_dir}")
    
    def get_unique_documents(self, 
                           documents: List[Dict[str, Any]],
                           deduplication_result: DeduplicationResult) -> List[Dict[str, Any]]:
        """
        Get list of unique documents after deduplication.
        
        Args:
            documents: Original document list
            deduplication_result: Result from deduplication
            
        Returns:
            List of unique documents
        """
        # Collect all duplicate PMIDs
        duplicate_pmids = set()
        for group in deduplication_result.duplicate_groups:
            duplicate_pmids.update(group.duplicate_pmids)
        
        # Filter unique documents
        unique_documents = []
        for doc in documents:
            pmid = doc.get('pmid', '')
            if pmid not in duplicate_pmids:
                unique_documents.append(doc)
        
        return unique_documents


# Utility functions

def deduplicate_leigh_syndrome_articles(documents: List[Dict[str, Any]],
                                       output_dir: str = "data/deduplication") -> DeduplicationResult:
    """
    Deduplicate Leigh syndrome articles.
    
    Args:
        documents: List of document dictionaries
        output_dir: Output directory for reports
        
    Returns:
        DeduplicationResult object
    """
    deduplicator = DocumentDeduplicator(
        similarity_threshold=0.85,
        title_threshold=0.90,
        abstract_threshold=0.80
    )
    
    result = deduplicator.deduplicate_documents(
        documents,
        save_report=True,
        output_dir=output_dir
    )
    
    print(f"Deduplication Results:")
    print(f"Total documents: {result.total_documents}")
    print(f"Unique documents: {result.unique_documents}")
    print(f"Duplicate groups: {len(result.duplicate_groups)}")
    print(f"Deduplication rate: {result.deduplication_rate:.2%}")
    
    return result

