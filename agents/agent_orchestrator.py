"""Agent 7 - Orchestrator.
Reads alerts_*.json from all source agents, evaluates ABP assumption status,
computes system_status.json, and generates a board brief (Claude API or deterministic).
"""
import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "outputs")

SOURCE_AGENTS = [
    "entry", "competitive", "revenue", "owner",
    "talent", "regulatory", "operations"
]

ABP_ASSUMPTIONS = {
    "A1": "Target owner signs at Radisson standard fee structure (3–4% mgmt fee)",
    "A2": "RevPAR breakeven achievable within 36 months of opening",
    "A3": "No other Radisson brand already present in same submarket (no cannibalisation)",
    "A4": "Energy & labour cost increases stay within 10% YoY",
    "A5": "Loyalty programme retains share against rival devaluations",
}

HEDGING_ACTIONS = {
    "H1": {
        "short": "H1 — Pause LOI; add FX floor clause",
        "full": ("FX depreciation exceeds 15% against EUR. "
                 "Owner: Development Director. "
                 "Action: Pause all LOI negotiations in affected market; "
                 "add FX floor clause to any term sheet currently in negotiation. "
                 "Deadline: before next LOI signature."),
        "triggered_by": "A1, A2",
    },
    "H2": {
        "short": "H2 — Deprioritise market; redirect dev effort",
        "full": ("Supply pipeline exceeds 15% of existing stock — oversupply risk. "
                 "Owner: Development Director. "
                 "Action: Deprioritise market in pipeline review; "
                 "redirect BD effort to next-priority country on target list. "
                 "Deadline: next pipeline review meeting."),
        "triggered_by": "A2",
    },
    "H3": {
        "short": "H3 — Full 90-day hold + escalate to development committee",
        "full": ("Two or more simultaneous RED alerts in the same market. "
                 "Owner: Chief Development Officer. "
                 "Action: Immediate 90-day moratorium on all new signings in this market; "
                 "brief Development Committee at next meeting; "
                 "do not advance any LOI or HMA currently in negotiation. "
                 "Deadline: notify committee within 5 business days."),
        "triggered_by": "A1, A2, A3",
    },
}


def load_alerts():
    all_alerts = {}
    for name in SOURCE_AGENTS:
        path = os.path.join(OUTPUT_DIR, f"alerts_{name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                all_alerts[name] = json.load(f)
        else:
            all_alerts[name] = {"agent": name, "overall_status": "NO_DATA", "indicators": []}
    return all_alerts


def evaluate_abp(all_alerts):
    """
    For each ABP assumption, determine status (HOLDING / AT_RISK / BREACHED)
    by matching active RED/YELLOW indicators to the assumption they affect.
    Returns a dict of assumption_id -> {status, evidence, recommendation}.
    """
    # Collect all indicators with their alert levels
    all_inds = []
    for name, data in all_alerts.items():
        for ind in data.get("indicators", []):
            all_inds.append({"agent": name, **ind})

    def reds_matching(keywords):
        return [i for i in all_inds
                if i.get("alert_level") == "RED"
                and any(k.lower() in str(i.get("name", "")).lower() or
                        k.lower() in str(i.get("recommendation", "")).lower()
                        for k in keywords)]

    def yellows_matching(keywords):
        return [i for i in all_inds
                if i.get("alert_level") == "YELLOW"
                and any(k.lower() in str(i.get("name", "")).lower() or
                        k.lower() in str(i.get("recommendation", "")).lower()
                        for k in keywords)]

    results = {}

    # A1: owner signs at standard fee structure
    # AT RISK if: rival approaches owner (owner agent), or FX makes deal economics hard
    a1_reds = reds_matching(["owner churn", "competing operator", "FX depreciation", "fx floor"])
    a1_yellows = yellows_matching(["owner churn", "FX", "contract"])
    if a1_reds:
        markets = list({i.get("market") or i.get("property", "") for i in a1_reds})
        results["A1"] = {
            "status": "AT_RISK",
            "evidence": f"{len(a1_reds)} RED signal(s): {', '.join(markets)}",
            "recommendation": "Asset management to schedule owner calls; review fee flexibility for at-risk properties.",
        }
    elif a1_yellows:
        results["A1"] = {
            "status": "WATCH",
            "evidence": f"{len(a1_yellows)} YELLOW signal(s) — no immediate breach",
            "recommendation": "Monitor contract calendar and FX trajectory.",
        }
    else:
        results["A1"] = {"status": "HOLDING", "evidence": "No signals threatening fee structure.", "recommendation": ""}

    # A2: RevPAR breakeven in 36 months
    # AT RISK if: pipeline oversupply, demand pace weak, RevPAR below budget
    a2_reds = reds_matching(["pipeline", "forward booking", "RevPAR", "revpar", "demand pace", "booking pace"])
    a2_yellows = yellows_matching(["pipeline", "forward booking", "RevPAR", "demand"])
    if a2_reds:
        markets = list({i.get("market") or i.get("property", "") for i in a2_reds})
        results["A2"] = {
            "status": "AT_RISK",
            "evidence": f"{len(a2_reds)} RED signal(s) threatening revenue model: {', '.join(markets[:4])}",
            "recommendation": "Re-run P&L models for affected markets; extend breakeven sensitivity range to 48 months.",
        }
    elif a2_yellows:
        results["A2"] = {
            "status": "WATCH",
            "evidence": f"{len(a2_yellows)} YELLOW signal(s) — monitor closely",
            "recommendation": "Stress-test breakeven models at 85% of assumed RevPAR.",
        }
    else:
        results["A2"] = {"status": "HOLDING", "evidence": "Revenue signals on track.", "recommendation": ""}

    # A3: no cannibalisation — no automated signal yet; flag if rival signs in Radisson submarket
    a3_reds = reds_matching(["rival signing", "target market"])
    if a3_reds:
        rivals = list({i.get("rival", i.get("value", "")) for i in a3_reds})
        results["A3"] = {
            "status": "AT_RISK",
            "evidence": f"Rival(s) signed in Radisson target submarket(s): {', '.join(rivals[:3])}",
            "recommendation": "Development Director to confirm Radisson has no overlapping pipeline in same submarket.",
        }
    else:
        results["A3"] = {"status": "HOLDING", "evidence": "No cannibalisation signals detected.", "recommendation": ""}

    # A4: energy & labour <10% YoY
    a4_reds = reds_matching(["energy", "labour", "wage", "minimum wage", "natural gas"])
    a4_yellows = yellows_matching(["energy", "labour", "wage", "natural gas"])
    if a4_reds:
        markets = list({i.get("market") or i.get("country", "") for i in a4_reds})
        results["A4"] = {
            "status": "BREACHED",
            "evidence": f"Energy/labour costs exceeding 10% threshold in: {', '.join(markets)}",
            "recommendation": "CFO to re-baseline cost model; review CAPEX timing and procurement contracts.",
        }
    elif a4_yellows:
        results["A4"] = {
            "status": "WATCH",
            "evidence": f"{len(a4_yellows)} YELLOW cost signal(s)",
            "recommendation": "Run sensitivity at +12% cost scenario.",
        }
    else:
        results["A4"] = {"status": "HOLDING", "evidence": "Cost increases within tolerance.", "recommendation": ""}

    # A5: loyalty retains share vs rival devaluations
    a5_reds = reds_matching(["loyalty", "devaluation", "points"])
    a5_yellows = yellows_matching(["loyalty", "devaluation"])
    if a5_reds:
        rivals = list({i.get("rival", "") for i in a5_reds if i.get("rival")})
        results["A5"] = {
            "status": "AT_RISK",
            "evidence": f"Rival loyalty devaluation detected — potential switching opportunity: {', '.join(rivals)}",
            "recommendation": "Brief loyalty team; consider targeted status-match campaign within 30 days.",
        }
    elif a5_yellows:
        results["A5"] = {
            "status": "WATCH",
            "evidence": "Rival loyalty changes detected — not yet a devaluation",
            "recommendation": "Monitor; prepare response campaign brief.",
        }
    else:
        results["A5"] = {"status": "HOLDING", "evidence": "No adverse loyalty moves detected.", "recommendation": ""}

    return results


def derive_system_status(all_alerts, abp_status):
    counts = {"RED": 0, "YELLOW": 0, "GREEN": 0, "NO_DATA": 0, "ERROR": 0}
    by_agent = {}
    red_indicators = []
    for name, data in all_alerts.items():
        status = data.get("overall_status", "NO_DATA")
        by_agent[name] = status
        for ind in data.get("indicators", []):
            lvl = ind.get("alert_level", "NO_DATA")
            counts[lvl] = counts.get(lvl, 0) + 1
            if lvl == "RED":
                red_indicators.append({"agent": name, **ind})

    if counts["RED"] >= 2:
        overall = "RED"
    elif counts["RED"] == 1:
        overall = "YELLOW"
    elif counts["YELLOW"] > 0:
        overall = "YELLOW"
    elif counts["GREEN"] > 0:
        overall = "GREEN"
    else:
        overall = "NO_DATA"

    # Count how many ABP assumptions are at risk or breached
    abp_at_risk = [k for k, v in abp_status.items()
                   if v["status"] in ("AT_RISK", "BREACHED")]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overall_status": overall,
        "indicator_counts": counts,
        "agent_status": by_agent,
        "red_indicator_count": len(red_indicators),
        "red_indicators": red_indicators,
        "abp_status": abp_status,
        "abp_at_risk": abp_at_risk,
        "hedging_actions": HEDGING_ACTIONS,
    }


def _hedge_bullets(red_indicators):
    """Derive triggered hedging actions from RED indicator recommendations."""
    triggered = {}
    for r in red_indicators:
        rec = r.get("recommendation", "")
        if "H1" in rec and "H1" not in triggered:
            triggered["H1"] = HEDGING_ACTIONS["H1"]
        if "H2" in rec and "H2" not in triggered:
            triggered["H2"] = HEDGING_ACTIONS["H2"]
        if "H3" in rec and "H3" not in triggered:
            triggered["H3"] = HEDGING_ACTIONS["H3"]
    return triggered


def fallback_brief(system_status, all_alerts):
    """Deterministic brief — used when ANTHROPIC_API_KEY is not set."""
    abp = system_status.get("abp_status", {})
    reds = system_status.get("red_indicators", [])
    hedging = _hedge_bullets(reds)

    lines = [
        "# Radisson CI — Board Brief",
        f"\n_Generated: {system_status['generated_at']}_\n",
        f"**System status: {system_status['overall_status']}** · "
        f"{system_status['red_indicator_count']} RED indicators across "
        f"{len(system_status['agent_status'])} agents · "
        f"{len(system_status.get('abp_at_risk', []))} ABP assumption(s) at risk\n",

        "## 1. Top risks this period\n",
    ]

    if reds:
        for r in reds[:3]:
            where = r.get("market") or r.get("property") or r.get("country") or ""
            lines.append(
                f"- **[{r['agent'].upper()}] {r.get('name', '')}** "
                f"({where}): `{r.get('value', '')}`. "
                f"{r.get('recommendation', '')}"
            )
    else:
        lines.append("- No RED indicators this period.")

    lines.append("\n## 2. ABP assumption status\n")
    status_icons = {"HOLDING": "✓ HOLDING", "WATCH": "⚠ WATCH", "AT_RISK": "✗ AT RISK", "BREACHED": "✗ BREACHED"}
    for k, v in abp.items():
        icon = status_icons.get(v["status"], v["status"])
        desc = ABP_ASSUMPTIONS.get(k, "")
        lines.append(f"- **{k} — {icon}**: {desc}")
        lines.append(f"  - _Evidence: {v['evidence']}_")
        if v.get("recommendation"):
            lines.append(f"  - _Action: {v['recommendation']}_")

    lines.append("\n## 3. Hedging actions triggered\n")
    if hedging:
        for hid, h in hedging.items():
            lines.append(f"- **{h['short']}**")
            lines.append(f"  - {h['full']}")
    else:
        lines.append("- No hedging actions triggered this period.")

    lines.append(
        "\n---\n_Brief generated without LLM (ANTHROPIC_API_KEY not set). "
        "Set the env var to receive a Claude-authored synthesis._"
    )
    return "\n".join(lines)


def claude_brief(system_status, all_alerts):
    try:
        import anthropic
    except ImportError:
        return None, "anthropic package not installed"

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "ANTHROPIC_API_KEY not set"

    client = anthropic.Anthropic(api_key=api_key)

    abp_evaluated = json.dumps(system_status.get("abp_status", {}), indent=2)
    top_reds = json.dumps(system_status.get("red_indicators", [])[:10], indent=2)
    hedging_defs = json.dumps(
        {k: v["full"] for k, v in HEDGING_ACTIONS.items()}, indent=2
    )

    prompt = f"""You are the CI analyst for Radisson Hotel Group.

The EWS system has just run. Write a 450-word board brief with exactly three sections:

1. **Top risks this period** (max 3 items, only RED alerts — cite the exact metric value)
2. **ABP assumption status** (go through each assumption: state HOLDING / AT RISK / BREACHED and why, in one sentence each)
3. **Hedging actions triggered** (list only the actions that were actually triggered; give the owner, the specific action, and a deadline)

Write in direct, evidence-based board English. No jargon. No preamble.

ACTIVE RED INDICATORS (top 10):
{top_reds}

ABP ASSUMPTION EVALUATION (pre-computed):
{abp_evaluated}

HEDGING ACTION DEFINITIONS:
{hedging_defs}

Output only the brief text. Start with the heading "# Board Brief — Radisson CI"."""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1400,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text, None
    except Exception as e:
        return None, f"Claude API error: {e}"


def run():
    all_alerts = load_alerts()
    abp_status = evaluate_abp(all_alerts)
    system_status = derive_system_status(all_alerts, abp_status)

    with open(os.path.join(OUTPUT_DIR, "system_status.json"), "w", encoding="utf-8") as f:
        json.dump(system_status, f, indent=2, ensure_ascii=False)

    brief, err = claude_brief(system_status, all_alerts)
    if brief is None:
        print(f"Claude unavailable ({err}). Writing deterministic brief.")
        brief = fallback_brief(system_status, all_alerts)
    else:
        print("Claude-authored brief generated.")

    with open(os.path.join(OUTPUT_DIR, "board_brief.md"), "w", encoding="utf-8") as f:
        f.write(brief)

    at_risk = system_status.get("abp_at_risk", [])
    print(
        f"Orchestrator: {system_status['overall_status']} — "
        f"{system_status['red_indicator_count']} RED · "
        f"{len(at_risk)} ABP assumption(s) at risk ({', '.join(at_risk) or 'none'})"
    )
    return system_status


if __name__ == "__main__":
    run()
