"""Summaries, model comparisons and evidence-grounded error reports."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from .stats import bootstrap_ci, paired_bootstrap
from .verifier import ERROR_TYPES


def summarize(rows: list[dict]) -> dict:
    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)

    models = {}
    for name, rs in by_model.items():
        ans = [r["final_correct"] for r in rs]
        proc = [r["process_correct"] for r in rs]
        a, alo, ahi = bootstrap_ci(ans)
        p, plo, phi = bootstrap_ci(proc)
        domains = {}
        for d in sorted({r["domain"] for r in rs}):
            sub = [r["final_correct"] for r in rs if r["domain"] == d]
            m, lo, hi = bootstrap_ci(sub)
            domains[d] = {"n": len(sub), "answer_acc": m, "ci": [lo, hi]}
        errors = Counter(r["first_error_type"] for r in rs if r["first_error_type"])
        models[name] = {
            "n": len(rs),
            "answer_acc": a, "answer_ci": [alo, ahi],
            "process_acc": p, "process_ci": [plo, phi],
            "lucky_guess_rate": sum(r["lucky_guess"] for r in rs) / len(rs),
            "by_domain": domains,
            "error_types": {e: errors.get(e, 0) for e in ERROR_TYPES + (["api_error"] if errors.get("api_error") else [])},
        }

    comparisons = []
    for m1, m2 in combinations(sorted(by_model), 2):
        a = {r["problem_id"]: r["final_correct"] for r in by_model[m1]}
        b = {r["problem_id"]: r["final_correct"] for r in by_model[m2]}
        shared = sorted(set(a) & set(b))
        res = paired_bootstrap([a[i] for i in shared], [b[i] for i in shared])
        comparisons.append({"a": m1, "b": m2, "metric": "answer_acc", "n": len(shared), **res})
    return {"models": models, "comparisons": comparisons}


def format_summary(summary: dict) -> str:
    lines = ["Model                 answer acc [95% CI]        process acc [95% CI]       lucky-guess",
             "-" * 92]
    for name, m in summary["models"].items():
        lines.append(f"{name:<20}  {m['answer_acc']:.3f} [{m['answer_ci'][0]:.3f}, {m['answer_ci'][1]:.3f}]"
                     f"     {m['process_acc']:.3f} [{m['process_ci'][0]:.3f}, {m['process_ci'][1]:.3f}]"
                     f"     {m['lucky_guess_rate']:.3f}")
    lines += ["", "First-error type counts:"]
    for name, m in summary["models"].items():
        lines.append(f"  {name:<20} " + "  ".join(f"{k}={v}" for k, v in m["error_types"].items()))
    lines += ["", "Paired bootstrap on answer accuracy (A - B):"]
    for c in summary["comparisons"]:
        flag = "significant" if c["significant"] else "not significant"
        lines.append(f"  {c['a']} vs {c['b']}: {c['diff']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]  "
                     f"p={c['p_value']:.4f}  ({flag})")
    return "\n".join(lines)


def error_report(row: dict) -> str:
    """Markdown report that pinpoints the exact step where the reasoning broke."""
    out = [f"### {row['problem_id']} ({row['topic']}) - {row['model']}", "", f"**Problem:** {row['statement']}", ""]
    out.append(f"**Expected:** `{row['expected_answer']}`  |  **Model answer:** `{row['final_answer']}`  |  "
               f"**Answer correct:** {'yes' if row['final_correct'] else 'no'}")
    out += ["", "| Step | Content | Verdict |", "|---|---|---|"]
    n = row.get("n_steps", 0)
    for s in row["steps"]:
        label = "final answer" if s["index"] >= n else str(s["index"] + 1)
        verdict = {"ok": "ok", "propagated": "carries earlier error", "parse_error": "unreadable"}.get(s["status"], "")
        if s["status"] == "error":
            verdict = f"**{s['error_type']}** - {s['detail']}"
        out.append(f"| {label} | `{s['text']}` | {verdict} |")
    if row["first_error_step"] is not None:
        where = "the final answer" if row["first_error_step"] >= n else f"step {row['first_error_step'] + 1}"
        out += ["", f"> Reasoning first breaks at {where}: **{row['first_error_type']}**."]
    if row["lucky_guess"]:
        out.append("> Final answer is correct, but the written reasoning does not support it (lucky guess).")
    return "\n".join(out)


def write_reports(rows: list[dict], out_dir: str | Path, per_model: int = 25) -> None:
    out = Path(out_dir)
    summary = summarize(rows)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "summary.txt").write_text(format_summary(summary), encoding="utf-8")
    rep_dir = out / "error_reports"
    rep_dir.mkdir(parents=True, exist_ok=True)
    for model in summary["models"]:
        failures = [r for r in rows if r["model"] == model and not r["process_correct"]]
        body = [f"# Error report: {model}", "", f"{len(failures)} attempts with at least one invalid step "
                f"(showing up to {per_model}).", ""]
        body += [error_report(r) + "\n" for r in failures[:per_model]]
        (rep_dir / f"{model}.md").write_text("\n".join(body), encoding="utf-8")
