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

        enrichment_summary = {"example": "placeholder"}
        gpt_summary = {"ok": True, "notes": [], "badges": []}

        combined = {"enrichment": enrichment_summary, "gpt": gpt_summary}
        self._write_summary(run_dir, combined)
        logging.info("Run completed.")
        return run_dir

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["PYTHON_ONLY", "GPT_ONLY", "HYBRID"])
    args = parser.parse_args(argv)

    if args.mode:
        os.environ["MODE"] = args.mode

    Orchestrator().run()

if __name__ == "__main__":
    main()
