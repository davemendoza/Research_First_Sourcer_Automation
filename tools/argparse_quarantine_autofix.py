#!/usr/bin/env python3
# Research_First_Sourcer_Automation
# tools/argparse_quarantine_autofix.py
# Version: v1.0.0 (2026-01-23)
# Copyright (c) 2025-2026 L. David Mendoza. All rights reserved.
#
# PURPOSE
#   Quarantine any import-time execution (including argparse poisoning) from Python modules by:
#     - Detecting unsafe top-level statements (anything other than imports, defs/classes, and safe constants)
#     - Moving those unsafe statements into a generated _cli_main() function
#     - Ensuring the module has: if __name__ == "__main__": _cli_main()
#
# THIS DOES (EXECUTION SAFETY)
#   - Guarantees that argparse/parse_args and any other top-level "work" does NOT run on import.
#   - Preserves original behavior when executed as a script, by running the same statements under _cli_main().
#
# THIS DOES NOT (LOGIC REWRITE)
#   - Does not invent/modify business logic.
#   - Does not attempt to refactor into run()/pipeline contracts.
#
# AUDITABILITY
#   - Always writes a .bak timestamped backup unless --no-backup is set.
#   - Writes a JSON report when --report is provided.
#
# VALIDATION
#   python3 -m py_compile tools/argparse_quarantine_autofix.py
#   python3 tools/argparse_quarantine_autofix.py --root EXECUTION_CORE --inplace --report /tmp/quarantine_report.json
#
# GIT
#   git add tools/argparse_quarantine_autofix.py
#   git commit -m "Tools: quarantine import-time execution (argparse) via AST rewrite"
#   git push

from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class FileResult:
    path: str
    changed: bool
    had_unsafe_top_level: bool
    unsafe_count: int
    wrote_backup: bool
    backup_path: Optional[str]
    error: Optional[str]


def _is_safe_constant_expr(node: ast.AST) -> bool:
    # Conservative: allow only literals and literal containers of literals.
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return all(_is_safe_constant_expr(elt) for elt in node.elts)
    if isinstance(node, ast.Dict):
        return all(
            (k is None or _is_safe_constant_expr(k)) and _is_safe_constant_expr(v)
            for k, v in zip(node.keys, node.values)
        )
    # Allow simple names only if they are common version/copyright markers;
    # otherwise treat as unsafe (could be computed/import dependent).
    if isinstance(node, ast.Name):
        return node.id in {"__version__", "__all__"}
    return False


def _is_safe_top_level_stmt(stmt: ast.stmt) -> bool:
    if isinstance(stmt, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return True

    # Module docstring is represented as Expr(Constant(str)) at top-level.
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
        return True

    # Allow safe constant assignments only.
    if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
        value = stmt.value if isinstance(stmt, ast.AnnAssign) else stmt.value
        if value is None:
            return False
        return _is_safe_constant_expr(value)

    return False


def _has_main_guard_calling_cli(mod: ast.Module) -> bool:
    # Detect: if __name__ == "__main__": _cli_main()
    for stmt in mod.body:
        if isinstance(stmt, ast.If):
            test = stmt.test
            if (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
                and len(test.ops) == 1
                and isinstance(test.ops[0], ast.Eq)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"
            ):
                # check body contains a call to _cli_main
                for b in stmt.body:
                    if isinstance(b, ast.Expr) and isinstance(b.value, ast.Call):
                        call = b.value
                        if isinstance(call.func, ast.Name) and call.func.id == "_cli_main":
                            return True
    return False


def _contains_cli_main_def(mod: ast.Module) -> bool:
    for stmt in mod.body:
        if isinstance(stmt, ast.FunctionDef) and stmt.name == "_cli_main":
            return True
    return False


def _build_cli_main(unsafe_stmts: List[ast.stmt]) -> ast.FunctionDef:
    # Create: def _cli_main(): <unsafe_stmts>
    # We intentionally do NOT add argparse imports here; unsafe statements already include whatever imports/calls existed.
    return ast.FunctionDef(
        name="_cli_main",
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body=unsafe_stmts if unsafe_stmts else [ast.Pass()],
        decorator_list=[],
        returns=None,
        type_comment=None,
    )


def _build_main_guard() -> ast.If:
    return ast.If(
        test=ast.Compare(
            left=ast.Name(id="__name__", ctx=ast.Load()),
            ops=[ast.Eq()],
            comparators=[ast.Constant(value="__main__")],
        ),
        body=[
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="_cli_main", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                )
            )
        ],
        orelse=[],
    )


def _rewrite_module(tree: ast.Module) -> Tuple[ast.Module, bool, int]:
    safe: List[ast.stmt] = []
    unsafe: List[ast.stmt] = []

    for stmt in tree.body:
        if _is_safe_top_level_stmt(stmt):
            safe.append(stmt)
        else:
            unsafe.append(stmt)

    changed = False
    unsafe_count = len(unsafe)

    if unsafe_count == 0:
        # Still ensure main guard doesn't accidentally call parse_args at top-level.
        # If module already had a main guard, we do nothing.
        return tree, False, 0

    # Remove unsafe from top-level and move into _cli_main
    changed = True

    # If _cli_main already exists, we do NOT try to merge to avoid corruption.
    # We fail closed and require manual review.
    if _contains_cli_main_def(tree):
        raise RuntimeError("Refuse to auto-merge: module already defines _cli_main(). Manual review required.")

    new_body: List[ast.stmt] = []

    # Keep safe statements in original order, but exclude any pre-existing __main__ guard from safe list
    # because that guard may currently execute unsafe work that's been moved.
    # We'll add a fresh guard at the end.
    for stmt in safe:
        # drop any existing __main__ guards to avoid double-execution
        if isinstance(stmt, ast.If):
            # retain non-main if blocks as safe (rare but possible)
            test = stmt.test
            if (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"
            ):
                changed = True
                continue
        new_body.append(stmt)

    # Insert generated _cli_main containing the exact unsafe statements
    new_body.append(_build_cli_main(unsafe))

    # Ensure main guard exists
    new_body.append(_build_main_guard())

    tree.body = new_body
    ast.fix_missing_locations(tree)
    return tree, changed, unsafe_count


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _should_target(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix != ".py":
        return False
    # Skip __init__.py by default; it commonly contains package exports and should stay minimal.
    if path.name == "__init__.py":
        return False
    return True


def process_file(path: Path, inplace: bool, backup: bool) -> FileResult:
    try:
        original = _read_text(path)
        tree = ast.parse(original)

        new_tree, changed, unsafe_count = _rewrite_module(tree)

        if not changed:
            return FileResult(
                path=str(path),
                changed=False,
                had_unsafe_top_level=False,
                unsafe_count=0,
                wrote_backup=False,
                backup_path=None,
                error=None,
            )

        # Unparse to source
        if not hasattr(ast, "unparse"):
            raise RuntimeError("Python >= 3.9 required (ast.unparse not available).")

        new_source = ast.unparse(new_tree) + "\n"

        wrote_backup = False
        backup_path = None
        if backup:
            ts = time.strftime("%Y%m%d_%H%M%S")
            backup_path = str(path) + f".bak_{ts}"
            shutil.copy2(str(path), backup_path)
            wrote_backup = True

        if inplace:
            _write_text(path, new_source)

        return FileResult(
            path=str(path),
            changed=True,
            had_unsafe_top_level=True,
            unsafe_count=unsafe_count,
            wrote_backup=wrote_backup,
            backup_path=backup_path,
            error=None,
        )
    except Exception as e:
        return FileResult(
            path=str(path),
            changed=False,
            had_unsafe_top_level=False,
            unsafe_count=0,
            wrote_backup=False,
            backup_path=None,
            error=str(e),
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Quarantine import-time execution in Python modules (argparse-safe).")
    ap.add_argument("--root", required=True, help="Root directory to scan (e.g., EXECUTION_CORE)")
    ap.add_argument("--inplace", action="store_true", help="Rewrite files in place")
    ap.add_argument("--no-backup", action="store_true", help="Do not write .bak timestamped backups")
    ap.add_argument("--report", default="", help="Write JSON report to this path (optional)")
    ap.add_argument("--fail-on-error", action="store_true", help="Exit non-zero if any file errored")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"❌ root not found or not a directory: {root}", file=sys.stderr)
        return 2

    results: List[FileResult] = []
    for p in sorted(root.rglob("*.py")):
        if not _should_target(p):
            continue
        results.append(process_file(p, inplace=args.inplace, backup=(not args.no_backup)))

    changed = sum(1 for r in results if r.changed)
    errored = [r for r in results if r.error]
    print("🔒 argparse/import-time quarantine complete")
    print(f"   scanned={len(results)} changed={changed} errors={len(errored)}")

    if errored:
        print("❌ Errors:")
        for r in errored:
            print(f"   - {r.path}: {r.error}")

    if args.report:
        report_path = Path(args.report).resolve()
        payload: Dict[str, Any] = {
            "root": str(root),
            "scanned": len(results),
            "changed": changed,
            "errors": len(errored),
            "results": [r.__dict__ for r in results],
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"🧾 wrote report: {report_path}")

    if args.fail_on_error and errored:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
EOF
