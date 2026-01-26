"""
EXECUTION_CORE/run_safe.py
============================================================
SINGLE AUTHORITATIVE PIPELINE ENTRYPOINT (LOCKED, REWIRED)

Maintainer: L. David Mendoza © 2026
Version: v3.3.0 (Gold-standard wiring, execution observability)

What this enforces (LOCKED)
- Seeds resolved ONLY via seed_locator.py
- Outputs routed ONLY via output_namer.py (unique timestamped filenames + LATEST.csv)
- OUTPUTS root contract enforced via output_guard.py
- Deterministic post-run narrative densification wired (post_run_narrative_pass.py)
- Fail-closed integrity gate wired (csv_integrity_guard.py)

Execution observability (NEW, fail-open, never blocks the run)
- RuntimeTracker live progress snapshot (rows, elapsed, rate, ETA)
- ProgressHeartbeat periodic status output
- EnrichmentCounters live counters (emails/phones/github.io/cv/oss)
- TalentIntelPreview live preview line output
- Completion notifier always fires (success or failure)

Pipeline (deterministic)
seed -> anchors -> github -> name -> role_materialize -> schema81 -> phase6 -> phase7
-> post_run_narrative -> canonical write -> integrity_guard -> notify

Usage
AI_TALENT_MODE=demo|scenario|gpt_slim python3 -m EXECUTION_CORE.run_safe <scenario_key>
python3 -m EXECUTION_CORE.run_safe --list-roles
"""
from __future__ import annotations
import csv
import os
import shutil
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
PIPELINE_VERSION = 'D30_LOCKED_GOLD_FINAL'

def die(msg: str) -> None:
    print(f'❌ {msg}', file=sys.stderr)
    sys.exit(1)

def require(cond: bool, msg: str) -> None:
    if not cond:
        die(msg)

def now_timestamp_compact() -> str:
    return time.strftime('%Y%m%d_%H%M%S')

def now_timestamp_human() -> str:
    return time.strftime('%Y-%m-%d_%H-%M-%S')

def _resolve_mode() -> str:
    env_mode = (os.environ.get('AI_TALENT_MODE') or '').strip().lower()
    if env_mode in ('demo', 'scenario', 'gpt_slim'):
        return env_mode
    return 'demo'

def _count_csv_rows(path: Path) -> int:
    try:
        with path.open(newline='', encoding='utf-8') as f:
            r = csv.reader(f)
            _ = next(r, None)
            return sum((1 for _ in r))
    except Exception:
        return -1

def _safe_read_header(path: Path) -> List[str]:
    try:
        with path.open(newline='', encoding='utf-8') as f:
            r = csv.reader(f)
            header = next(r, None)
            return list(header or [])
    except Exception:
        return []

def _count_nonempty_in_columns(path: Path, col_candidates: List[List[str]]) -> Dict[str, int]:
    """
    Counts non-empty cells for a small set of signal columns.
    This is intentionally conservative and file-based so it works without modifying upstream passes.
    It runs on an interval, not per row.
    """
    out = {'emails_found': 0, 'phones_found': 0, 'github_io_found': 0, 'cv_links_found': 0, 'oss_signals_found': 0}
    try:
        with path.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return out
            fields = set(reader.fieldnames)

            def resolve_cols(cands: List[str]) -> List[str]:
                return [c for c in cands if c in fields]
            email_cols = resolve_cols(col_candidates[0])
            phone_cols = resolve_cols(col_candidates[1])
            ghio_cols = resolve_cols(col_candidates[2])
            cv_cols = resolve_cols(col_candidates[3])
            oss_cols = resolve_cols(col_candidates[4])
            for row in reader:
                if email_cols and any(((row.get(c, '') or '').strip() for c in email_cols)):
                    out['emails_found'] += 1
                if phone_cols and any(((row.get(c, '') or '').strip() for c in phone_cols)):
                    out['phones_found'] += 1
                if ghio_cols and any(((row.get(c, '') or '').strip() for c in ghio_cols)):
                    out['github_io_found'] += 1
                if cv_cols and any(((row.get(c, '') or '').strip() for c in cv_cols)):
                    out['cv_links_found'] += 1
                if oss_cols and any(((row.get(c, '') or '').strip() for c in oss_cols)):
                    out['oss_signals_found'] += 1
            return out
    except Exception:
        return out
from EXECUTION_CORE.ai_role_registry import list_roles
from EXECUTION_CORE.output_guard import enforce_outputs_root_clean
from EXECUTION_CORE.output_namer import build_paths
from EXECUTION_CORE.seed_locator import resolve_seed_csv, SeedResolutionError
from EXECUTION_CORE.csv_integrity_guard import enforce_csv_integrity, CSVIntegrityError
from EXECUTION_CORE.runtime_tracker import RuntimeTracker
from EXECUTION_CORE.progress_heartbeat import ProgressHeartbeat
from EXECUTION_CORE.enrichment_counters import EnrichmentCounters
from EXECUTION_CORE.talent_intel_preview import TalentIntelPreview
from EXECUTION_CORE.completion_notifier import notify_completion
from EXECUTION_CORE.people_scenario_resolver import resolve_scenario
from EXECUTION_CORE.anchor_exhaustion_pass import process_csv as anchors_process_csv
from EXECUTION_CORE.people_source_github import process_csv as github_process_csv
from EXECUTION_CORE.name_resolution_pass import process_csv as name_process_csv
from EXECUTION_CORE.row_role_materialization_pass import process_csv as role_materialize_process_csv
from EXECUTION_CORE.canonical_schema_mapper import process_csv as schema_map_process_csv
from EXECUTION_CORE.phase6_ai_stack_signals import process_csv as phase6_process_csv
from EXECUTION_CORE.phase7_oss_contribution_intel import process_csv as phase7_process_csv
from EXECUTION_CORE.post_run_narrative_pass import process_csv as post_run_narrative_process_csv
from EXECUTION_CORE.canonical_people_writer import write_canonical_people_csv

class _LiveStageMonitor(threading.Thread):
    """
    Live monitor to keep RuntimeTracker and counters moving during long stage runs.

    - Watches current stage output file row count and updates tracker rows_completed.
    - Periodically recomputes enrichment counters by scanning the current output file.
    - Emits TalentIntelPreview periodically.
    - Never raises. Never blocks the pipeline.
    """

    def __init__(self, tracker: RuntimeTracker, counters: EnrichmentCounters, preview: TalentIntelPreview, get_stage_state: callable, interval_sec: int=15, counters_interval_sec: int=60) -> None:
        super().__init__(daemon=True)
        self._tracker = tracker
        self._counters = counters
        self._preview = preview
        self._get_stage_state = get_stage_state
        self._interval = max(5, int(interval_sec))
        self._counters_interval = max(20, int(counters_interval_sec))
        self._stop = threading.Event()
        self._last_rows_seen: int = 0
        self._last_counters_ts: float = 0.0
        self._last_mtime: float = 0.0
        self._col_candidates = [['Primary_Email', 'Work_Email', 'Home_Email', 'Email', 'Emails'], ['Primary_Phone', 'Mobile_Phone', 'Work_Phone', 'Phone', 'Phones'], ['GitHub_IO_URL', 'Github_IO_URL', 'Github.io', 'GitHub.io', 'GitHub_IO', 'Github_IO'], ['Resume_Link', 'Resume_URL', 'CV_Link', 'CV_URL', 'Resume', 'CV', 'Resume_URLs'], ['Open_Source_Impact_Note', 'GitHub_Repo_Evidence_Why', 'Key_GitHub_AI_Repos', 'OSS_Evidence', 'OSS_Signals']]

    def stop(self) -> None:
        self._stop.set()

    def _update_rows_from_file(self, out_path: Optional[Path]) -> None:
        if not out_path or not out_path.exists():
            return
        try:
            mtime = out_path.stat().st_mtime
            if mtime == self._last_mtime:
                return
            self._last_mtime = mtime
            n = _count_csv_rows(out_path)
            if n >= 0 and n > self._last_rows_seen:
                delta = n - self._last_rows_seen
                self._last_rows_seen = n
                try:
                    self._tracker.increment(delta)
                except Exception:
                    pass
        except Exception:
            return

    def _recompute_counters(self, out_path: Optional[Path]) -> None:
        if not out_path or not out_path.exists():
            return
        now = time.time()
        if now - self._last_counters_ts < self._counters_interval:
            return
        self._last_counters_ts = now
        try:
            counts = _count_nonempty_in_columns(out_path, self._col_candidates)
            snap = self._counters.snapshot()
            for k, v in counts.items():
                cur = int(snap.get(k, 0))
                target = int(v)
                if target > cur:
                    self._counters.increment(k, target - cur)
        except Exception:
            return

    def run(self) -> None:
        while not self._stop.is_set():
            try:
                stage_name, stage_out_path = self._get_stage_state()
                self._update_rows_from_file(stage_out_path)
                self._recompute_counters(stage_out_path)
                try:
                    self._preview.maybe_emit()
                except Exception:
                    pass
            except Exception:
                pass
            self._stop.wait(self._interval)

def main(argv: List[str]) -> None:
    if len(argv) != 2:
        die('Usage: AI_TALENT_MODE=demo|scenario|gpt_slim python3 -m EXECUTION_CORE.run_safe <scenario_key>')
    scenario_key = argv[1].strip()
    if scenario_key == '--list-roles':
        print('\nCanonical AI Role Types:\n')
        for r in list_roles():
            print(f' - {r}')
        sys.exit(0)
    require(bool(scenario_key), 'Scenario key must be non-empty')
    mode = _resolve_mode()
    ts_compact = now_timestamp_compact()
    ts_human = now_timestamp_human()
    OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)
    enforce_outputs_root_clean(REPO_ROOT)
    scenario: Dict[str, Any] = resolve_scenario(scenario_key)
    require(isinstance(scenario, dict), 'Scenario resolver must return dict')
    for k in ('SCENARIO_PREFIX', 'SCENARIO_SEED', 'ROLE_CANONICAL'):
        require(k in scenario and isinstance(scenario[k], str) and scenario[k].strip(), f'Missing/invalid scenario key: {k}')
    prefix = scenario['SCENARIO_PREFIX'].strip()
    seed_key = scenario['SCENARIO_SEED'].strip()
    role = scenario['ROLE_CANONICAL'].strip()
    print('✓ Scenario resolved')
    print(f'  PREFIX: {prefix}')
    print(f'  SEED:   {seed_key}')
    print(f'  ROLE:   {role}')
    print(f'  MODE:   {mode}')
    os.environ['AI_TALENT_ROLE_CANONICAL'] = role
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    try:
        seed_csv = resolve_seed_csv(repo_root=REPO_ROOT, prefix=seed_key, mode=mode)
    except SeedResolutionError as e:
        die(str(e))
    require(seed_csv.exists(), f'Resolved seed path does not exist: {seed_csv}')
    print(f'  SEED_CSV: {seed_csv}')
    seed_rows = _count_csv_rows(seed_csv)
    if seed_rows < 0:
        seed_rows = 0
    tracker: Optional[RuntimeTracker] = None
    heartbeat: Optional[ProgressHeartbeat] = None
    counters: Optional[EnrichmentCounters] = None
    preview: Optional[TalentIntelPreview] = None
    monitor: Optional[_LiveStageMonitor] = None
    current_stage: str = 'init'
    current_out: Optional[Path] = None

    def get_stage_state() -> Tuple[str, Optional[Path]]:
        return (current_stage, current_out)

    def snapshot_wrapped() -> Dict[str, Any]:
        snap = {}
        if tracker:
            try:
                snap = tracker.snapshot()
            except Exception:
                snap = {}
        snap['stage'] = current_stage
        if counters:
            try:
                snap['counters'] = counters.snapshot()
            except Exception:
                snap['counters'] = {}
        return snap
    p1 = WORK_DIR / f'{prefix}__01_anchors.csv'
    p2 = WORK_DIR / f'{prefix}__02_github.csv'
    p3 = WORK_DIR / f'{prefix}__03_named.csv'
    p3b = WORK_DIR / f'{prefix}__03b_role_bound.csv'
    p4 = WORK_DIR / f'{prefix}__04_schema_81.csv'
    p5 = WORK_DIR / f'{prefix}__05_phase6.csv'
    p6 = WORK_DIR / f'{prefix}__06_phase7.csv'
    p7 = WORK_DIR / f'{prefix}__07_post_run_narrative.csv'
    success = False
    out_csv: Optional[Path] = None
    try:
        try:
            tracker = RuntimeTracker(total_rows=seed_rows if seed_rows > 0 else 0)
            counters = EnrichmentCounters()
            preview = TalentIntelPreview(runtime_snapshot_fn=snapshot_wrapped, counters_snapshot_fn=counters.snapshot if counters else lambda: {}, interval_sec=60)
            heartbeat = ProgressHeartbeat(snapshot_fn=snapshot_wrapped, interval_sec=30)
            heartbeat.start()
            monitor = _LiveStageMonitor(tracker=tracker, counters=counters, preview=preview, get_stage_state=get_stage_state)
            monitor.start()
        except Exception:
            tracker = None
            counters = None
            preview = None
            heartbeat = None
            monitor = None
        current_stage = 'anchors'
        current_out = p1
        anchors_process_csv(str(seed_csv), str(p1))
        require(p1.exists(), f'Anchor output missing: {p1}')
        current_stage = 'github'
        current_out = p2
        github_process_csv(str(p1), str(p2))
        require(p2.exists(), f'GitHub output missing: {p2}')
        current_stage = 'name'
        current_out = p3
        name_process_csv(str(p2), str(p3))
        require(p3.exists(), f'Name output missing: {p3}')
        current_stage = 'role_materialize'
        current_out = p3b
        role_materialize_process_csv(str(p3), str(p3b))
        require(p3b.exists(), f'Role materialization output missing: {p3b}')
        current_stage = 'schema81'
        current_out = p4
        schema_map_process_csv(str(p3b), str(p4))
        require(p4.exists(), f'Schema81 output missing: {p4}')
        current_stage = 'phase6'
        current_out = p5
        phase6_process_csv(str(p4), str(p5))
        require(p5.exists(), f'Phase6 output missing: {p5}')
        current_stage = 'phase7'
        current_out = p6
        phase7_process_csv(str(p5), str(p6))
        require(p6.exists(), f'Phase7 output missing: {p6}')
        current_stage = 'post_run_narrative'
        current_out = p7
        post_run_narrative_process_csv(str(p6), str(p7))
        require(p7.exists(), f'Post-run narrative output missing: {p7}')
        current_stage = 'canonical_write'
        current_out = None
        paths = build_paths(prefix=prefix, mode=mode, ts_human=ts_human, repo_root=REPO_ROOT)
        if paths.canonical_csv.exists():
            die(f'Refusing to overwrite existing canonical CSV: {paths.canonical_csv}')
        canonical_out = write_canonical_people_csv(canonical_csv_path=str(p7), output_dir=str(paths.out_dir), output_prefix=paths.role_slug, timestamp=ts_compact, fixed_filename=paths.canonical_csv.name, pipeline_version=PIPELINE_VERSION, metadata_json_path=str(paths.metadata_json))
        out_csv = Path(canonical_out).resolve()
        require(out_csv.exists(), f'Canonical CSV was not written: {out_csv}')
        try:
            shutil.copyfile(str(out_csv), str(paths.latest_csv))
        except Exception as e:
            die(f'Failed to update LATEST.csv: {e}')
        current_stage = 'integrity_guard'
        current_out = out_csv
        try:
            enforce_csv_integrity(out_csv)
        except CSVIntegrityError as e:
            die(str(e))
        success = True
    finally:
        try:
            if monitor:
                monitor.stop()
        except Exception:
            pass
        try:
            if heartbeat:
                heartbeat.stop()
        except Exception:
            pass
        try:
            if tracker:
                tracker.mark_done()
        except Exception:
            pass
        if out_csv and out_csv.exists() and PREVIEW_SCRIPT.exists():
            try:
                import subprocess
                subprocess.run([sys.executable, str(PREVIEW_SCRIPT), str(out_csv), mode, prefix], cwd=str(REPO_ROOT))
            except Exception:
                pass
        try:
            if tracker:
                notify_completion(tracker.snapshot())
        except Exception:
            pass
    rows_written = _count_csv_rows(out_csv) if out_csv else -1
    print('\n✔ PIPELINE COMPLETE' if success else '\n❌ PIPELINE FAILED')
    if out_csv:
        print('✔ Canonical CSV:', out_csv)
    print('✔ Rows:', rows_written)
    print('✔ Timestamp:', ts_compact)

def _cli_main():
    REPO_ROOT = Path(__file__).resolve().parents[1]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    EXECUTION_DIR = REPO_ROOT / 'EXECUTION_CORE'
    OUTPUTS_ROOT = REPO_ROOT / 'OUTPUTS'
    WORK_DIR = REPO_ROOT / '_work'
    PREVIEW_SCRIPT = EXECUTION_DIR / 'talent_intel_preview.py'
    if __name__ == '__main__':
        main(sys.argv)
    EOF
if __name__ == '__main__':
    _cli_main()
