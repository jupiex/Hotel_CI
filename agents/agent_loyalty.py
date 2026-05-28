"""
Agent 11 — Loyalty Programme Intelligence
Monitors competitor loyalty rule changes, bonus promotions, Radisson Rewards
programme health metrics, and member satisfaction gaps vs. rivals.

KITs:
  KIT_1  Competitor rule changes — devaluation or improvement signals
  KIT_2  Competitor bonus promotions — campaigns cannibalising Radisson share
  KIT_3  Radisson programme health — enrolment, redemption, NPS trends
  KIT_4  Member satisfaction gap vs. competition
"""

import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "loyalty"
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "loyalty")
OUT_DIR  = os.path.join(ROOT, "outputs")
OUT_PATH = os.path.join(OUT_DIR, f"alerts_{AGENT_NAME}.json")

ABP_ASSUMPTIONS = {
    "A8": "Radisson Rewards retains competitive parity — no material member share loss to rival programmes",
}
HEDGING_ACTIONS = [
    "Maintain a 'competitor move' response fund (EUR 2m) for rapid counter-promotions",
    "Quarterly loyalty benchmarking review with CMO and VP Loyalty",
    "NPS recovery threshold: trigger programme audit if member NPS drops below 40",
]


def safe_read(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None, f"{filename} not found"
    try:
        df = pd.read_csv(path)
        if df.empty:
            return None, f"{filename} is empty"
        return df, None
    except Exception as e:
        return None, str(e)


def get_confidence(n_records, source_type="official"):
    if source_type == "official" and n_records >= 5:
        return "HIGH"
    if source_type == "official":
        return "MEDIUM"
    if n_records >= 10:
        return "MEDIUM"
    if n_records >= 3:
        return "MEDIUM"
    return "LOW"


def compute_overall(indicators):
    levels = [i["alert_level"] for i in indicators]
    if all(l == "NO_DATA" for l in levels):
        return "NO_DATA"
    if "RED" in levels:
        return "RED"
    if "YELLOW" in levels:
        return "YELLOW"
    return "GREEN"


# ─── KIT 1: Competitor rule changes ──────────────────────────────────────────

def kit1_competitor_rule_changes():
    df, err = safe_read("competitor_rule_changes.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_1", "name": "Competitor loyalty rule changes",
            "description": "Major rule changes by rival programmes (devaluations, tier shifts, new benefits)",
            "value": None, "unit": "changes", "threshold_yellow": 1, "threshold_red": 2,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Programme announcements / Points Guy", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A8",
        }]

    if "impact_level" in df.columns:
        n_high = int((df["impact_level"].str.upper() == "HIGH").sum())
        n_med  = int((df["impact_level"].str.upper() == "MEDIUM").sum())
    else:
        n_high = 0; n_med = len(df)

    n_total = len(df)

    if n_high >= 2:
        level = "RED"
        rec   = f"{n_high} HIGH-impact competitor rule changes detected — Radisson Rewards response review required."
    elif n_high >= 1 or n_med >= 3:
        level = "YELLOW"
        rec   = f"{n_high} high + {n_med} medium impact competitor changes — loyalty strategy team to assess member migration risk."
    else:
        level = "GREEN"
        rec   = f"{n_total} competitor changes tracked — no material threat to Radisson Rewards competitiveness."

    indicators.append({
        "kit": "KIT_1", "name": "Competitor loyalty rule changes",
        "description": "Major rule changes by rival programmes (devaluations, tier shifts, new benefits)",
        "value": n_high, "unit": "HIGH-impact changes",
        "threshold_yellow": 1, "threshold_red": 2,
        "alert_level": level,
        "confidence": get_confidence(n_total, "official"),
        "source": "Programme announcements / Points Guy", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A8",
        "detail": {"high_impact": n_high, "medium_impact": n_med, "total_changes": n_total},
    })
    return indicators


# ─── KIT 2: Competitor bonus promotions ──────────────────────────────────────

def kit2_competitor_promotions():
    df, err = safe_read("competitor_promotions.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_2", "name": "Competitor bonus promotions active",
            "description": "Live competitor loyalty promotions competing for Radisson member stays",
            "value": None, "unit": "promotions", "threshold_yellow": 3, "threshold_red": 5,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Competitor programme websites", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A8",
        }]

    today_str = datetime.now(timezone.utc).date().isoformat()
    if "end_date" in df.columns:
        df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
        active = df[df["end_date"] >= pd.Timestamp(today_str)]
    else:
        active = df

    # Exclude Radisson's own promotions
    if "competitor_programme" in active.columns:
        competitor_active = active[~active["competitor_programme"].str.contains("Radisson", case=False, na=False)]
    else:
        competitor_active = active

    n_active    = len(competitor_active)
    if "bonus_multiplier" in competitor_active.columns:
        high_mult = competitor_active[pd.to_numeric(competitor_active["bonus_multiplier"], errors="coerce") >= 3.0]
        n_triple  = len(high_mult)
    else:
        n_triple = 0

    if n_triple >= 2 or n_active >= 5:
        level = "RED"
        rec   = f"{n_active} competitor promotions active; {n_triple} with ≥3x multiplier — counter-promotion or matched offer needed."
    elif n_active >= 3:
        level = "YELLOW"
        rec   = f"{n_active} active competitor promotions — monitor member booking shifts and consider targeted counter offer."
    else:
        level = "GREEN"
        rec   = f"{n_active} competitor promotions active — promotional landscape manageable."

    indicators.append({
        "kit": "KIT_2", "name": "Competitor bonus promotions active",
        "description": "Live competitor loyalty promotions competing for Radisson member stays",
        "value": n_active, "unit": "active competitor promotions",
        "threshold_yellow": 3, "threshold_red": 5,
        "alert_level": level,
        "confidence": get_confidence(len(df), "official"),
        "source": "Competitor programme websites", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A8",
        "detail": {"active_promotions": n_active, "triple_plus_multiplier": n_triple},
    })
    return indicators


# ─── KIT 3: Radisson programme health ────────────────────────────────────────

def kit3_programme_health():
    df, err = safe_read("radisson_programme_health.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_3", "name": "Radisson Rewards programme health",
            "description": "Key programme health metrics: enrolment, redemption, NPS, breakage",
            "value": None, "unit": "metrics", "threshold_yellow": 2, "threshold_red": 4,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Internal CRM / Actuarial", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A8",
        }]

    if "change_pct" in df.columns and "metric" in df.columns:
        df["change_pct"] = pd.to_numeric(df["change_pct"], errors="coerce")
        # Metrics where negative change = deterioration
        declining = df[df["change_pct"] < -10]
        n_red_metrics    = int((df["change_pct"] < -20).sum())
        n_yellow_metrics = int(((df["change_pct"] >= -20) & (df["change_pct"] < -10)).sum())
    else:
        n_red_metrics = n_yellow_metrics = 0

    n_total = len(df)

    if n_red_metrics >= 3:
        level = "RED"
        rec   = f"{n_red_metrics} programme health metrics declining >20% — systemic loyalty programme degradation; VP Loyalty escalation required."
    elif n_red_metrics >= 1 or n_yellow_metrics >= 3:
        level = "YELLOW"
        rec   = f"{n_red_metrics} red + {n_yellow_metrics} yellow health metrics — programme health review needed."
    else:
        level = "GREEN"
        rec   = f"All {n_total} programme health metrics within acceptable range."

    indicators.append({
        "kit": "KIT_3", "name": "Radisson Rewards programme health",
        "description": "Key programme health metrics: enrolment, redemption, NPS, breakage",
        "value": n_red_metrics, "unit": "metrics declining >20%",
        "threshold_yellow": 1, "threshold_red": 3,
        "alert_level": level,
        "confidence": get_confidence(n_total, "official"),
        "source": "Internal CRM / Actuarial", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A8",
        "detail": {"metrics_tracked": n_total, "red_gt_20pct_decline": n_red_metrics, "yellow_10_20pct_decline": n_yellow_metrics},
    })

    # Worst single metric
    if "change_pct" in df.columns and n_total > 0:
        worst = df.loc[df["change_pct"].idxmin()]
        w_level = "RED" if float(worst["change_pct"]) < -20 else ("YELLOW" if float(worst["change_pct"]) < -10 else "GREEN")
        indicators.append({
            "kit": "KIT_3", "name": f"Metric — {worst.get('metric','?')} ({worst.get('region','?')})",
            "description": "Worst-performing Radisson Rewards programme health metric",
            "value": float(worst["change_pct"]), "unit": "% change vs prior year",
            "threshold_yellow": -10, "threshold_red": -20,
            "alert_level": w_level,
            "confidence": get_confidence(n_total, "official"),
            "source": str(worst.get("source", "Internal")), "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"{worst.get('metric','?')} ({worst.get('region','?')}): {worst.get('value_current','?')} vs PY {worst.get('value_py','?')} — {worst.get('notes','')}",
            "abp_assumption_affected": "A8",
        })

    return indicators


# ─── KIT 4: Member satisfaction gap ──────────────────────────────────────────

def kit4_member_satisfaction():
    df, err = safe_read("member_satisfaction.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_4", "name": "Member satisfaction gap vs. competitors",
            "description": "Radisson Rewards satisfaction scores vs top competitor programmes",
            "value": None, "unit": "score gap", "threshold_yellow": -10, "threshold_red": -15,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "J.D. Power EMEA Hotel Loyalty Survey", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A8",
        }]

    if "gap" in df.columns:
        df["gap"] = pd.to_numeric(df["gap"], errors="coerce")
        avg_gap  = float(df["gap"].mean())
        worst_gap = float(df["gap"].min())
        n_large_gap = int((df["gap"] <= -15).sum())
    else:
        avg_gap = worst_gap = 0; n_large_gap = 0

    if worst_gap <= -20 or n_large_gap >= 3:
        level = "RED"
        rec   = f"Avg gap {avg_gap:.1f} pts vs competitors; worst {worst_gap:.1f} pts — major competitiveness deficit; programme redesign needed."
    elif worst_gap <= -15 or avg_gap <= -10:
        level = "YELLOW"
        rec   = f"Average gap {avg_gap:.1f} pts vs competitors — loyalty strategy review and targeted benefits enhancement required."
    else:
        level = "GREEN"
        rec   = f"Average satisfaction gap {avg_gap:.1f} pts vs competitors — within acceptable range."

    indicators.append({
        "kit": "KIT_4", "name": "Member satisfaction gap vs. competitors",
        "description": "Radisson Rewards satisfaction scores vs top competitor programmes",
        "value": round(avg_gap, 1), "unit": "avg points gap (Radisson vs rival)",
        "threshold_yellow": -10, "threshold_red": -15,
        "alert_level": level,
        "confidence": get_confidence(len(df), "official"),
        "source": "J.D. Power EMEA Hotel Loyalty Survey", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A8",
        "detail": {"avg_gap": round(avg_gap, 1), "worst_gap": round(worst_gap, 1), "metrics_with_gap_gt_15": n_large_gap},
    })
    return indicators


# ─── Main run ─────────────────────────────────────────────────────────────────

def run():
    indicators = []
    indicators += kit1_competitor_rule_changes()
    indicators += kit2_competitor_promotions()
    indicators += kit3_programme_health()
    indicators += kit4_member_satisfaction()

    overall = compute_overall(indicators)

    output = {
        "agent":           AGENT_NAME,
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "overall_status":  overall,
        "abp_assumptions": ABP_ASSUMPTIONS,
        "hedging_actions": HEDGING_ACTIONS,
        "indicators":      indicators,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Loyalty Intelligence: {len(indicators)} indicators — overall {overall}")
    return output


if __name__ == "__main__":
    run()
