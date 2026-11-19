"""Command line interface.

  python -m stepproof generate                       # write data/problems.jsonl (520 problems)
  python -m stepproof run --models sim-careful sim-hasty sim-rule-confused
  python -m stepproof run --models claude-opus-5-5 claude-haiku-5-5 --limit 100 --workers 8
  python -m stepproof report                         # summary + per-model error reports
  python -m stepproof check-verifier                 # does the verifier find injected errors?
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .models import PROFILES, SimulatedModel
from .problems import generate, load, save
from .report import format_summary, summarize, write_reports
from .runner import load_results, run
from .verifier import verify


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="stepproof")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("--per-template", type=int, default=40)
    g.add_argument("--seed", type=int, default=7)
    g.add_argument("--out", default="data/problems.jsonl")

    r = sub.add_parser("run")
    r.add_argument("--models", nargs="+", default=list(PROFILES))
    r.add_argument("--problems", default="data/problems.jsonl")
    r.add_argument("--out", default="results")
    r.add_argument("--limit", type=int, help="only the first N problems of each template (cost control for API models)")
    r.add_argument("--workers", type=int, default=4, help="parallel API requests per model")

    rep = sub.add_parser("report")
    rep.add_argument("--results", default="results")

    c = sub.add_parser("check-verifier")
    c.add_argument("--problems", default="data/problems.jsonl")

    args = ap.parse_args(argv)

    if args.cmd == "generate":
        problems = generate(args.per_template, args.seed)
        save(problems, args.out)
        counts = Counter(p.domain for p in problems)
        print(f"wrote {len(problems)} problems to {args.out}: {dict(counts)}")
        return 0

    if args.cmd == "run":
        problems = _load_or_generate(args.problems)
        if args.limit:
            seen: Counter = Counter()
            problems = [p for p in problems if (seen.update([p.topic]) or seen[p.topic] <= args.limit)]
        path = run(args.models, problems, args.out, args.workers)
        rows = load_results(path)
        write_reports(rows, args.out)
        print()
        print(format_summary(summarize(rows)))
        print(f"\nresults: {path}\nerror reports: {Path(args.out) / 'error_reports'}")
        return 0

    if args.cmd == "report":
        rows = load_results(Path(args.results) / "results.jsonl")
        write_reports(rows, args.results)
        print(format_summary(summarize(rows)))
        return 0

    if args.cmd == "check-verifier":
        return check_verifier(_load_or_generate(args.problems))
    return 1


def check_verifier(problems) -> int:
    """Inject every applicable error type into every problem and measure how often the
    verifier (a) detects it, (b) puts it at the right step, (c) names the right type."""
    print(f"{'error type':<18}{'injected':>9}{'detected':>10}{'right step':>12}{'right type':>12}")
    for etype in ("arithmetic_slip", "invalid_algebra", "misapplied_rule", "unjustified_leap"):
        model = SimulatedModel("probe", {etype: 1.0})
        n = det = step = typ = 0
        for p in problems:
            sol = model.solve(p)
            if not sol.injected:
                continue
            n += 1
            v = verify(p, sol.steps, sol.final_answer)
            det += not v.process_correct
            step += v.first_error_step == sol.injected["step"]
            typ += v.first_error_type == etype
        if n:
            print(f"{etype:<18}{n:>9}{det / n:>10.1%}{step / n:>12.1%}{typ / n:>12.1%}")
    clean = sum(verify(p, p.reference_steps, p.answer).process_correct for p in problems)
    print(f"\nfalse alarms on {len(problems)} correct reference solutions: {len(problems) - clean}")
    return 0


def _load_or_generate(path: str):
    if Path(path).exists():
        return load(path)
    print(f"{path} not found - generating the default benchmark")
    problems = generate()
    save(problems, path)
    return problems


if __name__ == "__main__":
    raise SystemExit(main())
