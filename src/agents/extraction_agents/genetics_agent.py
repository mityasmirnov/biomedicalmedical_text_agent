"""
Genetics extraction agent for genetic information from patient cases.
"""

import json
import re
from typing import Dict, Any, Optional, List
from core.base import BaseAgent, ProcessingResult
from core.logging_config import get_logger
from processors.patient_segmenter import PatientSegment

log = get_logger(__name__)

class GeneticsAgent(BaseAgent):
    """Agent specialized in extracting genetic information from patient text."""
    
    def __init__(self, llm_client, **kwargs):
        super().__init__(name="genetics_agent", llm_client=llm_client, **kwargs)
        self.system_prompt = self._create_system_prompt()
        self._compile_genetic_patterns()
    
    def _compile_genetic_patterns(self):
        """Compile regex patterns for genetic information."""
        # Gene name patterns
        self.gene_patterns = [
            re.compile(r'\b([A-Z]{2,}[0-9]*[A-Z]*)\s+gene\b', re.IGNORECASE),
            re.compile(r'\bgene\s+([A-Z]{2,}[0-9]*[A-Z]*)\b', re.IGNORECASE),
            re.compile(r'\b([A-Z]{2,}[0-9]*[A-Z]*)\s+mutation', re.IGNORECASE),
        ]
        
        # Mutation patterns
        self.mutation_patterns = [
            re.compile(r'\bc\.([0-9]+[A-Z]>[A-Z])\b'),  # c.123A>G
            re.compile(r'\bp\.([A-Z][a-z]{2}[0-9]+[A-Z][a-z]{2})\b'),  # p.Arg123Gln
            re.compile(r'\b([A-Z][0-9]+[A-Z])\b'),  # R123Q
            re.compile(r'\b([0-9]+[A-Z]>[A-Z])\b'),  # 123A>G
        ]
        
        # Inheritance patterns
        self.inheritance_patterns = [
            re.compile(r'autosomal\s+recessive', re.IGNORECASE),
            re.compile(r'autosomal\s+dominant', re.IGNORECASE),
            re.compile(r'X-linked', re.IGNORECASE),
            re.compile(r'mitochondrial', re.IGNORECASE),
        ]
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for genetics extraction."""
        return """You are a medical genetics specialist focused on extracting genetic information from clinical case reports.

Your task is to extract the following genetic information from patient case text:
- gene: Primary gene involved (official gene symbol, e.g., "SURF1", "NDUFS1")
- mutations: Specific mutations/variants (e.g., "c.845_846delCT", "p.Arg123Gln")
- inheritance: Inheritance pattern (e.g., "autosomal recessive", "X-linked")
- zygosity: Mutation zygosity ("homozygous", "heterozygous", "compound heterozygous")
- parental_origin: Origin of mutation ("maternal", "paternal", "de novo", "unknown")
- genetic_testing: Type of genetic testing performed
- additional_genes: Other genes mentioned or tested

IMPORTANT RULES:
1. Extract ONLY information explicitly stated in the text
2. Use official gene symbols (e.g., SURF1, not surf1 or Surf1)
3. Include full mutation nomenclature when available
4. Use null for missing information
5. Return valid JSON format only
6. Be precise with genetic terminology

Example output format:
{
    "gene": "SURF1",
    "mutations": "c.845_846delCT",
    "inheritance": "autosomal recessive",
    "zygosity": "homozygous",
    "parental_origin": "unknown",
    "genetic_testing": "whole exome sequencing",
    "additional_genes": ["NDUFS1", "COX15"]
}"""
    
    async def execute(self, task: Dict[str, Any]) -> ProcessingResult[Dict[str, Any]]:
        """
        Execute genetics extraction task.
        
        Args:
            task: Task containing patient segment and extraction parameters
            
        Returns:
            ProcessingResult containing extracted genetics information
        """
        try:
            patient_segment = task.get("patient_segment")
            if not isinstance(patient_segment, PatientSegment):
                return ProcessingResult(
                    success=False,
                    error="Invalid patient segment provided"
                )
            
            log.info(f"Extracting genetics for {patient_segment.patient_id}")
            
            # Pre-process text to identify genetic elements
            genetic_hints = self._extract_genetic_hints(patient_segment.content)
            
            # Create extraction prompt
            prompt = self._create_extraction_prompt(patient_segment, genetic_hints)
            
            # Generate extraction using LLM
            result = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.0,
                max_tokens=1000
            )
            
            if not result.success:
                return ProcessingResult(
                    success=False,
                    error=f"LLM generation failed: {result.error}"
                )
            
            # Parse the JSON response
            extracted_data = self._parse_extraction_result(result.data)
            
            if not extracted_data:
                return ProcessingResult(
                    success=False,
                    error="Failed to parse extraction result"
                )
            
            # Validate and clean the extracted data
            cleaned_data = self._validate_and_clean_data(extracted_data)
            
            # Enhance with regex-based extraction
            enhanced_data = self._enhance_with_regex(cleaned_data, patient_segment.content)
            
            log.info(f"Successfully extracted genetics for {patient_segment.patient_id}")
            
            return ProcessingResult(
                success=True,
                data=enhanced_data,
                metadata={
                    "agent": self.name,
                    "patient_id": patient_segment.patient_id,
                    "extraction_method": "llm_with_regex_enhancement",
                    "genetic_hints": genetic_hints,
                    "llm_metadata": result.metadata
                }
            )
            
        except Exception as e:
            log.error(f"Error in genetics extraction: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Genetics extraction failed: {str(e)}"
            )
    
    def _extract_genetic_hints(self, text: str) -> Dict[str, List[str]]:
        """Extract genetic hints using regex patterns."""
        hints = {
            "genes": [],
            "mutations": [],
            "inheritance": []
        }
        
        # Extract gene names
        for pattern in self.gene_patterns:
            matches = pattern.findall(text)
            hints["genes"].extend(matches)
        
        # Extract mutations
        for pattern in self.mutation_patterns:
            matches = pattern.findall(text)
            hints["mutations"].extend(matches)
        
        # Extract inheritance patterns
        for pattern in self.inheritance_patterns:
            matches = pattern.findall(text)
            hints["inheritance"].extend(matches)
        
        # Remove duplicates and clean
        for key in hints:
            hints[key] = list(set(hints[key]))
        
        return hints
    
    def _create_extraction_prompt(self, patient_segment: PatientSegment, genetic_hints: Dict[str, List[str]]) -> str:
        """Create the extraction prompt for the patient segment."""
        prompt = f"""Extract genetic information from the following patient case text:

PATIENT TEXT:
{patient_segment.content}

"""
        
        # Add hints if found
        if any(genetic_hints.values()):
            prompt += "GENETIC ELEMENTS DETECTED:\n"
            if genetic_hints["genes"]:
                prompt += f"Potential genes: {', '.join(genetic_hints['genes'])}\n"
            if genetic_hints["mutations"]:
                prompt += f"Potential mutations: {', '.join(genetic_hints['mutations'])}\n"
            if genetic_hints["inheritance"]:
                prompt += f"Inheritance patterns: {', '.join(genetic_hints['inheritance'])}\n"
            prompt += "\n"
        
        prompt += "Extract the genetic information and return it as valid JSON following the specified format."
        
        return prompt
    
    def _parse_extraction_result(self, llm_output: str) -> Optional[Dict[str, Any]]:
        """Parse the LLM output to extract JSON data."""
        try:
            # Try to find JSON in the output
            json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            
            # If no JSON found, try to parse the entire output
            return json.loads(llm_output.strip())
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON from LLM output: {str(e)}")
            log.debug(f"LLM output was: {llm_output}")
            return None
        except Exception as e:
            log.error(f"Error parsing extraction result: {str(e)}")
            return None
    
    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the extracted genetic data."""
        cleaned = {}
        
        # Define expected fields and their types
        field_specs = {
            "gene": str,
            "mutations": str,
            "inheritance": str,
            "zygosity": str,
            "parental_origin": str,
            "genetic_testing": str,
            "additional_genes": list
        }
        
        for field, expected_type in field_specs.items():
            value = data.get(field)
            
            if value is None or value == "":
                cleaned[field] = None
                continue
            
            try:
                if expected_type == str:
                    cleaned[field] = str(value).strip() if value else None
                elif expected_type == list:
                    if isinstance(value, list):
                        cleaned[field] = [str(item).strip() for item in value if item]
                    elif isinstance(value, str):
                        # Try to parse as comma-separated list
                        items = [item.strip() for item in value.split(',') if item.strip()]
                        cleaned[field] = items if items else None
                    else:
                        cleaned[field] = None
                else:
                    cleaned[field] = value
                    
            except (ValueError, TypeError) as e:
                log.warning(f"Error converting field {field} with value {value}: {str(e)}")
                cleaned[field] = None
        
        # Additional validation
        self._validate_genetic_constraints(cleaned)
        
        return cleaned
    
    def _validate_genetic_constraints(self, data: Dict[str, Any]) -> None:
        """Validate genetic field constraints."""
        # Normalize gene names to uppercase
        if data.get("gene"):
            data["gene"] = data["gene"].upper()
        
        if data.get("additional_genes"):
            data["additional_genes"] = [gene.upper() for gene in data["additional_genes"]]
        
        # Validate inheritance patterns
        valid_inheritance = [
            "autosomal recessive", "autosomal dominant", 
            "X-linked", "mitochondrial", "unknown"
        ]
        inheritance = data.get("inheritance")
        if inheritance and inheritance.lower() not in [v.lower() for v in valid_inheritance]:
            log.warning(f"Non-standard inheritance pattern: {inheritance}")
        
        # Validate zygosity
        valid_zygosity = ["homozygous", "heterozygous", "compound heterozygous", "unknown"]
        zygosity = data.get("zygosity")
        if zygosity and zygosity.lower() not in [v.lower() for v in valid_zygosity]:
            log.warning(f"Non-standard zygosity: {zygosity}")
        
        # Validate parental origin
        valid_origins = ["maternal", "paternal", "de novo", "unknown"]
        origin = data.get("parental_origin")
        if origin and origin.lower() not in [v.lower() for v in valid_origins]:
            log.warning(f"Non-standard parental origin: {origin}")
    
    def _enhance_with_regex(self, data: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Enhance extracted data with regex-based findings."""
        enhanced = data.copy()
        
        # If no gene found by LLM, try regex
        if not enhanced.get("gene"):
            genes = []
            for pattern in self.gene_patterns:
                matches = pattern.findall(text)
                genes.extend(matches)
            
            if genes:
                # Take the most frequently mentioned gene
                gene_counts = {}
                for gene in genes:
                    gene_upper = gene.upper()
                    gene_counts[gene_upper] = gene_counts.get(gene_upper, 0) + 1
                
                most_common_gene = max(gene_counts, key=gene_counts.get)
                enhanced["gene"] = most_common_gene
                log.info(f"Enhanced gene extraction with regex: {most_common_gene}")
        
        # If no mutations found by LLM, try regex
        if not enhanced.get("mutations"):
            mutations = []
            for pattern in self.mutation_patterns:
                matches = pattern.findall(text)
                mutations.extend(matches)
            
            if mutations:
                enhanced["mutations"] = ", ".join(set(mutations))
                log.info(f"Enhanced mutation extraction with regex: {enhanced['mutations']}")
        
        # If no inheritance found by LLM, try regex
        if not enhanced.get("inheritance"):
            for pattern in self.inheritance_patterns:
                match = pattern.search(text)
                if match:
                    enhanced["inheritance"] = match.group(0).lower()
                    log.info(f"Enhanced inheritance extraction with regex: {enhanced['inheritance']}")
                    break
        
        return enhanced
    
    def normalize_gene_name(self, gene_name: str) -> str:
        """Normalize gene name to standard format."""
        if not gene_name:
            return gene_name
        
        # Convert to uppercase (standard for human genes)
        normalized = gene_name.upper().strip()
        
        # Remove common prefixes/suffixes that might be artifacts
        prefixes_to_remove = ["GENE", "PROTEIN"]
        suffixes_to_remove = ["GENE", "PROTEIN"]
        
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
        
        for suffix in suffixes_to_remove:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        
        return normalized
    
    def validate_mutation_nomenclature(self, mutation: str) -> bool:
        """Validate mutation nomenclature format."""
        if not mutation:
            return False
        
        # Common mutation nomenclature patterns
        valid_patterns = [
            r'^c\.\d+[ATCG]>[ATCG]$',  # c.123A>G
            r'^p\.[A-Z][a-z]{2}\d+[A-Z][a-z]{2}$',  # p.Arg123Gln
            r'^[A-Z]\d+[A-Z]$',  # R123Q
            r'^\d+[ATCG]>[ATCG]$',  # 123A>G
            r'^c\.\d+_\d+del[ATCG]*$',  # c.123_124delAT
            r'^c\.\d+ins[ATCG]+$',  # c.123insA
        ]
        
        return any(re.match(pattern, mutation) for pattern in valid_patterns)

