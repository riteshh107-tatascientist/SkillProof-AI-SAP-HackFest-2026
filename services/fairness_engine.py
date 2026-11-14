"""Selection-rate audit. A disparity is a SIGNAL FOR INVESTIGATION, not proof of discrimination."""
import numpy as np, pandas as pd
from scipy import stats

MIN_N = 30


def selection_rates(df: pd.DataFrame, group: str, outcome: str, min_n: int = MIN_N):
    d = df[[group, outcome]].dropna()
    g = d.groupby(group)[outcome].agg(applicants="count", selected="sum").reset_index()
    g["selection_rate"] = g.selected / g.applicants
    ref = g.selection_rate.max()
    g["impact_ratio"] = g.selection_rate / ref if ref > 0 else np.nan
    g["flag_80pct_rule"] = np.where(g.impact_ratio < 0.8, "Investigate", "Within 4/5 guide")
    g["sample_warning"] = np.where((g.applicants < min_n) | (g.selected < 5), f"Small sample (n<{min_n} or <5 selected): unreliable", "")
    top = g.loc[g.selection_rate.idxmax(), group] if len(g) else None
    g["parity_diff_vs_top"] = g.selection_rate - ref
    return g.rename(columns={group: "group"}), top


def significance(df: pd.DataFrame, group: str, outcome: str):
    ct = pd.crosstab(df[group], df[outcome])
    if ct.shape[0] < 2 or ct.shape[1] < 2: return {"test": "n/a", "p_value": None, "note": "Need at least two groups and both outcomes."}
    if ct.shape == (2, 2): return {"test": "Fisher exact", "p_value": float(stats.fisher_exact(ct)[1]), "note": ""}
    chi2, p, _, exp = stats.chi2_contingency(ct)
    return {"test": "Chi-square", "p_value": float(p), "note": "Expected counts below 5 - interpret cautiously." if (exp < 5).any() else ""}


def stratified(df: pd.DataFrame, group: str, outcome: str, score_col: str, bands=3):
    """Does the disparity persist among similarly skilled people? (conditions on skill)."""
    d = df.dropna(subset=[group, outcome, score_col]).copy()
    d["skill_band"] = pd.qcut(d[score_col], bands, labels=["Lower skill", "Mid skill", "Higher skill"][:bands] if bands == 3 else None, duplicates="drop")
    rows = []
    for band, sub in d.groupby("skill_band", observed=True):
        t, _ = selection_rates(sub, group, outcome)
        t.insert(0, "skill_band", str(band)); rows.append(t)
    return pd.concat(rows) if rows else pd.DataFrame()


def interpret(table: pd.DataFrame, sig: dict) -> str:
    flagged = table[(table.flag_80pct_rule == "Investigate") & (table.sample_warning == "")]
    small = table[table.sample_warning != ""]
    msg = []
    if len(flagged): msg.append(f"Groups below the four-fifths guide with adequate sample: {', '.join(map(str, flagged.group))}. Treat this as a signal to review the screening step, not as proof of discrimination.")
    else: msg.append("No adequately-sized group falls below the four-fifths guide.")
    if len(small): msg.append(f"Small-sample groups ({', '.join(map(str, small.group))}) cannot be judged reliably.")
    if sig.get("p_value") is not None: msg.append(f"{sig['test']} p-value = {sig['p_value']:.4f}. Statistical significance does not establish cause; check job-relatedness and data quality.")
    return " ".join(msg)
