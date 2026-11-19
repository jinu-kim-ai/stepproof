"""StepProof dashboard:  streamlit run app.py"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from stepproof.report import summarize
from stepproof.runner import load_results
from stepproof.verifier import ERROR_TYPES

st.set_page_config(page_title="StepProof", layout="wide")
st.title("StepProof: LLM Math Reasoning Evaluator")

default_results = Path(__file__).parent / "results" / "results.jsonl"
results_path = Path(st.sidebar.text_input("Results file", str(default_results)))
if not results_path.exists():
    st.info("No results yet. Run `python -m stepproof run` first.")
    st.stop()


@st.cache_data
def load(path: str, mtime: float):
    return load_results(path)


rows = load(str(results_path), results_path.stat().st_mtime)
df = pd.DataFrame(rows)
models = sorted(df["model"].unique())
domains = sorted(df["domain"].unique())
sel_models = st.sidebar.multiselect("Models", models, default=models)
sel_domains = st.sidebar.multiselect("Domains", domains, default=domains)
df = df[df["model"].isin(sel_models) & df["domain"].isin(sel_domains)]
rows = [r for r in rows if r["model"] in sel_models and r["domain"] in sel_domains]
if df.empty:
    st.warning("Nothing selected.")
    st.stop()
summary = summarize(rows)

# ---------------------------------------------------------------- headline table
st.subheader("Accuracy with 95% bootstrap confidence intervals")
st.caption("**Answer accuracy**: final answer is correct. **Process accuracy**: every step verifies. "
           "**Lucky guess**: right answer, invalid reasoning.")
head = pd.DataFrame([
    {"model": m, "problems": s["n"],
     "answer acc": f"{s['answer_acc']:.1%}  [{s['answer_ci'][0]:.1%}, {s['answer_ci'][1]:.1%}]",
     "process acc": f"{s['process_acc']:.1%}  [{s['process_ci'][0]:.1%}, {s['process_ci'][1]:.1%}]",
     "gap": f"{s['answer_acc'] - s['process_acc']:+.1%}",
     "lucky guess": f"{s['lucky_guess_rate']:.1%}"}
    for m, s in summary["models"].items()
])
st.dataframe(head, hide_index=True, width="stretch")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Answer accuracy by domain")
    dom = df.groupby(["domain", "model"])["final_correct"].mean().unstack("model")
    st.bar_chart(dom, stack=False, y_label="answer accuracy")
with c2:
    st.subheader("Where reasoning breaks (first error type)")
    err = (df[df["first_error_type"].notna()].groupby(["model", "first_error_type"]).size()
           .unstack("first_error_type").reindex(columns=[e for e in ERROR_TYPES + ["api_error"]
                                                         if e in set(df["first_error_type"].dropna())]).fillna(0))
    st.bar_chart(err, y_label="attempts")

st.subheader("Error rate by topic")
topic = (1 - df.groupby(["topic", "model"])["process_correct"].mean()).unstack("model")
st.dataframe(topic.style.format("{:.1%}").background_gradient(cmap="Reds", axis=None), width="stretch")

# ---------------------------------------------------------------- comparisons
if summary["comparisons"]:
    st.subheader("Pairwise comparison (paired bootstrap, answer accuracy)")
    comp = pd.DataFrame([{
        "A": c["a"], "B": c["b"], "A - B": f"{c['diff']:+.1%}",
        "95% CI": f"[{c['ci_low']:+.1%}, {c['ci_high']:+.1%}]", "p": f"{c['p_value']:.4f}",
        "verdict": "significant" if c["significant"] else "not significant"} for c in summary["comparisons"]])
    st.dataframe(comp, hide_index=True, width="stretch")

# ---------------------------------------------------------------- drill-down
st.subheader("Inspect a failed attempt")
fails = df[~df["process_correct"]]
f1, f2 = st.columns(2)
model_pick = f1.selectbox("Model", sorted(fails["model"].unique()) if not fails.empty else models)
types = ["(any)"] + sorted(fails["first_error_type"].dropna().unique())
type_pick = f2.selectbox("Error type", types)
sub = fails[fails["model"] == model_pick]
if type_pick != "(any)":
    sub = sub[sub["first_error_type"] == type_pick]
if sub.empty:
    st.write("No failures match.")
else:
    pid = st.selectbox("Problem", sub["problem_id"].tolist())
    r = sub[sub["problem_id"] == pid].iloc[0]
    st.markdown(f"**{r['topic']}**: {r['statement']}")
    st.markdown(f"Expected `{r['expected_answer']}` \u00b7 model answered `{r['final_answer']}` \u00b7 "
                f"{'correct' if r['final_correct'] else 'incorrect'} final answer")
    icons = {"ok": "\u2705", "propagated": "\u21aa\ufe0f", "error": "\u274c", "parse_error": "\u26a0\ufe0f"}
    for s in r["steps"]:
        label = "Final answer" if s["index"] >= r.get("n_steps", 0) else f"Step {s['index'] + 1}"
        line = f"{icons.get(s['status'], '')} **{label}:** `{s['text']}`"
        if s["status"] == "error":
            line += f"  \n  → **{s['error_type']}**: {s['detail']}"
        elif s["status"] == "propagated":
            line += "  _(follows correctly from an earlier error)_"
        st.markdown(line)
