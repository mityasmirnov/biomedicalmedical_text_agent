"""
Simplified extraction orchestrator for biomedicalmedical_text_agent.

This module defines an ``ExtractionOrchestrator`` class that coordinates the
execution of multiple extraction agents (demographics, genetics, phenotypes,
treatments) on patient case descriptions extracted from articles.  It is
intended as a lightweight stand-in for the more sophisticated orchestrator
present in the upstream repository.  It supports processing plain text
documents by splitting them on occurrences of "Patient" followed by a
number, then running configured agents over each section.

Because this repository fragment may not include the full dependency tree
from the original project, this orchestrator does not attempt to perform
schema validation or PDF parsing.  It is designed to illustrate how the new
``PhenotypesAgent`` and ``TreatmentsAgent`` can be integrated alongside
existing agents.  In a full deployment, this class should be replaced or
extended to leverage the upstream ``SchemaManager``, ``PDFParser`` and
``PatientSegmenter`` classes.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

# Attempt to import existing agents if available.  If not, import stubs.
try:
    from biomedicalmedical_text_agent.src.agents.extraction_agents.phenotypes_agent import PhenotypesAgent
except ImportError:
    PhenotypesAgent = None  # type: ignore
try:
    from biomedicalmedical_text_agent.src.agents.extraction_agents.treatments_agent import TreatmentsAgent
except ImportError:
    TreatmentsAgent = None  # type: ignore


class ExtractionOrchestrator:
    """Coordinate multiple extraction agents on patient case text.

    Parameters
    ----------
    llm_client: Any
        An instance of an LLM client implementing a ``generate`` method.
    use_demographics: bool, optional
        If True and a DemographicsAgent is available, include it when extracting.
    use_genetics: bool, optional
        If True and a GeneticsAgent is available, include it when extracting.
    use_phenotypes: bool, optional
        If True and a PhenotypesAgent is available, include it when extracting.
    use_treatments: bool, optional
        If True and a TreatmentsAgent is available, include it when extracting.
    """

    def __init__(
        self,
        llm_client: Any,
        *,
        use_demographics: bool = False,
        use_genetics: bool = False,
        use_phenotypes: bool = True,
        use_treatments: bool = True,
    ) -> None:
        self.llm_client = llm_client
        self.use_demographics = use_demographics
        self.use_genetics = use_genetics
        self.use_phenotypes = use_phenotypes and PhenotypesAgent is not None
        self.use_treatments = use_treatments and TreatmentsAgent is not None
        # Lazily instantiate agents as needed
        self._phenotypes_agent: Optional[PhenotypesAgent] = None
        self._treatments_agent: Optional[TreatmentsAgent] = None

    @staticmethod
    def split_patients(text: str) -> List[Tuple[str, str]]:
        """Split an article text into (patient_id, section) tuples.

        Searches for occurrences of "Patient <number>" and returns a list of
        (patient_label, section_text).  If no occurrences are found the
        entire text is returned as a single section with an empty label.

        Parameters
        ----------
        text: str
            Raw article text.

        Returns
        -------
        list of tuples
            Each tuple contains the patient label (e.g. "Patient 1") and the
            corresponding section text.
        """
        pattern = re.compile(r"(Patient\s+\d+)", flags=re.IGNORECASE)
        matches = list(pattern.finditer(text))
        if not matches:
            return [("", text.strip())]
        sections = []
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            label = match.group(1).strip()
            section_text = text[start:end].strip()
            sections.append((label, section_text))
        return sections

    def _get_phenotypes_agent(self) -> PhenotypesAgent:
        if self._phenotypes_agent is None:
            self._phenotypes_agent = PhenotypesAgent(self.llm_client)
        return self._phenotypes_agent

    def _get_treatments_agent(self) -> TreatmentsAgent:
        if self._treatments_agent is None:
            self._treatments_agent = TreatmentsAgent(self.llm_client)
        return self._treatments_agent

    def extract_from_text(self, article_text: str) -> List[Dict[str, Any]]:
        """Run extraction on each patient section in the provided text.

        Parameters
        ----------
        article_text: str
            Raw text of the article to process.

        Returns
        -------
        List[Dict[str, Any]]
            A list of dictionaries representing extracted records.  Each
            dictionary includes at minimum the keys 'patient_id',
            'phenotypes', 'treatment_description' and 'outcome' if the
            corresponding agents are enabled.  Additional keys may be added
            by other agents (not implemented here).
        """
        records: List[Dict[str, Any]] = []
        for patient_label, section in self.split_patients(article_text):
            record: Dict[str, Any] = {}
            record["patient_id"] = patient_label or "unknown"
            # Run phenotypes agent
            if self.use_phenotypes:
                phen_agent = self._get_phenotypes_agent()
                result = phen_agent.extract(section)
                if result.success and result.data:
                    record.update(result.data)
            # Run treatments agent
            if self.use_treatments:
                treat_agent = self._get_treatments_agent()
                result = treat_agent.extract(section)
                if result.success and result.data:
                    record.update(result.data)
            # Additional agents (demographics, genetics) could be called here
            records.append(record)
        return records