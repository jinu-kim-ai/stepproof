"""Run models over the benchmark and verify every solution step."""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .models import get_model
from .problems import Problem
from .verifier import verify


def evaluate_model(model, problems: list[Problem], workers: int = 1) -> list[dict]:
    def one(p: Problem) -> dict:
        try:
            sol = model.solve(p)
        except Exception as exc:  # API failure etc. -> record, don't crash the run
            return _row(model.name, p, None, error=f"{type(exc).__name__}: {exc}")
        return _row(model.name, p, sol)

    if workers > 1:
        with ThreadPoolExecutor(workers) as pool:
            return list(pool.map(one, problems))
    return [one(p) for p in problems]


def _row(model_name: str, p: Problem, sol, error: str = "") -> dict:
    base = {"model": model_name, "problem_id": p.id, "domain": p.domain, "topic": p.topic,
            "statement": p.statement, "expected_answer": p.answer}
    if sol is None:
        return {**base, "final_correct": False, "process_correct": False, "first_error_step": None,
                "first_error_type": "api_error", "lucky_guess": False, "steps": [], "final_answer": "",
                "injected": None, "error": error}
    v = verify(p, sol.steps, sol.final_answer)
    return {
        **base,
        "final_correct": v.final_correct,
        "process_correct": v.process_correct,
        "first_error_step": v.first_error_step,
        "first_error_type": v.first_error_type,
        "lucky_guess": v.lucky_guess,
        "steps": [s.__dict__ for s in v.steps],
        "n_steps": len(sol.steps),
        "final_answer": sol.final_answer,
        "injected": sol.injected,
        "error": "",
    }


def run(model_names: list[str], problems: list[Problem], out_dir: str | Path, workers: int = 1) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "results.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for name in model_names:
            model = get_model(name)
            n_workers = workers if not name.startswith("sim-") else 1
            rows = evaluate_model(model, problems, n_workers)
            for r in rows:
                fh.write(json.dumps(r) + "\n")
            acc = sum(r["final_correct"] for r in rows) / len(rows)
            proc = sum(r["process_correct"] for r in rows) / len(rows)
            print(f"{name:<20} answer acc={acc:.3f}  process acc={proc:.3f}  ({len(rows)} problems)")
    return path


def load_results(path: str | Path) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
