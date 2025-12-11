# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
import pandas as pd
import re
from typing import Dict, Any, List

class SchemaEnricher:
    """
    Phase 6 Enrichment Engine.
    Consumes validated sheets + schema rules and produces deterministic,
    role-specific enrichment across Strengths, Weaknesses, Signal_Score,
    and explicit schema signal columns.
    """

    def __init__(self, taxonomy: Dict[str, List[str]], logger=None):
        self.taxonomy = taxonomy
        self.logger = logger

    # ----------------------------------------------------------
    # Core Normalization
    # ----------------------------------------------------------
    def normalize_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        return text.lower().strip()

    def tokenize_fields(self, row: pd.Series, fields: List[str]) -> str:
        parts = []
        for f in fields:
            val = row.get(f, "")
            if isinstance(val, str):
                parts.append(val.lower())
        return " ".join(parts)

    # ----------------------------------------------------------
    # Signal Matching Core
    # ----------------------------------------------------------
    def detect_signals(self, text: str, rule_set: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Each schema includes 4–6 signal columns.
        This performs the deterministic AI taxonomy matching for each column.
        """
        matches = {}

        for signal_column, term_list in rule_set["schema_columns"].items():
            found = []
            for term in term_list:
                pattern = r"\b" + re.escape(term.lower()) + r"\b"
                if re.search(pattern, text):
                    found.append(term)
            matches[signal_column] = list(set(found))

        return matches

    # ----------------------------------------------------------
    # Signal Score Logic
    # ----------------------------------------------------------
    def compute_signal_score(self, signal_dict: Dict[str, List[str]]) -> str:
        """
        Score based on count of populated schema columns.
        High = 3–4 strong matches
        Medium = 1–2 strong matches
        Low = 0 or weak context
        """
        count = sum(1 for v in signal_dict.values() if len(v) > 0)

        if count >= 3:
            return "High"
        elif count >= 1:
            return "Medium"
        return "Low"

    # ----------------------------------------------------------
    # Strengths / Weaknesses Narrative
    # ----------------------------------------------------------
    def build_strengths(self, role_type: str, signals: Dict[str, List[str]], row_text: str) -> str:
        """
        Role-type narrative logic (Parasail-aligned).
        Uses explicit technical evidence; no generics.
        """
        evidence = []

        if signals.get("LLM_Core_Matches"):
            evidence.append(f"Shows explicit LLM exposure ({', '.join(signals['LLM_Core_Matches'])}).")

        if signals.get("RAG_Workflow_Details"):
            evidence.append("Demonstrated RAG workflow experience with verified framework terms.")

        if signals.get("VectorDB_Technologies"):
            evidence.append("Clear vector DB fluency through mentions of Pinecone, Weaviate, FAISS, or equivalents.")

        if signals.get("Inference_Stack_Optimization"):
            evidence.append("Experience optimizing inference stacks with vLLM, TensorRT, Triton, or llama.cpp.")

        if not evidence:
            return "No determinative technical strengths identified beyond general experience."

        return " ".join(evidence)

    def build_weaknesses(self, role_type: str, signals: Dict[str, List[str]], row_text: str) -> str:
        """
        Identifies real gaps. No placeholders. Uses strict taxonomy rules.
        """
        gaps = []

        if not signals.get("LLM_Core_Matches"):
            gaps.append("No explicit LLM family references detected.")

        if "deployment" not in row_text and "serve" not in row_text:
            gaps.append("Limited evidence of production deployment or inference scaling.")

        if not signals.get("VectorDB_Technologies"):
            gaps.append("No vector database alignment found.")

        if not gaps:
            return "No major technical gaps surfaced."

        return " ".join(gaps)

    # ----------------------------------------------------------
    # Main Enrichment Routine
    # ----------------------------------------------------------
    def enrich_sheet(self, sheet_df: pd.DataFrame, role_type: str, rules: Dict[str, Any]) -> pd.DataFrame:
        """
        Executes the full Phase 6 enrichment workflow.
        """
        fields_to_scan = ["Title", "Headline", "Summary", "Skills", "Experience"]

        output_df = sheet_df.copy()

        for idx, row in output_df.iterrows():

            # Merge all free-text fields
            joined_text = self.tokenize_fields(row, fields_to_scan)

            # Determine schema-matched signals
            signals = self.detect_signals(joined_text, rules)

            # Fill schema columns with explicit terms
            for col, items in signals.items():
                output_df.at[idx, col] = ", ".join(items) if items else ""

            # Calculate score
            score = self.compute_signal_score(signals)
            output_df.at[idx, "Signal_Score"] = score

            # Strengths / Weaknesses
            strengths = self.build_strengths(role_type, signals, joined_text)
            weaknesses = self.build_weaknesses(role_type, signals, joined_text)

            output_df.at[idx, "Strengths"] = strengths
            output_df.at[idx, "Weaknesses"] = weaknesses

        return output_df

    # ----------------------------------------------------------
    # Write Output
    # ----------------------------------------------------------
    def write_output(self, writer, df: pd.DataFrame, sheet_name: str):
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        if self.logger:
            self.logger.info(f"✓ Enriched sheet saved: {sheet_name}")

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
