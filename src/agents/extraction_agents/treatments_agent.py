"""
Module implementing a simple TreatmentsAgent for extracting treatment and outcome
information from patient case descriptions.  This agent is designed to be used
within the biomedicalmedical_text_agent pipeline.  It accepts a patient text
section and uses an LLM client to identify any therapies, medications or
interventions administered to the patient and the reported outcomes.

The output is returned as a dictionary structured according to the expected
schema keys.  If the LLM cannot determine a value for a field it should
return an empty string or None.  The agent may also log warnings or errors
via a ProcessingResult object if it encounters unexpected situations.

This implementation is intentionally lightweight and does not impose any
particular prompt format on the calling code.  Downstream orchestrators
should construct an appropriate prompt and pass the full patient text to
``extract``.

Example usage::

    from biomedicalmedical_text_agent.src.agents.extraction_agents.treatments_agent import TreatmentsAgent
    llm_client = ...  # instance of OpenRouterClient or HuggingFace client
    agent = TreatmentsAgent(llm_client)
    result = agent.extract(patient_text)
    if result.success:
        print(result.data)
    else:
        print("Extraction failed", result.error)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ProcessingResult:
    """Simple container for results returned by extraction agents.

    This class mirrors the ProcessingResult used elsewhere in the project.  It
    holds either a data dictionary on success or an error message on failure.
    Agents may also emit warnings describing minor issues encountered during
    processing.
    """

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)


class TreatmentsAgent:
    """Agent for extracting treatment and outcome information from text.

    Parameters
    ----------
    llm_client: Any
        An object implementing a ``generate`` method compatible with the
        existing OpenRouterClient.  The ``generate`` method should accept
        ``messages`` and ``model`` keyword arguments and return an object with
        a ``content`` attribute containing the model's response.
    system_prompt: str, optional
        Custom system prompt instructing the LLM to extract treatment
        information.  If not provided a sensible default prompt will be used.
    model: str, optional
        Name of the model to use when calling the LLM.  Defaults to
        ``"deepseek/deepseek-chat-v3-0324:free"`` to keep inference cost low.
    """

    def __init__(self, llm_client: Any, system_prompt: Optional[str] = None, model: str = "deepseek/deepseek-chat-v3-0324:free") -> None:
        self.llm_client = llm_client
        self.model = model
        if system_prompt is None:
            self.system_prompt = (
                "You are a biomedical information extraction agent.\n"
                "Your task is to identify treatments, interventions and outcomes described in the provided patient case description.\n"
                "Return a JSON object with the keys:\n"
                "    treatment_description: free text of any pharmacologic or non-pharmacologic treatments administered;\n"
                "    outcome: description of the patient's response to treatment, including improvement, deterioration or death;\n"
                "If no information is available for a field, return an empty string.\n"
                "Do not infer details that are not explicitly stated."
            )
        else:
            self.system_prompt = system_prompt

    def extract(self, patient_text: str) -> ProcessingResult:
        """Extract treatment and outcome information from a patient description.

        Parameters
        ----------
        patient_text: str
            The full textual description of a single patient case extracted from
            an article.  This may include clinical course, interventions and
            outcomes.

        Returns
        -------
        ProcessingResult
            A result object containing either a data dictionary with keys
            ``treatment_description`` and ``outcome`` on success or an error
            message on failure.
        """
        # Build a conversation for the LLM using system and user roles.  We
        # expect the llm_client to handle this format (similar to
        # OpenRouterClient or ChatGPT API).
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": (
                    "Patient description:\n"
                    f"{patient_text}\n\n"
                    "Please extract the treatment information and outcome as JSON with keys 'treatment_description' and 'outcome'."
                ),
            },
        ]

        try:
            # Call the LLM client.  We disable temperature for deterministic
            # output.  Additional kwargs may be passed through by llm_client
            # generate implementation.
            response = self.llm_client.generate(
                messages=messages,
                model=self.model,
                temperature=0.0,
                max_tokens=500,
            )
            # Extract the content string from the response.  For OpenRouter
            # responses we expect response.content; adjust as needed for other
            # clients.
            content = response.content if hasattr(response, "content") else response
            # Try to parse JSON from the response.  If parsing fails, we'll
            # return an error.
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                return ProcessingResult(
                    success=False,
                    error="Failed to parse JSON from model response",
                )
            # Ensure required keys exist in the dictionary
            for key in ["treatment_description", "outcome"]:
                data.setdefault(key, "")
            return ProcessingResult(success=True, data=data)
        except Exception as e:
            # Catch any unexpected exceptions from the LLM client
            return ProcessingResult(success=False, error=str(e))