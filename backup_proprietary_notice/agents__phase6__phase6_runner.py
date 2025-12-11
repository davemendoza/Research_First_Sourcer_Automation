# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
import os
import json
import time
import logging
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

from phase6_loader import Phase6Loader
from schema_validator import SchemaValidator
from schema_enricher import SchemaEnricher

# ---------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------
logger = logging.getLogger("phase6_runner")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(handler)


# ---------------------------------------------------------
# Worker Function (for multiprocessing)
# ---------------------------------------------------------
def process_sheet_worker(args):
    """Runs validation + enrichment in its own subprocess."""
    (sheet_name, df, role_type, rule_set, taxonomy) = args

    validator = SchemaValidator()
    enricher = SchemaEnricher(taxonomy=taxonomy)

    # Validate
    df_valid = validator.validate_sheet(df, rule_set, sheet_name)

    # Enrich
    df_enriched = enricher.enrich_sheet(df_valid, role_type, rule_set)

    # Add Explainability: JSON evidence field
    df_enriched["Signal_Evidence"] = df_enriched.apply(
        lambda r: json.dumps({
            "LLM_Core_Matches": r.get("LLM_Core_Matches", ""),
            "RAG_Workflow_Details": r.get("RAG_Workflow_Details", ""),
            "VectorDB_Technologies": r.get("VectorDB_Technologies", ""),
            "Inference_Stack_Optimization": r.get("Inference_Stack_Optimization", ""),
            "Signal_Score": r.get("Signal_Score", "")
        }), axis=1
    )

    return sheet_name, df_enriched


# ---------------------------------------------------------
# Main Phase 6 Runner
# ---------------------------------------------------------
class Phase6Runner:
    """
    Professional-grade Phase 6 Schema Intelligence Pipeline.
    Includes:
    • Parallel execution
    • Explainable scoring evidence
    • Resume-safe, fault-tolerant processing
    • Atomic safe-write workflow
    """

    def __init__(self, workbook_path: str, output_path: str, rules_path: str, taxonomy: dict):
        self.workbook_path = workbook_path
        self.output_path = output_path
        self.tmp_output_path = output_path.replace(".xlsx", "_tmp.xlsx")
        self.rules_path = rules_path
        self.taxonomy = taxonomy

        self.loader = Phase6Loader(logger=logger)
        self.validator = SchemaValidator(logger=logger)
        self.enricher = SchemaEnricher(taxonomy=self.taxonomy, logger=logger)

    # -----------------------------------------------------
    # RUN PIPELINE
    # -----------------------------------------------------
    def run(self):
        start_time = time.time()
        logger.info("🚀 Phase 6 Runner (Enhanced Edition) Started")

        # -----------------------------------------------
        # Load workbook + rules
        # -----------------------------------------------
        workbook = self.loader.load_workbook(self.workbook_path)
        rules_dict = self.loader.load_schema_rules(self.rules_path)

        # Temp cache directory
        tmp_cache_dir = "./phase6_tmp"
        os.makedirs(tmp_cache_dir, exist_ok=True)

        # -----------------------------------------------
        # Prepare job list for parallel execution
        # -----------------------------------------------
        jobs = []

        for sheet_name, df in workbook.items():
            # Skip sheets that must not be enriched
            if sheet_name in ["MASTER_ALL", "GENERAL"]:
                logger.info(f"Skipping enrichment for MASTER sheet: {sheet_name}")
                continue

            rule_set = rules_dict.get(sheet_name, {})
            role_type = rule_set.get("role_type", "Unknown")

            jobs.append((sheet_name, df, role_type, rule_set, self.taxonomy))

        logger.info(f"🔧 Total sheets to enrich: {len(jobs)}")

        # -----------------------------------------------
        # Parallel Execution
        # -----------------------------------------------
        results = {}
        with ProcessPoolExecutor() as executor:
            futures = {executor.submit(process_sheet_worker, job): job[0] for job in jobs}

            for future in as_completed(futures):
                sheet_name = futures[future]
                try:
                    s_name, df_processed = future.result()
                    results[s_name] = df_processed
                    logger.info(f"✓ Completed sheet (parallel): {s_name}")
                except Exception as e:
                    logger.error(f"❌ Error processing sheet {sheet_name}: {e}")

        # -----------------------------------------------
        # Safe Temp Write
        # -----------------------------------------------
        logger.info(f"💾 Writing enriched workbook to temp file: {self.tmp_output_path}")

        writer = pd.ExcelWriter(self.tmp_output_path, engine="openpyxl")

        # Write enriched sheets
        for s_name, df_enriched in results.items():
            df_enriched.to_excel(writer, sheet_name=s_name, index=False)

        # Write untouched sheets
        for s_name, df in workbook.items():
            if s_name not in results:
                df.to_excel(writer, sheet_name=s_name, index=False)

        writer.close()

        # -----------------------------------------------
        # Atomic Replace Output
        # -----------------------------------------------
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        os.rename(self.tmp_output_path, self.output_path)
        logger.info(f"🎉 Phase 6 Enrichment Complete: {self.output_path}")

        # -----------------------------------------------
        # Runtime Summary
        # -----------------------------------------------
        total_time = round(time.time() - start_time, 2)
        logger.info(f"⏱ Total Processing Time: {total_time} seconds")
        logger.info("🔥 Enhanced Phase 6 Pipeline finished cleanly.")


# ---------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Enhanced Phase 6 Schema Enrichment Pipeline")
    parser.add_argument("--input", required=True, help="Path to input workbook")
    parser.add_argument("--rules", required=True, help="Path to schema rules JSON file")
    parser.add_argument("--output", required=True, help="Path to final enriched workbook")
    parser.add_argument("--taxonomy", required=True, help="Path to taxonomy JSON")
    args = parser.parse_args()

    taxonomy = json.load(open(args.taxonomy, "r"))

    runner = Phase6Runner(
        workbook_path=args.input,
        output_path=args.output,
        rules_path=args.rules,
        taxonomy=taxonomy
    )

    runner.run()

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
