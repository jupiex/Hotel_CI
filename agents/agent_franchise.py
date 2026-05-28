"""
Agent 13 — Franchise Partner Health
Monitors revenue performance vs. budget, management team stability, franchise
fee payment status, and owner/franchisee company financial distress signals.

KITs:
  KIT_1  Revenue performance vs. budget — properties materially below plan
  KIT_2  Management team changes — GM/key executive departures at risk sites
  KIT_3  Franchise fee payment status — overdue and disputed invoices
  KIT_4  Franchisee company distress — owner leverage and credit signals
"""

import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "franchise"
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "franchise")
OUT_DIR  = os.path.join(ROOT, "outputs")
OUT_PATH = os.path.join(OUT_DIR, f"alerts_{AGENT_NAME}.json")

ABP_ASSUMPTIONS = {
    "A10": "Franchise partner portfolio health maintained — <5% of portfolio in material distress",
}
HEDGING_ACTIONS = [
    "Monthly AR review with Finance — any invoice >45 days triggers asset manager call",
    "GM departure protocol: Regional Director on-site within 72 hours for HIGH-risk properties",
    "Annual franchisee financial health review — credit watch list maintained",
]

REVPAR_VS_BUDGET_RED    = -15.0  # >15% below budget = RED
REVPAR_VS_BUDGET_YELLOW = -7.5


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


# ─── KIT 1: Revenue performance ──────────────────────────────────────────────

def kit1_revenue_performance():
    df, err = safe_read("revenue_performance.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_1", "name": "Franchise revenue vs. budget",
            "description": "Properties materially below RevPAR budget — franchise stability risk",
            "value": None, "unit": "properties", "threshold_yellow": 2, "threshold_red": 3,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "PMS Revenue Extract", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A10",
            "property_ids": [],
        }]

    if "vs_budget_pct" in df.columns:
        df["vs_budget_pct"] = pd.to_numeric(df["vs_budget_pct"], errors="coerce")
        red_props    = df[df["vs_budget_pct"] <= REVPAR_VS_BUDGET_RED]
        yellow_props = df[(df["vs_budget_pct"] > REVPAR_VS_BUDGET_RED) & (df["vs_budget_pct"] <= REVPAR_VS_BUDGET_YELLOW)]
        n_red    = len(red_props)
        n_yellow = len(yellow_props)
        n_total  = len(df)
    else:
        n_red = n_yellow = n_total = 0; red_props = pd.DataFrame()

    red_ids = list(red_props["property_id"].astype(str)) if "property_id" in red_props.columns else []

    if n_red >= 3:
        level = "RED"
        rec   = f"{n_red}/{n_total} franchise properties >15% below RevPAR budget — performance intervention and contract review required."
    elif n_red >= 1 or n_yellow >= 3:
        level = "YELLOW"
        rec   = f"{n_red} RED + {n_yellow} YELLOW properties below RevPAR budget — commercial team engagement with owners needed."
    else:
        level = "GREEN"
        rec   = f"Franchise revenue performance acceptable — all {n_total} reviewed properties within -7.5% of budget."

    indicators.append({
        "kit": "KIT_1", "name": "Franchise revenue vs. budget",
        "description": "Properties materially below RevPAR budget — franchise stability risk",
        "value": n_red, "unit": "properties >15% below budget",
        "threshold_yellow": 1, "threshold_red": 3,
        "alert_level": level,
        "confidence": get_confidence(n_total, "official"),
        "source": "PMS Revenue Extract", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A10",
        "detail": {"properties_tracked": n_total, "red_gt15pct_below": n_red, "yellow_7_5_to_15pct_below": n_yellow},
        "property_ids": red_ids,
    })

    # Worst property
    if n_total > 0 and "vs_budget_pct" in df.columns:
        worst = df.loc[df["vs_budget_pct"].idxmin()]
        w_level = "RED" if float(worst["vs_budget_pct"]) <= REVPAR_VS_BUDGET_RED else (
            "YELLOW" if float(worst["vs_budget_pct"]) <= REVPAR_VS_BUDGET_YELLOW else "GREEN")
        indicators.append({
            "kit": "KIT_1", "name": f"Worst revenue — {worst.get('property_id','?')}",
            "description": "Franchise property furthest below RevPAR budget",
            "value": float(worst["vs_budget_pct"]), "unit": "% vs budget",
            "threshold_yellow": REVPAR_VS_BUDGET_YELLOW, "threshold_red": REVPAR_VS_BUDGET_RED,
            "alert_level": w_level,
            "confidence": "HIGH",
            "source": "PMS Revenue Extract", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"{worst.get('property_name','?')} ({worst.get('country','?')}): RevPAR EUR {worst.get('revpar_current','?')} vs budget EUR {worst.get('revpar_budget','?')} — {worst.get('vs_budget_pct','?')}% gap.",
            "abp_assumption_affected": "A10",
            "property_id": str(worst.get("property_id", "")), "country": str(worst.get("country", "")),
        })

    return indicators


# ─── KIT 2: Management changes ────────────────────────────────────────────────

def kit2_management_changes():
    df, err = safe_read("management_changes.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_2", "name": "Management team instability",
            "description": "High-risk GM and key executive vacancies at franchise properties",
            "value": None, "unit": "vacancies", "threshold_yellow": 2, "threshold_red": 3,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Internal HR Records", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A10",
            "property_ids": [],
        }]

    if "risk_level" in df.columns:
        high_risk = df[df["risk_level"].str.upper() == "HIGH"]
        med_risk  = df[df["risk_level"].str.upper() == "MEDIUM"]
        n_high    = len(high_risk)
        n_med     = len(med_risk)
    else:
        n_high = 0; n_med = len(df); high_risk = pd.DataFrame()

    high_ids = list(high_risk["property_id"].astype(str)) if "property_id" in high_risk.columns else []

    if n_high >= 3:
        level = "RED"
        rec   = f"{n_high} HIGH-risk management vacancies — guest experience and franchise stability at risk; regional escalation."
    elif n_high >= 1 or n_med >= 3:
        level = "YELLOW"
        rec   = f"{n_high} HIGH + {n_med} MEDIUM-risk management changes — recruitment urgency and interim coverage review."
    else:
        level = "GREEN"
        rec   = "No high-risk management vacancies — franchise team stability maintained."

    indicators.append({
        "kit": "KIT_2", "name": "Management team instability",
        "description": "High-risk GM and key executive vacancies at franchise properties",
        "value": n_high, "unit": "HIGH-risk vacancies",
        "threshold_yellow": 1, "threshold_red": 3,
        "alert_level": level,
        "confidence": get_confidence(len(df), "official"),
        "source": "Internal HR Records", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A10",
        "detail": {"total_changes_tracked": len(df), "high_risk": n_high, "medium_risk": n_med},
        "property_ids": high_ids,
    })

    for _, row in high_risk.iterrows():
        indicators.append({
            "kit": "KIT_2", "name": f"HIGH vacancy — {row.get('property_id','?')} {row.get('role','?')}",
            "description": f"High-risk management vacancy",
            "value": 0, "unit": "days vacant",
            "threshold_yellow": 30, "threshold_red": 60,
            "alert_level": "RED",
            "confidence": "HIGH",
            "source": "Internal HR Records", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"{row.get('property_name','?')} ({row.get('country','?')}): {row.get('role','?')} {row.get('change_type','?')} — {row.get('notes','')}",
            "abp_assumption_affected": "A10",
            "property_id": str(row.get("property_id", "")), "country": str(row.get("country", "")),
        })

    return indicators


# ─── KIT 3: Payment status ───────────────────────────────────────────────────

def kit3_payment_status():
    df, err = safe_read("payment_status.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_3", "name": "Franchise fee payment status",
            "description": "Overdue and disputed franchise fee invoices",
            "value": None, "unit": "EUR k overdue", "threshold_yellow": 50, "threshold_red": 150,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Finance AR Ledger", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A10",
            "property_ids": [],
        }]

    if "payment_status" in df.columns and "amount_eur_k" in df.columns:
        df["amount_eur_k"] = pd.to_numeric(df["amount_eur_k"], errors="coerce")
        df["days_overdue"]  = pd.to_numeric(df.get("days_overdue", 0), errors="coerce")
        overdue   = df[df["payment_status"].str.upper().isin(["OVERDUE", "PARTIAL"])]
        disputed  = df[(df.get("dispute_flag", "NO").astype(str).str.upper() == "YES")]
        total_overdue_eur_k = float(overdue["amount_eur_k"].sum())
        n_overdue  = len(overdue)
        n_disputed = len(disputed)
        n_30plus   = int((df["days_overdue"] >= 30).sum())
    else:
        total_overdue_eur_k = 0; n_overdue = n_disputed = n_30plus = 0; overdue = pd.DataFrame()

    overdue_ids = list(overdue["property_id"].astype(str).unique()) if "property_id" in overdue.columns else []

    if total_overdue_eur_k >= 150 or n_30plus >= 3:
        level = "RED"
        rec   = f"EUR {total_overdue_eur_k:.0f}k overdue across {n_overdue} invoice(s); {n_30plus} >30 days — legal notice and withhold-services review."
    elif total_overdue_eur_k >= 50 or n_overdue >= 2:
        level = "YELLOW"
        rec   = f"EUR {total_overdue_eur_k:.0f}k overdue ({n_overdue} invoice(s)) — asset manager outreach within 5 business days."
    else:
        level = "GREEN"
        rec   = "Franchise fee AR within normal collection cycle — no material overdue risk."

    indicators.append({
        "kit": "KIT_3", "name": "Franchise fee payment status",
        "description": "Overdue and disputed franchise fee invoices",
        "value": round(total_overdue_eur_k, 1), "unit": "EUR k overdue",
        "threshold_yellow": 50, "threshold_red": 150,
        "alert_level": level,
        "confidence": get_confidence(len(df), "official"),
        "source": "Finance AR Ledger", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A10",
        "detail": {"invoices_tracked": len(df), "overdue_count": n_overdue, "disputed_count": n_disputed,
                   "over_30_days": n_30plus, "total_overdue_eur_k": round(total_overdue_eur_k, 1)},
        "property_ids": overdue_ids,
    })
    return indicators


# ─── KIT 4: Franchisee distress ──────────────────────────────────────────────

def kit4_franchisee_distress():
    df, err = safe_read("franchisee_distress.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_4", "name": "Franchisee company financial distress",
            "description": "Owner / franchisee company leverage, covenant and credit watch signals",
            "value": None, "unit": "companies", "threshold_yellow": 2, "threshold_red": 3,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Creditreform / Bloomberg / Internal monitoring", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A10",
            "property_ids": [],
        }]

    if "severity" in df.columns:
        high_dist  = df[df["severity"].str.upper() == "HIGH"]
        med_dist   = df[df["severity"].str.upper() == "MEDIUM"]
        n_high     = len(high_dist)
        n_med      = len(med_dist)
    else:
        n_high = 0; n_med = len(df); high_dist = pd.DataFrame()

    # Expand affected properties (pipe-separated property IDs)
    high_prop_ids = []
    if "properties_affected" in high_dist.columns:
        for _, row in high_dist.iterrows():
            props = str(row.get("properties_affected", "")).split("|")
            high_prop_ids.extend([p.strip() for p in props if p.strip()])

    if n_high >= 2:
        level = "RED"
        rec   = f"{n_high} franchisee companies in HIGH financial distress — strategic reserve and early-termination review required."
    elif n_high >= 1 or n_med >= 3:
        level = "YELLOW"
        rec   = f"{n_high} HIGH + {n_med} MEDIUM distress signals — quarterly financial health monitoring and contingency planning."
    else:
        level = "GREEN"
        rec   = "Franchise partner financial health stable — no material distress signals."

    indicators.append({
        "kit": "KIT_4", "name": "Franchisee company financial distress",
        "description": "Owner / franchisee company leverage, covenant and credit watch signals",
        "value": n_high, "unit": "HIGH-severity distress signals",
        "threshold_yellow": 1, "threshold_red": 2,
        "alert_level": level,
        "confidence": get_confidence(len(df), "market"),
        "source": "Creditreform / Bloomberg / Internal monitoring", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A10",
        "detail": {"companies_monitored": len(df), "high_severity": n_high, "medium_severity": n_med},
        "property_ids": high_prop_ids,
    })

    # Flag each HIGH distress company
    for _, row in high_dist.iterrows():
        props_str = str(row.get("properties_affected", ""))
        prop_ids = [p.strip() for p in props_str.split("|") if p.strip()]
        indicators.append({
            "kit": "KIT_4", "name": f"Distress — {row.get('owner_company','?')[:40]}",
            "description": f"High-severity financial distress at franchise owner company",
            "value": float(row.get("ltv_pct", 0)), "unit": "LTV %",
            "threshold_yellow": 65, "threshold_red": 75,
            "alert_level": "RED",
            "confidence": "MEDIUM",
            "source": str(row.get("source", "")), "source_url": str(row.get("source_url", "")),
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"{row.get('owner_company','?')} ({row.get('country','?')}): {row.get('distress_type','?')} — {row.get('news_signal','')}",
            "abp_assumption_affected": "A10",
            "country": str(row.get("country", "")),
            "property_ids": prop_ids,
        })

    return indicators


# ─── Main run ─────────────────────────────────────────────────────────────────

def run():
    indicators = []
    indicators += kit1_revenue_performance()
    indicators += kit2_management_changes()
    indicators += kit3_payment_status()
    indicators += kit4_franchisee_distress()

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

    print(f"Franchise Partner Health: {len(indicators)} indicators — overall {overall}")
    return output


if __name__ == "__main__":
    run()
