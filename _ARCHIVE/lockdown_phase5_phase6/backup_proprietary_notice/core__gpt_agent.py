# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved.

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

@dataclass
class GPTConfig:
    api_key: Optional[str] = None
    model: str = "gpt-4.1-mini"
    mode: str = "HYBRID"
    log_level: str = "INFO"

class GPTAgent:
    """
    GPT is the reasoning and orchestration brain.
    Validates enrichment outputs. Suggests schema corrections.
    Generates dashboard badges and audit notes.
    """

    def __init__(self, config: Optional[GPTConfig] = None) -> None:
        cfg = config or self._from_env()
        self.config = cfg

        logging.basicConfig(
            level=getattr(logging, cfg.log_level.upper(), logging.INFO),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

        if openai is None:
            logger.warning(
                "openai library not installed. Install with pip install openai."
            )
        else:
            openai.api_key = cfg.api_key

    @staticmethod
    def _from_env() -> GPTConfig:
        return GPTConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            mode=os.getenv("MODE", "HYBRID").upper(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def _ensure(self) -> None:
        if openai is None:
            raise RuntimeError("openai library missing")
        if not self.config.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

    def chat(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> str:
        self._ensure()

        resp = openai.ChatCompletion.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        return resp["choices"][0]["message"]["content"]

    def review_enrichment_batch(self, run_dir: Path, batch_summary: Dict[str, Any], schema_version: str) -> Dict[str, Any]:
        system_prompt = (
            "You are the reasoning engine for a talent enrichment system. "
            "Respond only in JSON. Provide schema validation notes, audit hints, and badges."
        )
        user_payload = {
            "schema_version": schema_version,
            "run_dir": str(run_dir),
            "batch_summary": batch_summary,
        }

        try:
            raw = self.chat(system_prompt, json.dumps(user_payload), temperature=0.1)
            data = json.loads(raw)
        except Exception as exc:
            return {
                "ok": False,
                "error": str(exc),
                "notes": [],
                "badges": [],
            }

        data.setdefault("ok", True)
        data.setdefault("notes", [])
        data.setdefault("badges", [])
        return data

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
