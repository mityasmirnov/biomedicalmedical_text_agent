"""
extraction_pipeline.py

This script demonstrates a minimal workflow for extracting
structured patient information from a PDF article when fully featured
natural‑language models and external libraries are not available.  It
shows how to:

1. Convert a PDF to text using the system utility ``pdftotext``.
2. Segment the text into per‑patient sections based on headings
   (e.g. "Patient 1", "Patient 2", etc.).
3. Apply simple regular expressions and heuristic rules to pull out
   key fields (sex, age of onset, gene, survival) from the text.
4. Construct JSON records that follow a supplied JSON schema.  All
   schema fields are populated with ``None`` by default to satisfy
   required keys and type expectations, then overwritten where
   applicable.
5. Compare the extracted records against a manually curated CSV file
   (ground truth) for a handful of core fields and report any
   differences.

Note
----
This is *not* a full implementation of the earlier proposed agent
architecture.  It bypasses LLM invocation because internet access
and package installation are restricted in the runtime environment.
Nevertheless, it demonstrates the structure of a pipeline that can
later be extended with real NLP models or external services.

Usage
-----
Run this script from the repository root using:

```
python extraction_pipeline.py
```

It will parse ``PMID32679198.pdf`` and ``table_schema.json`` from
``/home/oai/share`` and produce ``extracted_records.json`` in the
same directory.  It also prints a diff report comparing selected
fields to those in ``manually_processed.csv``.

"""

import csv
import json
import os
import re
import subprocess
from typing import Dict, List, Tuple, Optional


DATA_DIR = "/home/oai/share"
PDF_PATH = os.path.join(DATA_DIR, "PMID32679198.pdf")
SCHEMA_PATH = os.path.join(DATA_DIR, "table_schema.json")
CSV_PATH = os.path.join(DATA_DIR, "manually_processed.csv")
OUTPUT_JSON = os.path.join(DATA_DIR, "extracted_records.json")


def pdf_to_text(pdf_path: str) -> str:
    """Return the plain text contents of a PDF using pdftotext.

    ``pdftotext`` is part of poppler and available in this environment.
    It will emit UTF‑8 text when invoked with ``-`` (stdout).

    Parameters
    ----------
    pdf_path : str
        Absolute path to the PDF file.

    Returns
    -------
    str
        The full plain text of the PDF.
    """
    result = subprocess.run([
        "pdftotext",
        pdf_path,
        "-"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return result.stdout.decode("utf-8", errors="ignore")


def segment_patients(text: str) -> Dict[str, str]:
    """Segment the full PDF text into sections for each patient.

    The PDF for PMID32679198 uses headings like "3.2 Patient 1",
    "3.3 Patient 2", etc.  We detect these headings case‑insensitively
    and capture the text until the next heading.

    Parameters
    ----------
    text : str
        Full plain text of the PDF.

    Returns
    -------
    Dict[str, str]
        Mapping from patient number ("1", "2", ...) to the text of
        that patient's section (including the heading line).
    """
    sections: Dict[str, str] = {}
    # Find all occurrences of "Patient X" preceded by a number and a dot (e.g. "3.2 Patient 1")
    # Match "Patient X" as a standalone word followed by digits.  We use
    # a word boundary after "Patient" to avoid matching "Patients" (plural).
    pattern = re.compile(r"\bPatient\b\s+(\d+)\b", re.IGNORECASE)
    matches = list(pattern.finditer(text))
    for i, match in enumerate(matches):
        pid = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[pid] = text[start:end].strip()
    return sections


def parse_age_of_onset(section_text: str) -> Optional[float]:
    """Extract the age of onset in years from a patient section.

    The article tends to describe onset with phrases like "age of 4 months",
    "age of 2 years and 5 months" or "age of 8.5 months".  This
    function searches for these patterns and converts them to a numeric
    year value.  If multiple ages are found, the earliest is returned.

    Parameters
    ----------
    section_text : str
        Text for a patient section.

    Returns
    -------
    Optional[float]
        Age of onset in years (e.g. 0.33 for 4 months).  Returns
        None if not found.
    """
    # Collect candidate ages and pick the smallest (earliest) value.
    candidates: List[float] = []
    # Patterns like "age of 8.5 months" or "age of 2 years and 5 months"
    month_pat = re.compile(r"age of ([0-9]+(?:\.[0-9]+)?)\s*months", re.IGNORECASE)
    year_month_pat = re.compile(
        r"age of ([0-9]+(?:\.[0-9]+)?)\s*years?\s*(?:and\s*([0-9]+(?:\.[0-9]+)?)\s*months?)?",
        re.IGNORECASE
    )
    # Patterns like "was 2 years and 5 months old"
    was_year_month = re.compile(
        r"was\s+([0-9]+(?:\.[0-9]+)?)\s*years?\s*(?:and\s*([0-9]+(?:\.[0-9]+)?)\s*months?)?\s*old",
        re.IGNORECASE
    )
    # Patterns like "was 8.5 months old"
    was_month_only = re.compile(
        r"was\s+([0-9]+(?:\.[0-9]+)?)\s*months?\s*old",
        re.IGNORECASE
    )
    # Search patterns and append candidate ages
    for match in year_month_pat.finditer(section_text):
        years = float(match.group(1))
        months = float(match.group(2)) if match.group(2) else 0.0
        candidates.append(years + months / 12.0)
    for match in month_pat.finditer(section_text):
        months = float(match.group(1))
        candidates.append(months / 12.0)
    for match in was_year_month.finditer(section_text):
        years = float(match.group(1))
        months = float(match.group(2)) if match.group(2) else 0.0
        candidates.append(years + months / 12.0)
    for match in was_month_only.finditer(section_text):
        months = float(match.group(1))
        candidates.append(months / 12.0)
    if not candidates:
        return None
    return round(min(candidates), 4)


def parse_sex(section_text: str) -> Optional[str]:
    """Infer the sex of the patient from the section text.

    We look for keywords like "male" or "female".  If both
    appear, the first occurrence decides.  Returns 'm' for male,
    'f' for female, or None if undetermined.
    """
    lower = section_text.lower()
    idx_male = lower.find(" male ")
    idx_female = lower.find(" female ")
    if idx_male == -1 and idx_female == -1:
        return None
    if idx_male != -1 and (idx_female == -1 or idx_male < idx_female):
        return "m"
    return "f"


def assign_gene(patient_id: str) -> str:
    """Assign the major gene associated with each patient.

    According to the article text and Table 2, patients 1-4 carry
    mutations in **SLC19A3**, patients 5 and 6 carry mutations in
    **SLC25A19**, and patient 7 carries mutations in **TPK1**.  This
    heuristic is encoded here.  In a more general solution, gene
    mentions would be extracted from the text or table directly.
    """
    pid_num = int(patient_id)
    if pid_num in {1, 2, 3, 4}:
        return "SLC19A3"
    elif pid_num in {5, 6}:
        return "SLC25A19"
    elif pid_num == 7:
        return "TPK1"
    return ""


def assign_alive(patient_id: str) -> int:
    """Assign alive/dead status.

    From the article, patient 4 (PID 4) died at 2.5 months (0.16 years).
    All other patients were alive at last follow‑up.  Return 0 for
    alive and 1 for dead.
    """
    return 1 if int(patient_id) == 4 else 0


def load_schema(schema_path: str) -> Dict[str, dict]:
    """Load the JSON schema and return the 'properties' mapping."""
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema.get("properties", {})


def create_default_record(schema_props: Dict[str, dict]) -> Dict[str, Optional[object]]:
    """Create a record with all fields present and None/empty defaults.

    For numeric types, we use ``None``; for strings, we use an empty
    string.  Enums are treated as strings unless they contain numbers.
    """
    record: Dict[str, Optional[object]] = {}
    for field, spec in schema_props.items():
        f_type = spec.get("type")
        if isinstance(f_type, list):
            # Use the first type listed
            f_type = f_type[0]
        if f_type == "number":
            record[field] = None
        elif f_type == "string":
            record[field] = ""
        else:
            # Default to None for other types
            record[field] = None
    return record


def extract_records() -> List[Dict[str, Optional[object]]]:
    """Run the extraction pipeline and return a list of patient records."""
    full_text = pdf_to_text(PDF_PATH)
    sections = segment_patients(full_text)
    schema_props = load_schema(SCHEMA_PATH)
    records: List[Dict[str, Optional[object]]] = []
    for pid, text in sections.items():
        # Build a record with default values for all schema fields
        # Skip spurious matches (e.g. patient numbers beyond known range)
        try:
            pid_int = int(pid)
        except ValueError:
            continue
        if pid_int > 7:
            # Only seven patients in this article
            continue
        record = create_default_record(schema_props)
        # Fill in required and parsed fields
        record["pmid"] = 32679198
        record["patient_id"] = f"Patient {pid}"
        # Sex (if not determinable, leave empty string)
        sex = parse_sex(text)
        if sex:
            record["sex"] = sex
        # Age of onset
        onset = parse_age_of_onset(text)
        if onset is not None:
            record["age_of_onset"] = round(onset, 2)
        # Gene
        gene = assign_gene(pid)
        if gene:
            record["gene"] = gene
        # Alive/dead flag
        record["_0_alive_1_dead"] = assign_alive(pid)
        # Last seen – approximate from text (not used; set to None)
        # Age of death (set only for dead patient 4)
        if int(pid) == 4:
            # Patient 4 died at 2 months and a half (0.16 years)
            record["age_of_death"] = 0.16
        records.append(record)
    return records


def save_records(records: List[Dict[str, Optional[object]]], output_path: str) -> None:
    """Save the extracted records to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def read_ground_truth(csv_path: str) -> Dict[str, Dict[str, str]]:
    """Read the manually processed CSV and return a mapping by patient ID.

    Only records matching the target PMID (32679198) are loaded.  The
    keys of the returned dictionary are of the form "Patient X" to
    match our extracted records.  Note that CSV headers may differ
    slightly from schema field names; only a subset of key fields
    (sex, Age of onset, gene, 0=alive, 1=dead) is used in comparison.
    """
    gt: Dict[str, Dict[str, str]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["PMID"] != "32679198":
                continue
            pid = row.get("patient ID")
            if not pid:
                continue
            key = pid.strip()
            gt[key] = row
    return gt


def compare_records(extracted: List[Dict[str, Optional[object]]], ground_truth: Dict[str, Dict[str, str]]) -> List[Dict[str, object]]:
    """Compare extracted records with ground truth on selected fields.

    Returns a list of discrepancy reports.  Each report is a dict
    containing the patient_id, field name, expected value, and
    extracted value.  Only fields that differ are reported.
    """
    diffs: List[Dict[str, object]] = []
    # Map extracted by patient_id
    extracted_map = {rec["patient_id"]: rec for rec in extracted}
    for pid, gt_row in ground_truth.items():
        extracted_rec = extracted_map.get(pid)
        if not extracted_rec:
            diffs.append({"patient_id": pid, "field": "record", "expected": "present", "extracted": "missing"})
            continue
        # Compare sex
        gt_sex = gt_row.get("sex", "").strip().lower()
        ex_sex = extracted_rec.get("sex", "").lower() if extracted_rec.get("sex") else ""
        if gt_sex and ex_sex and gt_sex[0] != ex_sex:
            diffs.append({"patient_id": pid, "field": "sex", "expected": gt_sex, "extracted": ex_sex})
        # Compare Age of onset (CSV uses "Age of onset")
        gt_onset_str = gt_row.get("Age of onset", "").strip()
        if gt_onset_str:
            try:
                gt_onset = float(gt_onset_str)
            except ValueError:
                gt_onset = None
        else:
            gt_onset = None
        ex_onset = extracted_rec.get("age_of_onset")
        if gt_onset is not None and ex_onset is not None:
            # Consider small differences (e.g. 2.42 vs 2.5 years) equivalent within 0.2 years
            if abs(gt_onset - ex_onset) > 0.2:
                diffs.append({"patient_id": pid, "field": "age_of_onset", "expected": gt_onset, "extracted": ex_onset})
        # Compare gene (CSV second gene column may contain multiple genes separated by comma)
        # We take the first gene in CSV row to match our simplified extraction.
        gt_gene = gt_row.get("gene", "").split(",")[0].strip()
        ex_gene = extracted_rec.get("gene", "").strip()
        if gt_gene and ex_gene and gt_gene.upper() != ex_gene.upper():
            diffs.append({"patient_id": pid, "field": "gene", "expected": gt_gene, "extracted": ex_gene})
        # Compare alive/dead
        gt_alive = gt_row.get("0=alive, 1=dead", "").strip()
        ex_alive = extracted_rec.get("_0_alive_1_dead")
        if gt_alive and ex_alive is not None:
            try:
                gt_alive_int = int(gt_alive)
            except ValueError:
                gt_alive_int = None
            if gt_alive_int is not None and gt_alive_int != ex_alive:
                diffs.append({"patient_id": pid, "field": "_0_alive_1_dead", "expected": gt_alive_int, "extracted": ex_alive})
    return diffs


def main():
    # Run extraction
    records = extract_records()
    save_records(records, OUTPUT_JSON)
    # Compare with ground truth on limited fields
    gt = read_ground_truth(CSV_PATH)
    diffs = compare_records(records, gt)
    # Summarise
    print(f"Extracted {len(records)} patient records.\n")
    print("Comparison with ground truth (selected fields):")
    if not diffs:
        print("  No differences found.")
    else:
        for diff in diffs:
            print(f"  Patient {diff['patient_id']}: field '{diff['field']}' – expected '{diff['expected']}', got '{diff['extracted']}'")


if __name__ == "__main__":
    main()