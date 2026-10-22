#!/usr/bin/env python3
"""Evaluate MediLens release metrics against the release checklist (RG-01..RG-21).

Usage:
    python release_gate.py metrics.json [--json] [--today YYYY-MM-DD]

Release checks are named RG-xx so they are not confused with the project's
phase gates (G0..G6, G0-R, G1-D, G2-CS, G3-P, G5-H). The phase gates G3, G5 and
G6 are decided with this script; G2-CS, G3-P, G1-D and G0-R feed RG-15..RG-19.

See assets/release-metrics-example.json for the input shape. Missing evidence
counts as FAIL. Non-overridable failures always give NO-GO; overridable failures
give NO-GO unless a matching, unexpired entry exists in
"risk_acceptances": [{"gate": "RG-09", "owner": "...", "expires": "YYYY-MM-DD"}].
Exit code 0 for GO, 1 for NO-GO.
"""

import json
import sys
from datetime import date


def checks(m):
    ai = m.get("ai", {})
    base, cand = ai.get("baseline_f1", {}), ai.get("candidate_f1", {})
    f1_ok = bool(base) and all(
        cand.get(u, 0) >= 0.80 - 1e-9 and (base.get(u, 0) - cand.get(u, 0)) <= 0.01 + 1e-9
        for u in base
    )
    cov = m.get("coverage", {})
    cs = m.get("clinical_safety", {})
    reg = m.get("regulatory", {})
    pen = m.get("pentest", {})
    cost = m.get("ai_cost", {})
    real_data = bool(m.get("real_data", False))
    pentest_ok = (not real_data) or (
        pen.get("done") is True and pen.get("open_high_critical", 1) == 0
    )
    return [
        ("RG-01", "No open S1", m.get("open_defects", {}).get("S1", 1) == 0, False),
        ("RG-02", "No open S2", m.get("open_defects", {}).get("S2", 1) == 0, False),
        ("RG-03", "MUST suites 100% pass", m.get("must_suite_pass_rate", 0) >= 1.0, False),
        (
            "RG-04",
            "Coverage BE>=80% FE>=70%",
            cov.get("backend", 0) >= 0.80 and cov.get("frontend", 0) >= 0.70,
            True,
        ),
        ("RG-05", "Authz matrix 100%", m.get("authz_matrix_coverage", 0) >= 1.0, False),
        ("RG-06", "AI F1 per unit (>=0.80, drop<=1pt)", f1_ok, False),
        (
            "RG-07",
            "Guardrails block>=95% false<=10%",
            ai.get("guardrail_block_rate", 0) >= 0.95
            and ai.get("guardrail_false_block_rate", 1) <= 0.10,
            False,
        ),
        ("RG-08", "Hallucination <=5%", ai.get("hallucination_rate", 1) <= 0.05, False),
        ("RG-09", "API p95 <=300ms", m.get("perf", {}).get("api_p95_ms", 1e9) <= 300, True),
        ("RG-10", "A11y serious/critical = 0", m.get("a11y_serious_critical", 1) == 0, True),
        ("RG-11", "Security sign-off GO", m.get("security_signoff") == "GO", False),
        (
            "RG-12",
            "Medical content reviewed 100%",
            m.get("medical_content_reviewed_ratio", 0) >= 1.0,
            False,
        ),
        ("RG-13", "DR drill <=120 days", m.get("dr_drill_days_ago", 9999) <= 120, True),
        (
            "RG-14",
            "Release notes + rollback plan",
            bool(m.get("release_notes_ready")) and bool(m.get("rollback_plan_ready")),
            False,
        ),
        (
            "RG-15",
            "Clinical Safety Case signed, 0 unacceptable residual risks (G2-CS)",
            cs.get("safety_case_signed") is True and cs.get("unacceptable_residual_risks", 1) == 0,
            False,
        ),
        ("RG-16", "Claims lint: 0 BLOCK findings", m.get("claims_lint_block", 1) == 0, False),
        (
            "RG-17",
            "Regulatory Decision Record current for this scope (G0-R)",
            reg.get("rdr_current") is True,
            False,
        ),
        ("RG-18", "External pentest clean when real data is in scope (G3-P)", pentest_ok, False),
        (
            "RG-19",
            "Data licence gate PASS for datasets/models in release (G1-D)",
            m.get("data_licence_gate") == "PASS",
            False,
        ),
        (
            "RG-20",
            "AI cost within budget and escalation <=15%",
            cost.get("usd_per_doc", 1e9) <= cost.get("budget_usd_per_doc", 0.10)
            and cost.get("escalation_rate", 1) <= 0.15,
            True,
        ),
        ("RG-21", "i18n check: 0 errors (VI/EN)", m.get("i18n_errors", 1) == 0, False),
    ]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    m = json.load(open(sys.argv[1], encoding="utf-8"))
    today = date.today().isoformat()
    if "--today" in sys.argv:
        today = sys.argv[sys.argv.index("--today") + 1]
    accepted = {a["gate"] for a in m.get("risk_acceptances", []) if a.get("expires", "") >= today}
    results, go = [], True
    for gid, name, ok, overridable in checks(m):
        status = "PASS" if ok else ("ACCEPTED" if overridable and gid in accepted else "FAIL")
        if status == "FAIL":
            go = False
        results.append({"check": gid, "name": name, "status": status, "overridable": overridable})
    decision = "GO" if go else "NO-GO"
    if "--json" in sys.argv:
        print(
            json.dumps(
                {"release": m.get("release"), "decision": decision, "checks": results}, indent=2
            )
        )
    else:
        print(f"Release {m.get('release')}")
        for r in results:
            flag = (
                ""
                if r["status"] != "FAIL"
                else (
                    "  (overridable with risk acceptance)" if r["overridable"] else "  (blocking)"
                )
            )
            print(f"  {r['check']:<6} {r['status']:<9} {r['name']}{flag}")
        print(f"DECISION: {decision}")
    return 0 if go else 1


if __name__ == "__main__":
    sys.exit(main())
