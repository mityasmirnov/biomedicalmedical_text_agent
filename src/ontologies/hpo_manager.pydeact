"""
Human Phenotype Ontology (HPO) manager for phenotype normalization.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from core.base import ProcessingResult
from core.logging_config import get_logger

log = get_logger(__name__)

class HPOManager:
    """Manages HPO ontology for phenotype normalization and mapping."""
    
    def __init__(self, hpo_data_path: Optional[str] = None):
        self.hpo_data_path = Path(hpo_data_path) if hpo_data_path else Path("data/ontologies/hpo")
        self.hpo_data_path.mkdir(parents=True, exist_ok=True)
        
        # HPO data structures
        self.terms = {}  # HP:ID -> term data
        self.name_to_id = {}  # term name -> HP:ID
        self.synonyms_to_id = {}  # synonym -> HP:ID
        self.parent_child = {}  # HP:ID -> list of child IDs
        self.child_parent = {}  # HP:ID -> list of parent IDs
        
        # Fuzzy matching data
        self.term_keywords = {}  # keyword -> set of HP:IDs
        
        self._load_or_create_hpo_data()
    
    def _load_or_create_hpo_data(self):
        """Load HPO data from file or create minimal dataset."""
        hpo_file = self.hpo_data_path / "hpo_terms.json"
        
        if hpo_file.exists():
            try:
                with open(hpo_file, 'r') as f:
                    data = json.load(f)
                    self.terms = data.get('terms', {})
                    self.name_to_id = data.get('name_to_id', {})
                    self.synonyms_to_id = data.get('synonyms_to_id', {})
                    self.parent_child = data.get('parent_child', {})
                    self.child_parent = data.get('child_parent', {})
                
                self._build_keyword_index()
                log.info(f"Loaded {len(self.terms)} HPO terms from {hpo_file}")
                return
                
            except Exception as e:
                log.warning(f"Error loading HPO data: {str(e)}, creating minimal dataset")
        
        # Create minimal HPO dataset for common phenotypes
        self._create_minimal_hpo_dataset()
        self._save_hpo_data()
    
    def _create_minimal_hpo_dataset(self):
        """Create a minimal HPO dataset with common phenotypes."""
        log.info("Creating minimal HPO dataset")
        
        # Common phenotypes found in medical literature
        minimal_terms = {
            "HP:0001250": {
                "name": "Seizures",
                "definition": "Seizures are episodes of abnormal motor, sensory, autonomic, or psychic activity.",
                "synonyms": ["Seizure", "Epileptic seizure", "Convulsions"],
                "parents": ["HP:0000707"],
                "children": ["HP:0002069", "HP:0011097"]
            },
            "HP:0001263": {
                "name": "Global developmental delay",
                "definition": "A delay in the achievement of motor or mental milestones in the domains of development.",
                "synonyms": ["Developmental delay", "Delayed development", "Delayed psychomotor development"],
                "parents": ["HP:0000707"],
                "children": []
            },
            "HP:0001252": {
                "name": "Muscular hypotonia",
                "definition": "Muscular hypotonia is an abnormally low muscle tone.",
                "synonyms": ["Hypotonia", "Low muscle tone", "Muscle hypotonia", "Floppy infant syndrome"],
                "parents": ["HP:0003011"],
                "children": []
            },
            "HP:0002376": {
                "name": "Developmental regression",
                "definition": "Loss of developmental milestones.",
                "synonyms": ["Regression", "Developmental deterioration", "Loss of milestones"],
                "parents": ["HP:0000707"],
                "children": []
            },
            "HP:0001508": {
                "name": "Failure to thrive",
                "definition": "Failure to thrive is a term used to describe poor weight gain and physical growth failure.",
                "synonyms": ["FTT", "Poor growth", "Growth failure"],
                "parents": ["HP:0001507"],
                "children": []
            },
            "HP:0000707": {
                "name": "Abnormality of the nervous system",
                "definition": "An abnormality of the nervous system.",
                "synonyms": ["Neurological abnormality", "Neurologic abnormality"],
                "parents": ["HP:0000118"],
                "children": ["HP:0001250", "HP:0001263", "HP:0002376"]
            },
            "HP:0003011": {
                "name": "Abnormality of the musculature",
                "definition": "An abnormality of the musculature.",
                "synonyms": ["Muscle abnormality", "Muscular abnormality"],
                "parents": ["HP:0000118"],
                "children": ["HP:0001252"]
            },
            "HP:0001507": {
                "name": "Growth abnormality",
                "definition": "An abnormality of growth or size.",
                "synonyms": ["Growth abnormality"],
                "parents": ["HP:0000118"],
                "children": ["HP:0001508"]
            },
            "HP:0000118": {
                "name": "Phenotypic abnormality",
                "definition": "A phenotypic abnormality.",
                "synonyms": ["Organ abnormality"],
                "parents": [],
                "children": ["HP:0000707", "HP:0003011", "HP:0001507"]
            },
            # Leigh syndrome specific phenotypes
            "HP:0002069": {
                "name": "Bilateral tonic-clonic seizures",
                "definition": "Bilateral tonic-clonic seizures.",
                "synonyms": ["Generalized tonic-clonic seizures", "Grand mal seizures"],
                "parents": ["HP:0001250"],
                "children": []
            },
            "HP:0011097": {
                "name": "Epileptic spasms",
                "definition": "Epileptic spasms are a type of seizure.",
                "synonyms": ["Infantile spasms", "West syndrome spasms"],
                "parents": ["HP:0001250"],
                "children": []
            },
            "HP:0001298": {
                "name": "Encephalopathy",
                "definition": "Encephalopathy is a term for any diffuse disease of the brain.",
                "synonyms": ["Brain dysfunction", "Cerebral dysfunction"],
                "parents": ["HP:0000707"],
                "children": []
            },
            "HP:0002151": {
                "name": "Increased serum lactate",
                "definition": "An abnormal increase in the level of lactate in the blood.",
                "synonyms": ["Elevated lactate", "High lactate", "Lactic acidosis"],
                "parents": ["HP:0003111"],
                "children": []
            },
            "HP:0003111": {
                "name": "Abnormality of blood and blood-forming tissues",
                "definition": "An abnormality of blood and blood-forming tissues.",
                "synonyms": ["Blood abnormality", "Hematological abnormality"],
                "parents": ["HP:0000118"],
                "children": ["HP:0002151"]
            }
        }
        
        # Build data structures
        self.terms = minimal_terms
        
        for hpo_id, term_data in minimal_terms.items():
            # Name mapping
            self.name_to_id[term_data["name"].lower()] = hpo_id
            
            # Synonym mapping
            for synonym in term_data.get("synonyms", []):
                self.synonyms_to_id[synonym.lower()] = hpo_id
            
            # Parent-child relationships
            parents = term_data.get("parents", [])
            children = term_data.get("children", [])
            
            self.child_parent[hpo_id] = parents
            self.parent_child[hpo_id] = children
        
        self._build_keyword_index()
        log.info(f"Created minimal HPO dataset with {len(self.terms)} terms")
    
    def _build_keyword_index(self):
        """Build keyword index for fuzzy matching."""
        self.term_keywords = {}
        
        for hpo_id, term_data in self.terms.items():
            # Extract keywords from name
            name_keywords = self._extract_keywords(term_data["name"])
            
            # Extract keywords from synonyms
            synonym_keywords = []
            for synonym in term_data.get("synonyms", []):
                synonym_keywords.extend(self._extract_keywords(synonym))
            
            # Add all keywords to index
            all_keywords = set(name_keywords + synonym_keywords)
            for keyword in all_keywords:
                if keyword not in self.term_keywords:
                    self.term_keywords[keyword] = set()
                self.term_keywords[keyword].add(hpo_id)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for indexing."""
        # Remove common stop words
        stop_words = {'of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'by'}
        
        # Extract words and clean them
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _save_hpo_data(self):
        """Save HPO data to file."""
        try:
            hpo_file = self.hpo_data_path / "hpo_terms.json"
            data = {
                'terms': self.terms,
                'name_to_id': self.name_to_id,
                'synonyms_to_id': self.synonyms_to_id,
                'parent_child': self.parent_child,
                'child_parent': self.child_parent
            }
            
            with open(hpo_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            log.debug(f"Saved HPO data to {hpo_file}")
            
        except Exception as e:
            log.error(f"Error saving HPO data: {str(e)}")
    
    def normalize_phenotype(self, phenotype_text: str) -> ProcessingResult[Dict[str, any]]:
        """
        Normalize a phenotype text to HPO terms.
        
        Args:
            phenotype_text: Text describing a phenotype
            
        Returns:
            ProcessingResult containing normalized HPO information
        """
        try:
            if not phenotype_text or not phenotype_text.strip():
                return ProcessingResult(
                    success=True,
                    data={"original_text": phenotype_text, "hpo_matches": []}
                )
            
            text = phenotype_text.strip().lower()
            matches = []
            
            # Exact name match
            if text in self.name_to_id:
                hpo_id = self.name_to_id[text]
                matches.append({
                    "hpo_id": hpo_id,
                    "hpo_name": self.terms[hpo_id]["name"],
                    "match_type": "exact_name",
                    "confidence": 1.0
                })
            
            # Exact synonym match
            elif text in self.synonyms_to_id:
                hpo_id = self.synonyms_to_id[text]
                matches.append({
                    "hpo_id": hpo_id,
                    "hpo_name": self.terms[hpo_id]["name"],
                    "match_type": "exact_synonym",
                    "confidence": 0.95
                })
            
            # Fuzzy keyword matching
            else:
                keyword_matches = self._fuzzy_match_keywords(text)
                matches.extend(keyword_matches)
            
            # Sort by confidence
            matches.sort(key=lambda x: x["confidence"], reverse=True)
            
            result = {
                "original_text": phenotype_text,
                "hpo_matches": matches[:5],  # Top 5 matches
                "best_match": matches[0] if matches else None
            }
            
            return ProcessingResult(
                success=True,
                data=result,
                metadata={"total_matches": len(matches)}
            )
            
        except Exception as e:
            log.error(f"Error normalizing phenotype '{phenotype_text}': {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Phenotype normalization failed: {str(e)}"
            )
    
    def _fuzzy_match_keywords(self, text: str) -> List[Dict[str, any]]:
        """Perform fuzzy matching using keywords."""
        text_keywords = set(self._extract_keywords(text))
        
        if not text_keywords:
            return []
        
        # Score HPO terms by keyword overlap
        term_scores = {}
        
        for keyword in text_keywords:
            if keyword in self.term_keywords:
                for hpo_id in self.term_keywords[keyword]:
                    if hpo_id not in term_scores:
                        term_scores[hpo_id] = 0
                    term_scores[hpo_id] += 1
        
        # Convert scores to matches
        matches = []
        for hpo_id, score in term_scores.items():
            term_data = self.terms[hpo_id]
            
            # Calculate confidence based on keyword overlap
            term_keywords = set(self._extract_keywords(term_data["name"]))
            for synonym in term_data.get("synonyms", []):
                term_keywords.update(self._extract_keywords(synonym))
            
            if term_keywords:
                confidence = len(text_keywords & term_keywords) / len(text_keywords | term_keywords)
            else:
                confidence = 0.1
            
            if confidence > 0.1:  # Minimum threshold
                matches.append({
                    "hpo_id": hpo_id,
                    "hpo_name": term_data["name"],
                    "match_type": "fuzzy_keywords",
                    "confidence": confidence,
                    "matched_keywords": list(text_keywords & term_keywords)
                })
        
        return matches
    
    def get_term_info(self, hpo_id: str) -> ProcessingResult[Dict[str, any]]:
        """Get detailed information about an HPO term."""
        try:
            if hpo_id not in self.terms:
                return ProcessingResult(
                    success=False,
                    error=f"HPO term {hpo_id} not found"
                )
            
            term_data = self.terms[hpo_id].copy()
            
            # Add parent and child information
            term_data["parent_terms"] = []
            for parent_id in self.child_parent.get(hpo_id, []):
                if parent_id in self.terms:
                    term_data["parent_terms"].append({
                        "hpo_id": parent_id,
                        "name": self.terms[parent_id]["name"]
                    })
            
            term_data["child_terms"] = []
            for child_id in self.parent_child.get(hpo_id, []):
                if child_id in self.terms:
                    term_data["child_terms"].append({
                        "hpo_id": child_id,
                        "name": self.terms[child_id]["name"]
                    })
            
            return ProcessingResult(
                success=True,
                data=term_data
            )
            
        except Exception as e:
            log.error(f"Error getting HPO term info: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get term info: {str(e)}"
            )
    
    def batch_normalize_phenotypes(self, phenotype_list: List[str]) -> ProcessingResult[List[Dict[str, any]]]:
        """Normalize multiple phenotypes at once."""
        try:
            results = []
            
            for phenotype in phenotype_list:
                result = self.normalize_phenotype(phenotype)
                if result.success:
                    results.append(result.data)
                else:
                    results.append({
                        "original_text": phenotype,
                        "hpo_matches": [],
                        "error": result.error
                    })
            
            return ProcessingResult(
                success=True,
                data=results,
                metadata={"total_processed": len(phenotype_list)}
            )
            
        except Exception as e:
            log.error(f"Error in batch phenotype normalization: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Batch normalization failed: {str(e)}"
            )
    
    def search_terms(self, query: str, limit: int = 10) -> ProcessingResult[List[Dict[str, any]]]:
        """Search HPO terms by query."""
        try:
            query_lower = query.lower()
            matches = []
            
            # Search in names and synonyms
            for hpo_id, term_data in self.terms.items():
                name = term_data["name"].lower()
                synonyms = [s.lower() for s in term_data.get("synonyms", [])]
                
                # Check for substring matches
                if query_lower in name:
                    confidence = 0.9 if query_lower == name else 0.7
                    matches.append({
                        "hpo_id": hpo_id,
                        "hpo_name": term_data["name"],
                        "match_type": "name_substring",
                        "confidence": confidence
                    })
                
                elif any(query_lower in synonym for synonym in synonyms):
                    matches.append({
                        "hpo_id": hpo_id,
                        "hpo_name": term_data["name"],
                        "match_type": "synonym_substring",
                        "confidence": 0.6
                    })
            
            # Sort by confidence and limit results
            matches.sort(key=lambda x: x["confidence"], reverse=True)
            matches = matches[:limit]
            
            return ProcessingResult(
                success=True,
                data=matches,
                metadata={"query": query, "total_found": len(matches)}
            )
            
        except Exception as e:
            log.error(f"Error searching HPO terms: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"HPO search failed: {str(e)}"
            )
    
    def get_statistics(self) -> ProcessingResult[Dict[str, any]]:
        """Get HPO manager statistics."""
        try:
            stats = {
                "total_terms": len(self.terms),
                "total_name_mappings": len(self.name_to_id),
                "total_synonym_mappings": len(self.synonyms_to_id),
                "total_keywords": len(self.term_keywords),
                "data_path": str(self.hpo_data_path)
            }
            
            return ProcessingResult(
                success=True,
                data=stats
            )
            
        except Exception as e:
            log.error(f"Error getting HPO statistics: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get statistics: {str(e)}"
            )

