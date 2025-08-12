"""
Gene normalization manager using HGNC standards.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from core.base import ProcessingResult
from core.logging_config import get_logger

log = get_logger(__name__)

class GeneManager:
    """Manages gene symbol normalization using HGNC standards."""
    
    def __init__(self, gene_data_path: Optional[str] = None):
        self.gene_data_path = Path(gene_data_path) if gene_data_path else Path("data/ontologies/genes")
        self.gene_data_path.mkdir(parents=True, exist_ok=True)
        
        # Gene data structures
        self.genes = {}  # HGNC symbol -> gene data
        self.symbol_to_hgnc = {}  # various symbols -> official HGNC symbol
        self.alias_to_hgnc = {}  # aliases -> official HGNC symbol
        self.prev_symbols_to_hgnc = {}  # previous symbols -> official HGNC symbol
        
        self._load_or_create_gene_data()
    
    def _load_or_create_gene_data(self):
        """Load gene data from file or create minimal dataset."""
        gene_file = self.gene_data_path / "hgnc_genes.json"
        
        if gene_file.exists():
            try:
                with open(gene_file, 'r') as f:
                    data = json.load(f)
                    self.genes = data.get('genes', {})
                    self.symbol_to_hgnc = data.get('symbol_to_hgnc', {})
                    self.alias_to_hgnc = data.get('alias_to_hgnc', {})
                    self.prev_symbols_to_hgnc = data.get('prev_symbols_to_hgnc', {})
                
                log.info(f"Loaded {len(self.genes)} genes from {gene_file}")
                return
                
            except Exception as e:
                log.warning(f"Error loading gene data: {str(e)}, creating minimal dataset")
        
        # Create minimal gene dataset for common genes
        self._create_minimal_gene_dataset()
        self._save_gene_data()
    
    def _create_minimal_gene_dataset(self):
        """Create a minimal gene dataset with common genes."""
        log.info("Creating minimal gene dataset")
        
        # Common genes found in medical literature, especially mitochondrial diseases
        minimal_genes = {
            "SURF1": {
                "hgnc_id": "HGNC:11474",
                "symbol": "SURF1",
                "name": "surfeit locus protein 1",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "9q34.2",
                "aliases": ["SHY1"],
                "prev_symbols": [],
                "gene_family": ["Surfeit gene cluster"],
                "ensembl_gene_id": "ENSG00000148290",
                "entrez_id": "6834",
                "omim_id": "185620"
            },
            "NDUFS1": {
                "hgnc_id": "HGNC:7707",
                "symbol": "NDUFS1",
                "name": "NADH:ubiquinone oxidoreductase core subunit S1",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "2q33.3",
                "aliases": ["CI-75kD", "NADH-UQ-Fe-S-protein-1"],
                "prev_symbols": [],
                "gene_family": ["NADH:ubiquinone oxidoreductase subunits"],
                "ensembl_gene_id": "ENSG00000023228",
                "entrez_id": "4719",
                "omim_id": "157655"
            },
            "COX15": {
                "hgnc_id": "HGNC:2267",
                "symbol": "COX15",
                "name": "cytochrome c oxidase assembly homolog 15",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "10q24.2",
                "aliases": ["CEMCOX2"],
                "prev_symbols": [],
                "gene_family": ["Cytochrome c oxidase assembly factors"],
                "ensembl_gene_id": "ENSG00000103689",
                "entrez_id": "1355",
                "omim_id": "603646"
            },
            "PDHA1": {
                "hgnc_id": "HGNC:8806",
                "symbol": "PDHA1",
                "name": "pyruvate dehydrogenase E1 subunit alpha 1",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "Xp22.12",
                "aliases": ["PHE1A", "PDHA"],
                "prev_symbols": [],
                "gene_family": ["Pyruvate dehydrogenase complex"],
                "ensembl_gene_id": "ENSG00000131828",
                "entrez_id": "5160",
                "omim_id": "300502"
            },
            "PDHB": {
                "hgnc_id": "HGNC:8807",
                "symbol": "PDHB",
                "name": "pyruvate dehydrogenase E1 subunit beta",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "3p21.1-p14.2",
                "aliases": ["PHE1B"],
                "prev_symbols": [],
                "gene_family": ["Pyruvate dehydrogenase complex"],
                "ensembl_gene_id": "ENSG00000168291",
                "entrez_id": "5162",
                "omim_id": "179060"
            },
            "NDUFS4": {
                "hgnc_id": "HGNC:7711",
                "symbol": "NDUFS4",
                "name": "NADH:ubiquinone oxidoreductase subunit S4",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "5q11.1",
                "aliases": ["CI-18kD", "AQDQ"],
                "prev_symbols": [],
                "gene_family": ["NADH:ubiquinone oxidoreductase subunits"],
                "ensembl_gene_id": "ENSG00000164258",
                "entrez_id": "4724",
                "omim_id": "602694"
            },
            "NDUFS8": {
                "hgnc_id": "HGNC:7715",
                "symbol": "NDUFS8",
                "name": "NADH:ubiquinone oxidoreductase core subunit S8",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "11q13.2",
                "aliases": ["CI-23kD"],
                "prev_symbols": [],
                "gene_family": ["NADH:ubiquinone oxidoreductase subunits"],
                "ensembl_gene_id": "ENSG00000110717",
                "entrez_id": "4728",
                "omim_id": "602141"
            },
            "MT-ATP6": {
                "hgnc_id": "HGNC:7414",
                "symbol": "MT-ATP6",
                "name": "mitochondrially encoded ATP synthase membrane subunit 6",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "mitochondria",
                "aliases": ["ATP6", "MTATP6"],
                "prev_symbols": ["ATP6"],
                "gene_family": ["Mitochondrial complex V subunits"],
                "ensembl_gene_id": "ENSG00000198899",
                "entrez_id": "4508",
                "omim_id": "516060"
            },
            "BRCA1": {
                "hgnc_id": "HGNC:1100",
                "symbol": "BRCA1",
                "name": "BRCA1 DNA repair associated",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "17q21.31",
                "aliases": ["BRCAI", "BRCC1", "FANCS", "IRIS", "PNCA4", "PPP1R53", "PSCP", "RNF53"],
                "prev_symbols": [],
                "gene_family": ["BRCA1 A complex", "RING-type E3 ubiquitin transferases"],
                "ensembl_gene_id": "ENSG00000012048",
                "entrez_id": "672",
                "omim_id": "113705"
            },
            "BRCA2": {
                "hgnc_id": "HGNC:1101",
                "symbol": "BRCA2",
                "name": "BRCA2 DNA repair associated",
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product",
                "status": "Approved",
                "location": "13q13.1",
                "aliases": ["FANCD1", "GLM3", "PNCA2"],
                "prev_symbols": [],
                "gene_family": ["Fanconi anemia complementation groups"],
                "ensembl_gene_id": "ENSG00000139618",
                "entrez_id": "675",
                "omim_id": "600185"
            }
        }
        
        # Build data structures
        self.genes = minimal_genes
        
        for symbol, gene_data in minimal_genes.items():
            # Official symbol mapping
            self.symbol_to_hgnc[symbol] = symbol
            self.symbol_to_hgnc[symbol.lower()] = symbol
            
            # Alias mappings
            for alias in gene_data.get("aliases", []):
                self.alias_to_hgnc[alias] = symbol
                self.alias_to_hgnc[alias.lower()] = symbol
            
            # Previous symbol mappings
            for prev_symbol in gene_data.get("prev_symbols", []):
                self.prev_symbols_to_hgnc[prev_symbol] = symbol
                self.prev_symbols_to_hgnc[prev_symbol.lower()] = symbol
        
        log.info(f"Created minimal gene dataset with {len(self.genes)} genes")
    
    def _save_gene_data(self):
        """Save gene data to file."""
        try:
            gene_file = self.gene_data_path / "hgnc_genes.json"
            data = {
                'genes': self.genes,
                'symbol_to_hgnc': self.symbol_to_hgnc,
                'alias_to_hgnc': self.alias_to_hgnc,
                'prev_symbols_to_hgnc': self.prev_symbols_to_hgnc
            }
            
            with open(gene_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            log.debug(f"Saved gene data to {gene_file}")
            
        except Exception as e:
            log.error(f"Error saving gene data: {str(e)}")
    
    def normalize_gene_symbol(self, gene_symbol: str) -> ProcessingResult[Dict[str, any]]:
        """
        Normalize a gene symbol to official HGNC symbol.
        
        Args:
            gene_symbol: Gene symbol to normalize
            
        Returns:
            ProcessingResult containing normalized gene information
        """
        try:
            if not gene_symbol or not gene_symbol.strip():
                return ProcessingResult(
                    success=True,
                    data={"original_symbol": gene_symbol, "normalized_symbol": None, "match_type": None}
                )
            
            symbol = gene_symbol.strip()
            original_symbol = symbol
            
            # Try exact match first (case-sensitive)
            if symbol in self.symbol_to_hgnc:
                normalized = self.symbol_to_hgnc[symbol]
                match_type = "exact_symbol"
                confidence = 1.0
            
            # Try case-insensitive match
            elif symbol.lower() in self.symbol_to_hgnc:
                normalized = self.symbol_to_hgnc[symbol.lower()]
                match_type = "case_insensitive_symbol"
                confidence = 0.95
            
            # Try alias match
            elif symbol in self.alias_to_hgnc:
                normalized = self.alias_to_hgnc[symbol]
                match_type = "alias"
                confidence = 0.9
            elif symbol.lower() in self.alias_to_hgnc:
                normalized = self.alias_to_hgnc[symbol.lower()]
                match_type = "case_insensitive_alias"
                confidence = 0.85
            
            # Try previous symbol match
            elif symbol in self.prev_symbols_to_hgnc:
                normalized = self.prev_symbols_to_hgnc[symbol]
                match_type = "previous_symbol"
                confidence = 0.8
            elif symbol.lower() in self.prev_symbols_to_hgnc:
                normalized = self.prev_symbols_to_hgnc[symbol.lower()]
                match_type = "case_insensitive_previous"
                confidence = 0.75
            
            # Try fuzzy matching
            else:
                fuzzy_result = self._fuzzy_match_gene(symbol)
                if fuzzy_result:
                    normalized = fuzzy_result["symbol"]
                    match_type = "fuzzy_match"
                    confidence = fuzzy_result["confidence"]
                else:
                    # No match found
                    result = {
                        "original_symbol": original_symbol,
                        "normalized_symbol": None,
                        "match_type": None,
                        "confidence": 0.0,
                        "gene_info": None
                    }
                    
                    return ProcessingResult(
                        success=True,
                        data=result,
                        warnings=[f"No match found for gene symbol: {original_symbol}"]
                    )
            
            # Get gene information
            gene_info = self.genes.get(normalized, {})
            
            result = {
                "original_symbol": original_symbol,
                "normalized_symbol": normalized,
                "match_type": match_type,
                "confidence": confidence,
                "gene_info": gene_info
            }
            
            return ProcessingResult(
                success=True,
                data=result
            )
            
        except Exception as e:
            log.error(f"Error normalizing gene symbol '{gene_symbol}': {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Gene normalization failed: {str(e)}"
            )
    
    def _fuzzy_match_gene(self, symbol: str) -> Optional[Dict[str, any]]:
        """Perform fuzzy matching for gene symbols."""
        symbol_upper = symbol.upper()
        
        # Check for partial matches in official symbols
        for official_symbol in self.genes.keys():
            # Check if the input is a substring of an official symbol
            if symbol_upper in official_symbol:
                return {"symbol": official_symbol, "confidence": 0.6}
            
            # Check if an official symbol is a substring of the input
            if official_symbol in symbol_upper:
                return {"symbol": official_symbol, "confidence": 0.5}
        
        # Check for similar symbols (edit distance)
        best_match = None
        best_score = 0
        
        for official_symbol in self.genes.keys():
            score = self._calculate_similarity(symbol_upper, official_symbol)
            if score > best_score and score > 0.7:  # Minimum similarity threshold
                best_match = official_symbol
                best_score = score
        
        if best_match:
            return {"symbol": best_match, "confidence": best_score * 0.4}  # Reduce confidence for fuzzy matches
        
        return None
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings using Levenshtein distance."""
        if len(s1) == 0:
            return 0.0 if len(s2) > 0 else 1.0
        if len(s2) == 0:
            return 0.0
        
        # Simple Levenshtein distance implementation
        matrix = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
        
        for i in range(len(s1) + 1):
            matrix[i][0] = i
        for j in range(len(s2) + 1):
            matrix[0][j] = j
        
        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        max_len = max(len(s1), len(s2))
        distance = matrix[len(s1)][len(s2)]
        similarity = 1.0 - (distance / max_len)
        
        return similarity
    
    def get_gene_info(self, gene_symbol: str) -> ProcessingResult[Dict[str, any]]:
        """Get detailed information about a gene."""
        try:
            if gene_symbol not in self.genes:
                return ProcessingResult(
                    success=False,
                    error=f"Gene {gene_symbol} not found"
                )
            
            gene_info = self.genes[gene_symbol].copy()
            return ProcessingResult(
                success=True,
                data=gene_info
            )
            
        except Exception as e:
            log.error(f"Error getting gene info: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get gene info: {str(e)}"
            )
    
    def batch_normalize_genes(self, gene_list: List[str]) -> ProcessingResult[List[Dict[str, any]]]:
        """Normalize multiple gene symbols at once."""
        try:
            results = []
            
            for gene_symbol in gene_list:
                result = self.normalize_gene_symbol(gene_symbol)
                if result.success:
                    results.append(result.data)
                else:
                    results.append({
                        "original_symbol": gene_symbol,
                        "normalized_symbol": None,
                        "error": result.error
                    })
            
            return ProcessingResult(
                success=True,
                data=results,
                metadata={"total_processed": len(gene_list)}
            )
            
        except Exception as e:
            log.error(f"Error in batch gene normalization: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Batch normalization failed: {str(e)}"
            )
    
    def search_genes(self, query: str, limit: int = 10) -> ProcessingResult[List[Dict[str, any]]]:
        """Search genes by query."""
        try:
            query_upper = query.upper()
            matches = []
            
            # Search in symbols, names, and aliases
            for symbol, gene_data in self.genes.items():
                name = gene_data.get("name", "").upper()
                aliases = [alias.upper() for alias in gene_data.get("aliases", [])]
                
                # Check symbol match
                if query_upper in symbol:
                    confidence = 1.0 if query_upper == symbol else 0.8
                    matches.append({
                        "symbol": symbol,
                        "name": gene_data.get("name", ""),
                        "match_type": "symbol",
                        "confidence": confidence
                    })
                
                # Check name match
                elif query_upper in name:
                    matches.append({
                        "symbol": symbol,
                        "name": gene_data.get("name", ""),
                        "match_type": "name",
                        "confidence": 0.7
                    })
                
                # Check alias match
                elif any(query_upper in alias for alias in aliases):
                    matches.append({
                        "symbol": symbol,
                        "name": gene_data.get("name", ""),
                        "match_type": "alias",
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
            log.error(f"Error searching genes: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Gene search failed: {str(e)}"
            )
    
    def get_statistics(self) -> ProcessingResult[Dict[str, any]]:
        """Get gene manager statistics."""
        try:
            stats = {
                "total_genes": len(self.genes),
                "total_symbol_mappings": len(self.symbol_to_hgnc),
                "total_alias_mappings": len(self.alias_to_hgnc),
                "total_previous_symbol_mappings": len(self.prev_symbols_to_hgnc),
                "data_path": str(self.gene_data_path)
            }
            
            return ProcessingResult(
                success=True,
                data=stats
            )
            
        except Exception as e:
            log.error(f"Error getting gene statistics: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Failed to get statistics: {str(e)}"
            )

