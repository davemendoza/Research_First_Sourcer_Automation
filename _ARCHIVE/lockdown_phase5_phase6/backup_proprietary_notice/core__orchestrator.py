# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved.

import argparse
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.gpt_agent import GPTAgent, GPTConfig
from enrichers.pipeline import run_enrichment_pipeline

logger = logging.getLogger(__name__)

@dataclass
class OrchestratorConfig:
    mode: str = "HYBRID"
    inputs_dir: Path = Path("inputs")
    outputs_dir: Path = Path("outputs")
    logs_dir: Path = Path("logs")
    schema_version: str = "v3.8.0"

class Orchestrator:

    def __init__(self, cfg: Optional[OrchestratorConfig] = None, gpt_cfg: Optional[GPTConfig] = None):
        self.cfg = cfg or self._from_env()
        self.gpt_agent = GPTAgent(gpt_cfg)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

        self.cfg.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.cfg.logs_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _from_env() -> OrchestratorConfig:
        mode = os.getenv("MODE", "HYBRID").upper()
        return OrchestratorConfig(
            mode=mode,
            inputs_dir=Path(os.getenv("INPUTS_DIR", "inputs")),
            outputs_dir=Path(os.getenv("OUTPUTS_DIR", "outputs")),
            logs_dir=Path(os.getenv("LOGS_DIR", "logs")),
            schema_version=os.getenv("SCHEMA_VERSION", "v3.8.0"),
        )

    def _new_run(self) -> Path:
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        run_dir = self.cfg.outputs_dir / f"run_{stamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _write_summary(self, run_dir: Path, data: Dict[str, Any]) -> None:
        out = self.cfg.logs_dir / "latest_run_summary.json"
        out.write_text(json.dumps({
            "run_dir": str(run_dir),
            "schema_version": self.cfg.schema_version,
            "summary": data,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        }, indent=2))

    def run(self) -> Path:
        run_dir = self._new_run()

        logging.info("Starting orchestrator run into %s", run_dir)

        enrichment_summary = {}
        if self.cfg.mode in {"PYTHON_ONLY", "HYBRID"}:
            enrichment_summary = run_enrichment_pipeline(
                inputs_dir=self.cfg.inputs_dir,
                run_dir=run_dir,
                schema_version=self.cfg.schema_version,
            )

        gpt_summary = {}
        if self.cfg.mode in {"GPT_ONLY", "HYBRID"}:
            gpt_summary = self.gpt_agent.review_enrichment_batch(
                run_dir=run_dir,
                batch_summary=enrichment_summary,
                schema_version=self.cfg.schema_version,
            )

        combined = {"enrichment": enrichment_summary, "gpt": gpt_summary}
        self._write_summary(run_dir, combined)

        logging.info("Run completed.")
        return run_dir

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["PYTHON_ONLY", "GPT_ONLY", "HYBRID"])
    parser.add_argument("--inputs", type=str)
    args = parser.parse_args(argv)

    if args.mode:
        os.environ["MODE"] = args.mode
    if args.inputs:
        os.environ["INPUTS_DIR"] = args.inputs

    Orchestrator().run()

if __name__ == "__main__":
    main()

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
