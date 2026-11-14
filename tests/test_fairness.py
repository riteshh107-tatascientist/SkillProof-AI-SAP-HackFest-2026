import pandas as pd
from services import fairness_engine as fe
from utils.helpers import load_csv


def test_impact_ratio_and_small_sample():
    df = pd.DataFrame({"g": ["A"] * 100 + ["B"] * 100 + ["C"] * 5, "y": [1] * 50 + [0] * 50 + [1] * 20 + [0] * 80 + [1] * 1 + [0] * 4})
    t, top = fe.selection_rates(df, "g", "y"); a = t.set_index("group")
    assert top == "A" and abs(a.loc["B", "impact_ratio"] - 0.4) < 1e-9 and a.loc["B", "flag_80pct_rule"] == "Investigate"
    assert "Small sample" in a.loc["C", "sample_warning"] and a.loc["A", "sample_warning"] == ""
    assert fe.significance(df[df.g != "C"], "g", "y")["test"] == "Fisher exact"


def test_demo_dataset_shows_legacy_gap_but_not_skills_gap():
    d = load_csv("fairness_demo.csv")
    leg, _ = fe.selection_rates(d, "institution_tier", "legacy_screen_shortlisted"); sk, _ = fe.selection_rates(d, "institution_tier", "skills_screen_shortlisted")
    assert leg.impact_ratio.min() < sk.impact_ratio.min()
    assert not fe.stratified(d, "institution_tier", "legacy_screen_shortlisted", "skill_score").empty
