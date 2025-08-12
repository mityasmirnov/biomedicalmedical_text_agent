"""
Demographics extraction agent for patient demographic information.
"""

import json
import re
from typing import Dict, Any, Optional
from core.base import BaseAgent, ProcessingResult
from core.logging_config import get_logger
from processors.patient_segmenter import PatientSegment

log = get_logger(__name__)

class DemographicsAgent(BaseAgent):
    """Agent specialized in extracting demographic information from patient text."""
    
    def __init__(self, llm_client, **kwargs):
        super().__init__(name="demographics_agent", llm_client=llm_client, **kwargs)
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for demographics extraction."""
        return """You are a medical data extraction specialist focused on extracting demographic information from clinical case reports.

Your task is to extract the following demographic information from patient case text:
- patient_id: Patient identifier (e.g., "Patient 1", "Case A", etc.)
- sex: Patient sex (0 for male, 1 for female, null if unknown)
- age_of_onset: Age when symptoms/condition first appeared (in years, as number)
- last_seen: Age at last clinical visit or follow-up (in years, as number)
- _0_alive_1_dead: Patient status (0 for alive, 1 for dead, null if unknown)
- age_of_death: Age at death (in years, as number, null if alive or unknown)
- ethnicity: Patient ethnicity/race if mentioned
- consanguinity: Whether parents are related (0 for no, 1 for yes, null if unknown)
- family_history: Brief description of relevant family history

IMPORTANT RULES:
1. Extract ONLY information explicitly stated in the text
2. Use null for missing or unclear information
3. Convert ages to numbers (e.g., "5 years old" → 5)
4. For sex: male=0, female=1
5. For alive/dead status: alive=0, dead=1
6. Return valid JSON format only
7. Be conservative - if unsure, use null

Example output format:
{
    "patient_id": "Patient 1",
    "sex": 1,
    "age_of_onset": 3,
    "last_seen": 12,
    "_0_alive_1_dead": 0,
    "age_of_death": null,
    "ethnicity": "Caucasian",
    "consanguinity": 0,
    "family_history": "No significant family history"
}"""
    
    async def execute(self, task: Dict[str, Any]) -> ProcessingResult[Dict[str, Any]]:
        """
        Execute demographics extraction task.
        
        Args:
            task: Task containing patient segment and extraction parameters
            
        Returns:
            ProcessingResult containing extracted demographics
        """
        try:
            patient_segment = task.get("patient_segment")
            if not isinstance(patient_segment, PatientSegment):
                return ProcessingResult(
                    success=False,
                    error="Invalid patient segment provided"
                )
            
            log.info(f"Extracting demographics for {patient_segment.patient_id}")
            
            # Create extraction prompt
            prompt = self._create_extraction_prompt(patient_segment)
            
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
            
            log.info(f"Successfully extracted demographics for {patient_segment.patient_id}")
            
            return ProcessingResult(
                success=True,
                data=cleaned_data,
                metadata={
                    "agent": self.name,
                    "patient_id": patient_segment.patient_id,
                    "extraction_method": "llm_based",
                    "llm_metadata": result.metadata
                }
            )
            
        except Exception as e:
            log.error(f"Error in demographics extraction: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Demographics extraction failed: {str(e)}"
            )
    
    def _create_extraction_prompt(self, patient_segment: PatientSegment) -> str:
        """Create the extraction prompt for the patient segment."""
        prompt = f"""Extract demographic information from the following patient case text:

PATIENT TEXT:
{patient_segment.content}

Extract the demographic information and return it as valid JSON following the specified format."""
        
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
        """Validate and clean the extracted demographic data."""
        cleaned = {}
        
        # Define expected fields and their types
        field_specs = {
            "patient_id": str,
            "sex": int,
            "age_of_onset": (int, float),
            "last_seen": (int, float),
            "_0_alive_1_dead": int,
            "age_of_death": (int, float),
            "ethnicity": str,
            "consanguinity": int,
            "family_history": str
        }
        
        for field, expected_type in field_specs.items():
            value = data.get(field)
            
            if value is None or value == "":
                cleaned[field] = None
                continue
            
            try:
                if expected_type == str:
                    cleaned[field] = str(value).strip() if value else None
                elif expected_type == int:
                    if isinstance(value, str) and value.lower() in ["null", "none", ""]:
                        cleaned[field] = None
                    else:
                        cleaned[field] = int(float(value))
                elif expected_type == (int, float):
                    if isinstance(value, str) and value.lower() in ["null", "none", ""]:
                        cleaned[field] = None
                    else:
                        cleaned[field] = float(value)
                else:
                    cleaned[field] = value
                    
            except (ValueError, TypeError) as e:
                log.warning(f"Error converting field {field} with value {value}: {str(e)}")
                cleaned[field] = None
        
        # Additional validation
        self._validate_field_constraints(cleaned)
        
        return cleaned
    
    def _validate_field_constraints(self, data: Dict[str, Any]) -> None:
        """Validate field constraints and fix common issues."""
        # Validate sex values
        sex = data.get("sex")
        if sex is not None and sex not in [0, 1]:
            log.warning(f"Invalid sex value: {sex}, setting to null")
            data["sex"] = None
        
        # Validate alive/dead status
        alive_dead = data.get("_0_alive_1_dead")
        if alive_dead is not None and alive_dead not in [0, 1]:
            log.warning(f"Invalid alive/dead status: {alive_dead}, setting to null")
            data["_0_alive_1_dead"] = None
        
        # Validate consanguinity
        consanguinity = data.get("consanguinity")
        if consanguinity is not None and consanguinity not in [0, 1]:
            log.warning(f"Invalid consanguinity value: {consanguinity}, setting to null")
            data["consanguinity"] = None
        
        # Validate age consistency
        age_of_onset = data.get("age_of_onset")
        last_seen = data.get("last_seen")
        age_of_death = data.get("age_of_death")
        
        if (age_of_onset is not None and last_seen is not None and 
            age_of_onset > last_seen):
            log.warning("Age of onset > last seen, swapping values")
            data["age_of_onset"], data["last_seen"] = last_seen, age_of_onset
        
        if (age_of_death is not None and last_seen is not None and 
            age_of_death < last_seen):
            log.warning("Age of death < last seen, setting last_seen to age_of_death")
            data["last_seen"] = age_of_death
        
        # If patient is dead, ensure age_of_death is set
        if alive_dead == 1 and age_of_death is None and last_seen is not None:
            log.info("Patient marked as dead, using last_seen as age_of_death")
            data["age_of_death"] = last_seen
    
    def extract_age_from_text(self, text: str) -> Optional[float]:
        """Extract age from text using regex patterns."""
        age_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*old',
            r'(\d+(?:\.\d+)?)\s*(?:months?|mos?)\s*old',
            r'age\s*(?:of\s*)?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:year|yr)[-\s]old',
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                age_value = float(match.group(1))
                
                # Convert months to years if needed
                if 'month' in match.group(0).lower():
                    age_value = age_value / 12
                
                return age_value
        
        return None

