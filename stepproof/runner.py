"""Run models over the benchmark and verify every solution step."""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .models import get_model
from .problems import Problem
from .verifier import verify


def evaluate_model(model, problems: list[Problem], workers: int = 1) -> list[dict]:
    def attempt(p: Problem):
        try:
            return model.solve(p)
        except Exception as exc:  # API failure etc. -> record, don't crash the run
            return exc

    # Only the model calls run in parallel; SymPy verification stays on one thread.
    if workers > 1:
        with ThreadPoolExecutor(workers) as pool:
            attempts = list(pool.map(attempt, problems))
    else:
        attempts = [attempt(p) for p in problems]
    return [
        _row(model.name, p, None, error=f"{type(a).__name__}: {a}") if isinstance(a, Exception)
        else _row(model.name, p, a)
        for p, a in zip(problems, attempts)
    ]


def _row(model_name: str, p: Problem, sol, error: str = "") -> dict:
    base = {"model": model_name, "problem_id": p.id, "domain": p.domain, "topic": p.topic,
            "statement": p.statement, "expected_answer": p.answer}
    if sol is None:
        return {**base, "final_correct": False, "process_correct": False, "first_error_step": None,
                "first_error_type": "api_error", "lucky_guess": False, "steps": [], "n_steps": 0,
                "final_answer": "", "injected": None, "error": error}
    # model_steps keeps the model's own words, so saved runs can be re-verified offline (see reverify)
    base = {**base, "model_steps": list(sol.steps), "n_steps": len(sol.steps), "final_answer": sol.final_answer,
            "injected": sol.injected, "raw": sol.raw if not sol.steps else ""}
    return {**base, **_verdict(p, sol.steps, sol.final_answer)}


def _verdict(p: Problem, steps: list[str], final_answer: str) -> dict:
    try:
        v = verify(p, steps, final_answer)
    except Exception as exc:  # unexpected model notation that breaks SymPy -> record it, keep going
        return {"final_correct": False, "process_correct": False, "first_error_step": None,
                "first_error_type": "parse_error", "lucky_guess": False, "steps": [],
                "error": f"verifier: {type(exc).__name__}: {exc}"}
    return {
        "final_correct": v.final_correct,
        "process_correct": v.process_correct,
        "first_error_step": v.first_error_step,
        "first_error_type": v.first_error_type,
        "lucky_guess": v.lucky_guess,
        "steps": [s.__dict__ for s in v.steps],
        "error": "",
    }


def reverify(results_path: str | Path, problems: list[Problem]) -> list[dict]:
    """Re-run verification on saved model answers (no API calls) and rewrite the results file."""
    by_id = {p.id: p for p in problems}
    rows = load_results(results_path)
    changed = 0
    for r in rows:
        if r.get("first_error_type") == "api_error" or "model_steps" not in r:
            continue
        new = _verdict(by_id[r["problem_id"]], r["model_steps"], r["final_answer"])
        changed += (new["process_correct"], new["first_error_type"]) != (r["process_correct"], r["first_error_type"])
        r.update(new)
    Path(results_path).write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    print(f"re-verified {len(rows)} attempts; verdict changed on {changed}")
    return rows


def run(model_names: list[str], problems: list[Problem], out_dir: str | Path, workers: int = 1) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "results.jsonl"
    usage_log = {}
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
            usage = getattr(model, "usage", None)
            if usage:
                usage_log[name] = usage
                print(f"{'':<20} API usage: {usage['requests']} requests, "
                      f"{usage['input_tokens']:,} input tokens, {usage['output_tokens']:,} output tokens")
            fh.flush()
    if usage_log:
        (out / "usage.json").write_text(json.dumps(usage_log, indent=2), encoding="utf-8")
    return path


def load_results(path: str | Path) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
