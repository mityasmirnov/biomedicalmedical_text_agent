"""
LangExtract Engine for Biomedical Information Extraction

This module integrates Google's LangExtract with OpenRouter API for structured
extraction from medical literature with precise source grounding.
"""

import os
import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try to import LangExtract
try:
    import langextract as lx
except ImportError:
    lx = None

from openai import OpenAI

from .schema_classes import BiomedicExtractionClasses, BIOMEDICAL_SYSTEM_PROMPT
from .normalizer import BiomedicNormalizer
# Remove circular import
# from core.config import Config
from processors.patient_segmenter import PatientSegmenter


logger = logging.getLogger(__name__)


class LangExtractEngine:
    """
    LangExtract engine for biomedical information extraction.
    
    Integrates Google's LangExtract with OpenRouter API for structured
    extraction from medical literature with precise source grounding.
    """
    
    def __init__(
        self,
        config: Optional[Any] = None,
        model_id: str = "google/gemma-2-27b-it:free",
        openrouter_api_key: Optional[str] = None,
        use_local_model: bool = False,
        local_model_url: str = "http://localhost:11434"
    ):
        """
        Initialize LangExtract engine.
        
        Args:
            config: System configuration (optional to avoid circular imports)
            model_id: Model ID for OpenRouter or local model
            openrouter_api_key: OpenRouter API key
            use_local_model: Whether to use local model (Ollama)
            local_model_url: URL for local model server
        """
        if lx is None:
            raise ImportError("LangExtract is required. Install with: pip install langextract")
        
        self.config = config
        self.model_id = model_id
        self.use_local_model = use_local_model
        self.local_model_url = local_model_url
        
        # Set up API key
        self.openrouter_api_key = (
            openrouter_api_key or 
            os.getenv("OPENROUTER_API_KEY") or
            (self.config.llm.openrouter_api_key if self.config and hasattr(self.config, 'llm') else None)
        )
        
        # Initialize extraction classes
        self.extraction_classes = BiomedicExtractionClasses()
        
        # Initialize normalizer
        self.normalizer = BiomedicNormalizer(config=self.config)
        
        # Initialize patient segmenter (optional; fallback to simple segmentation)
        try:
            self.patient_segmenter = PatientSegmenter()
        except Exception:
            self.patient_segmenter = None
        
        # Setup OpenAI client for OpenRouter
        if not self.use_local_model and self.openrouter_api_key:
            self.openai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key
            )
        else:
            self.openai_client = None
        
        logger.info(f"LangExtract engine initialized with model: {model_id}")
    
    def extract_from_text(
        self,
        text: str,
        extraction_passes: int = 2,
        max_workers: int = 8,
        max_char_buffer: int = 1200,
        segment_patients: bool = True,
        include_visualization: bool = True
    ) -> Dict[str, Any]:
        """
        Extract structured information from biomedical text.
        
        Args:
            text: Input text to extract from
            extraction_passes: Number of extraction passes for improved recall
            max_workers: Number of parallel workers
            max_char_buffer: Maximum character buffer size for chunking
            segment_patients: Whether to segment text by patients first
            include_visualization: Whether to generate visualization HTML
            
        Returns:
            Dictionary containing extraction results and metadata
        """
        logger.info(f"Starting extraction from text ({len(text)} characters)")
        
        try:
            # Segment by patients if requested
            if segment_patients:
                patient_segments = self._segment_text_simple(text)
                logger.info(f"Segmented text into {len(patient_segments)} patient sections (simple)")
            else:
                patient_segments = [{"text": text, "patient_id": "unknown", "start": 0, "end": len(text)}]
            
            all_results = []
            
            # Process each patient segment
            for i, segment in enumerate(patient_segments):
                logger.info(f"Processing patient segment {i+1}/{len(patient_segments)}")
                
                # Run LangExtract
                result = self._run_langextract(
                    text=segment["text"],
                    extraction_passes=extraction_passes,
                    max_workers=max_workers,
                    max_char_buffer=max_char_buffer
                )
                
                all_results.append(result)
            
            # Combine results
            combined_result = self._combine_results(all_results)
            # Add high-level segment metadata without relying on result.metadata
            combined_result.setdefault("metadata", {})
            combined_result["metadata"].setdefault("segments", [])
            for i, segment in enumerate(patient_segments):
                combined_result["metadata"]["segments"].append({
                    "segment_id": i,
                    "patient_id": segment.get("patient_id"),
                    "segment_start": segment.get("start"),
                    "segment_end": segment.get("end")
                })
            
            # Normalize extractions
            normalized_result = self.normalizer.normalize_extractions(combined_result)
            
            # Generate visualization if requested
            if include_visualization:
                visualization_html = self._generate_visualization(normalized_result)
                normalized_result["visualization_html"] = visualization_html
            
            logger.info("Extraction completed successfully")
            return normalized_result
            
        except Exception as e:
            logger.error(f"Error during extraction: {e}")
            raise
    
    def extract_from_file(
        self,
        file_path: Union[str, Path],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract from a file (PDF, TXT, etc.).
        
        Args:
            file_path: Path to input file
            **kwargs: Additional arguments for extract_from_text
            
        Returns:
            Extraction results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content based on extension
        if file_path.suffix.lower() == '.pdf':
            from ..processors.pdf_parser import PDFParser
            parser = PDFParser()
            text = parser.extract_text(str(file_path))
        else:
            # Assume text file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        return self.extract_from_text(text, **kwargs)
    
    def extract_from_url(
        self,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract from a URL (supports direct LangExtract URL processing).
        
        Args:
            url: URL to extract from
            **kwargs: Additional arguments
            
        Returns:
            Extraction results
        """
        logger.info(f"Extracting from URL: {url}")
        
        # Use LangExtract's built-in URL support
        result = self._run_langextract(
            text=url,  # LangExtract handles URLs directly
            **kwargs
        )
        
        # Normalize results
        normalized_result = self.normalizer.normalize_extractions(result)
        
        return normalized_result
    
    def _run_langextract(
        self,
        text: str,
        extraction_passes: int = 2,
        max_workers: int = 8,
        max_char_buffer: int = 1200
    ) -> Any:
        """
        Run LangExtract on the given text.
        
        Args:
            text: Input text
            extraction_passes: Number of passes
            max_workers: Parallel workers
            max_char_buffer: Buffer size
            
        Returns:
            LangExtract result object
        """
        # Prepare examples from schema classes
        examples = self._prepare_examples()
        
        # Configure model parameters
        selected_model_id = self.model_id
        # Force OpenAI-compatible provider when using OpenRouter to avoid accidental Ollama selection by pattern
        if not self.use_local_model and self.openrouter_api_key:
            # If the model id matches common non-OpenAI providers that LangExtract maps to Ollama, fall back to a safe OpenAI id
            import re
            if re.match(r"^(google/|microsoft/|huggingfaceh4/|meta-llama/|mistralai/|Qwen/|deepseek-ai/|bigcode/|codellama/|TinyLlama/|WizardLM/)", selected_model_id, flags=re.IGNORECASE):
                logger.warning(
                    f"Model id '{selected_model_id}' maps to Ollama in LangExtract. "
                    f"Using OpenRouter via OpenAI-compatible id 'gpt-4o-mini' instead."
                )
                selected_model_id = "gpt-4o-mini"

        model_params = {
            "model_id": selected_model_id,
            "extraction_passes": extraction_passes,
            "max_workers": max_workers,
            "max_char_buffer": max_char_buffer,
            "temperature": 0.0
        }
        
        # Add model-specific parameters
        if self.use_local_model:
            model_params.update({
                "model_url": self.local_model_url,
                "fence_output": False,
                "use_schema_constraints": False
            })
        else:
            # For OpenRouter/cloud models using OpenAI-compatible API
            if self.openrouter_api_key:
                # Route OpenAI client through OpenRouter
                os.environ["OPENROUTER_API_KEY"] = self.openrouter_api_key
                os.environ["OPENAI_API_KEY"] = self.openrouter_api_key
                os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
        
        # Run extraction
        result = lx.extract(
            text_or_documents=text,
            prompt_description=BIOMEDICAL_SYSTEM_PROMPT,
            examples=examples,
            **model_params
        )
        
        return result

    def _segment_text_simple(self, text: str) -> List[Dict[str, Any]]:
        """
        Simple patient segmentation based on explicit markers.
        Falls back to single segment if no markers found.
        """
        import re
        markers = list(re.finditer(r"\b(?:Patient|Case|Subject|Individual)\s+(\d+|[A-Z])\b", text, flags=re.IGNORECASE))
        if not markers:
            return [{"text": text, "patient_id": "Patient 1", "start": 0, "end": len(text)}]
        segments: List[Dict[str, Any]] = []
        for i, m in enumerate(markers):
            start = m.start()
            end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
            content = text[start:end].strip()
            if not content:
                continue
            pid = f"Patient {m.group(1)}"
            segments.append({"text": content, "patient_id": pid, "start": start, "end": end})
        if not segments:
            return [{"text": text, "patient_id": "Patient 1", "start": 0, "end": len(text)}]
        return segments
    
    def _prepare_examples(self) -> List[Any]:
        """
        Prepare few-shot examples from extraction classes.
        
        Returns:
            List of LangExtract example objects
        """
        examples = []
        
        # Get examples from PatientRecord class
        patient_record_class = self.extraction_classes.patient_record
        
        if patient_record_class.few_shot_examples:
            for example_data in patient_record_class.few_shot_examples:
                # Convert to LangExtract format
                extractions = []
                
                for extraction_dict in example_data["extractions"]:
                    for class_name, class_data in extraction_dict.items():
                        # Create extraction object
                        extraction = lx.data.Extraction(
                            extraction_class=class_name,
                            extraction_text=example_data["extraction_text"],
                            attributes=class_data
                        )
                        extractions.append(extraction)
                
                # Create example
                example = lx.data.ExampleData(
                    text=example_data["extraction_text"],
                    extractions=extractions
                )
                examples.append(example)
        
        return examples
    
    def _combine_results(self, results: List[Any]) -> Dict[str, Any]:
        """
        Combine multiple LangExtract results.
        
        Args:
            results: List of LangExtract result objects
            
        Returns:
            Combined result dictionary
        """
        combined = {
            "extractions": [],
            "metadata": {
                "total_segments": len(results),
                "extraction_timestamp": datetime.utcnow().isoformat(),
                "model_id": self.model_id,
                "segments": []
            }
        }
        
        for i, result in enumerate(results):
            # Extract data from result object and convert to serializable dicts
            raw_extractions = []
            if hasattr(result, 'extractions') and result.extractions is not None:
                raw_extractions = result.extractions
            elif hasattr(result, 'data') and result.data is not None:
                raw_extractions = result.data

            for item in raw_extractions:
                # LangExtract Extraction object → dict
                if hasattr(item, 'extraction_class') and hasattr(item, 'attributes'):
                    extraction_dict = {
                        "extraction_class": getattr(item, 'extraction_class', None),
                        "attributes": getattr(item, 'attributes', None),
                        "extraction_text": getattr(item, 'extraction_text', None)
                    }
                    combined["extractions"].append(extraction_dict)
                elif isinstance(item, dict):
                    combined["extractions"].append(item)
            
            # Add segment metadata
            segment_meta = {
                "segment_id": i,
                "extraction_count": len(raw_extractions),
            }
            
            if hasattr(result, 'metadata') and result.metadata:
                segment_meta.update(result.metadata)
            
            combined["metadata"]["segments"].append(segment_meta)
        
        return combined
    
    def _generate_visualization(self, extraction_result: Dict[str, Any]) -> str:
        """
        Generate HTML visualization of extractions.
        
        Args:
            extraction_result: Normalized extraction results
            
        Returns:
            HTML string for visualization
        """
        try:
            # Save extractions to temporary JSONL file
            temp_file = Path("/tmp/temp_extractions.jsonl")
            
            # Convert to LangExtract format for visualization
            with open(temp_file, 'w') as f:
                # Prefer normalized container's original_extractions if present
                extractions = extraction_result.get("extractions") or extraction_result.get("original_extractions") or []
                for extraction in extractions:
                    # Ensure each line is JSON-serializable dict
                    if isinstance(extraction, dict):
                        f.write(json.dumps(extraction, default=str) + "\n")
                    else:
                        try:
                            f.write(json.dumps(extraction.__dict__, default=str) + "\n")
                        except Exception:
                            # Fallback to string
                            f.write(json.dumps({"extraction": str(extraction)}) + "\n")
            
            # Generate visualization
            html_content = lx.visualize(str(temp_file))
            
            # Clean up
            if temp_file.exists():
                temp_file.unlink()
            
            # Handle different return types
            if hasattr(html_content, 'data'):
                return html_content.data
            else:
                return str(html_content)
                
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            return f"<html><body><h1>Visualization Error</h1><p>{str(e)}</p></body></html>"
    
    def save_results(
        self,
        results: Dict[str, Any],
        output_dir: Union[str, Path],
        filename_prefix: str = "extraction_results"
    ) -> Dict[str, Path]:
        """
        Save extraction results to files.
        
        Args:
            results: Extraction results
            output_dir: Output directory
            filename_prefix: Prefix for output files
            
        Returns:
            Dictionary of saved file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_files = {}
        
        # Save JSON results
        json_file = output_dir / f"{filename_prefix}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        saved_files["json"] = json_file
        
        # Save JSONL for LangExtract compatibility
        jsonl_file = output_dir / f"{filename_prefix}_{timestamp}.jsonl"
        with open(jsonl_file, 'w') as f:
            extractions = results.get("extractions") or results.get("original_extractions") or []
            for extraction in extractions:
                f.write(json.dumps(extraction, default=str) + "\n")
        saved_files["jsonl"] = jsonl_file
        
        # Save visualization HTML
        if "visualization_html" in results:
            html_file = output_dir / f"{filename_prefix}_{timestamp}.html"
            with open(html_file, 'w') as f:
                f.write(results["visualization_html"])
            saved_files["html"] = html_file
        
        # Save normalized CSV
        if "normalized_data" in results:
            csv_file = output_dir / f"{filename_prefix}_{timestamp}.csv"
            import pandas as pd
            df = pd.DataFrame(results["normalized_data"])
            df.to_csv(csv_file, index=False)
            saved_files["csv"] = csv_file
        
        logger.info(f"Results saved to {len(saved_files)} files in {output_dir}")
        return saved_files
    
    def evaluate_against_ground_truth(
        self,
        extraction_results: Dict[str, Any],
        ground_truth_file: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Evaluate extraction results against ground truth.
        
        Args:
            extraction_results: Results from extraction
            ground_truth_file: Path to ground truth CSV
            
        Returns:
            Evaluation metrics and comparison
        """
        return self.normalizer.evaluate_against_ground_truth(
            extraction_results,
            ground_truth_file
        )


# Utility functions for easy usage

def extract_from_text(
    text: str,
    model_id: str = "google/gemma-2-27b-it:free",
    openrouter_api_key: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick extraction from text using default settings.
    
    Args:
        text: Input text
        model_id: Model to use
        openrouter_api_key: API key
        **kwargs: Additional arguments
        
    Returns:
        Extraction results
    """
    engine = LangExtractEngine(
        model_id=model_id,
        openrouter_api_key=openrouter_api_key
    )
    return engine.extract_from_text(text, **kwargs)


def extract_from_file(
    file_path: Union[str, Path],
    model_id: str = "google/gemma-2-27b-it:free",
    openrouter_api_key: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick extraction from file using default settings.
    
    Args:
        file_path: Input file path
        model_id: Model to use
        openrouter_api_key: API key
        **kwargs: Additional arguments
        
    Returns:
        Extraction results
    """
    engine = LangExtractEngine(
        model_id=model_id,
        openrouter_api_key=openrouter_api_key
    )
    return engine.extract_from_file(file_path, **kwargs)


# Example usage
if __name__ == "__main__":
    # Example text
    sample_text = """
    Patient 2 is a female who developed generalized weakness on the second day of fever 
    when she was 2 years and 5 months old, approximately half a month after measles vaccination. 
    She later had recurrent episodes at 4 years 2 months. Molecular testing identified two 
    variants in SLC19A3: c.26T>C (p.Leu9Pro) and c.980-7_980-4del. She received high-dose 
    thiamine and biotin with clinical improvement. She is alive at last follow-up.
    """
    
    # Run extraction
    try:
        results = extract_from_text(
            text=sample_text,
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
        )
        
        print("Extraction completed!")
        print(f"Found {len(results.get('extractions', []))} extractions")
        
        # Print first few extractions
        for i, extraction in enumerate(results.get('extractions', [])[:3]):
            print(f"\nExtraction {i+1}:")
            print(json.dumps(extraction, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set OPENROUTER_API_KEY environment variable")

