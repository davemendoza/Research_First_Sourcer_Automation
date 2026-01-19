# © 2026 L. David Mendoza
#
# FILE: config_hardening_day26.py
#
# PURPOSE:
# Centralize tunables and enforce explicit overrides (no silent defaults).
#
# DESIGN:
# - Import-only
# - No filesystem IO
# - No environment-variable reads
# - Explicit override application with fail-closed validation
#
# NOTE:
# This module does not change scoring semantics. It only governs how
# configuration is represented and validated.
#
# IMPORT-ONLY. NO SIDE EFFECTS.

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Dict, Mapping, Optional


class ConfigError(ValueError):
    """Raised when config is invalid or an override is ambiguous."""


@dataclass(frozen=True)
class EngineConfig:
    """
    Frozen defaults.
    Explicit overrides must be applied via apply_overrides_fail_closed().
    """
    max_rows: int = 5000
    max_recovery_per_run: int = 5000
    enable_external_ingestion: bool = True
    enable_public_recovery: bool = True
    determinism_required: bool = True
    strict_no_overwrite: bool = True


DEFAULT_CONFIG = EngineConfig()


_ALLOWED_OVERRIDE_KEYS = set(EngineConfig().__dataclass_fields__.keys())


def validate_config_fail_closed(cfg: EngineConfig) -> None:
    if cfg.max_rows <= 0:
        raise ConfigError("max_rows must be > 0")
    if cfg.max_recovery_per_run <= 0:
        raise ConfigError("max_recovery_per_run must be > 0")


def apply_overrides_fail_closed(
    base: EngineConfig,
    overrides: Optional[Mapping[str, Any]],
) -> EngineConfig:
    """
    Apply explicit overrides with fail-closed behavior:
    - Unknown keys are rejected
    - None values are rejected (no silent defaults)
    - Type mismatches are rejected
    """
    if overrides is None:
        validate_config_fail_closed(base)
        return base

    if not isinstance(overrides, Mapping):
        raise ConfigError("overrides must be a mapping")

    unknown = [k for k in overrides.keys() if k not in _ALLOWED_OVERRIDE_KEYS]
    if unknown:
        raise ConfigError(f"Unknown override keys: {unknown}")

    patch: Dict[str, Any] = {}
    for k, v in overrides.items():
        if v is None:
            raise ConfigError(f"Override '{k}' must not be None")
        patch[k] = v

    cfg = replace(base, **patch)
    validate_config_fail_closed(cfg)
    return cfg
