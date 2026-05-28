"""
Agent 12 — ESG & Compliance Risk
Monitors regulatory deadline compliance, energy efficiency gaps, carbon
reporting progress, and labour standards audits across the Radisson portfolio.

KITs:
  KIT_1  Regulatory deadlines — properties/jurisdictions at risk of non-compliance
  KIT_2  Energy efficiency gaps — properties materially above intensity targets
  KIT_3  Carbon reporting progress — Scope 1 & 2 vs. 2030 trajectory
  KIT_4  Labour standards — audit findings and modern slavery risk
"""

import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "esg"
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "esg")
OUT_DIR  = os.path.join(ROOT, "outputs")
OUT_PATH = os.path.join(OUT_DIR, f"alerts_{AGENT_NAME}.json")

ABP_ASSUMPTIONS = {
    "A9": "ESG compliance maintained — no material regulatory breach or carbon penalty affecting hotel valuations",
}
HEDGING_ACTIONS = [
    "Maintain ESG compliance tracker updated quarterly with all jurisdictional deadlines",
    "Pre-approve capex budget for energy efficiency upgrades flagged as AT RISK",
    "Annual ETI/SA8000 audit programme — all managed and franchise properties",
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


# ─── KIT 1: Regulatory deadlines ─────────────────────────────────────────────

def kit1_regulatory_deadlines():
    df, err = safe_read("regulatory_deadlines.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_1", "name": "ESG regulatory deadline compliance",
            "description": "Count of ESG regulations with AT RISK compliance status across portfolio",
            "value": None, "unit": "regulations", "threshold_yellow": 1, "threshold_red": 2,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "EUR-Lex / National Regulatory Bodies", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A9",
            "property_ids": [],
        }]

    if "compliance_status" in df.columns:
        at_risk   = df[df["compliance_status"].str.upper() == "AT RISK"]
        in_prog   = df[df["compliance_status"].str.upper() == "IN PROGRESS"]
        compliant = df[df["compliance_status"].str.upper() == "COMPLIANT"]
        n_at_risk = len(at_risk)
        n_in_prog = len(in_prog)
    else:
        n_at_risk = n_in_prog = 0; at_risk = pd.DataFrame()

    # Total potential penalty exposure
    if "penalty_eur_k" in df.columns:
        total_penalty = float(df["penalty_eur_k"].sum())
        at_risk_penalty = float(at_risk["penalty_eur_k"].sum()) if len(at_risk) > 0 else 0
    else:
        total_penalty = at_risk_penalty = 0

    # Collect affected property IDs
    if "affected_property_count" in at_risk.columns:
        affected_props = int(at_risk["affected_property_count"].sum())
    else:
        affected_props = 0

    if n_at_risk >= 3:
        level = "RED"
        rec   = f"{n_at_risk} regulations AT RISK — EUR {at_risk_penalty:.0f}k penalty exposure; immediate compliance programme required."
    elif n_at_risk >= 1:
        level = "YELLOW"
        rec   = f"{n_at_risk} regulation(s) AT RISK — EUR {at_risk_penalty:.0f}k exposure; remediation plans to be submitted within 30 days."
    else:
        level = "GREEN"
        rec   = f"All {len(df)} tracked regulations compliant or on track — no immediate penalty risk."

    indicators.append({
        "kit": "KIT_1", "name": "ESG regulatory deadline compliance",
        "description": "Count of ESG regulations with AT RISK compliance status across portfolio",
        "value": n_at_risk, "unit": "regulations AT RISK",
        "threshold_yellow": 1, "threshold_red": 3,
        "alert_level": level,
        "confidence": get_confidence(len(df), "official"),
        "source": "EUR-Lex / National Regulatory Bodies", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A9",
        "detail": {"at_risk": n_at_risk, "in_progress": n_in_prog, "compliant": len(compliant) if "compliant" in dir() else 0,
                   "total_penalty_eur_k": round(total_penalty, 0), "at_risk_penalty_eur_k": round(at_risk_penalty, 0)},
        "property_ids": [],
    })

    # Flag each AT RISK regulation separately
    for _, row in at_risk.iterrows():
        indicators.append({
            "kit": "KIT_1", "name": f"AT RISK: {row.get('regulation_name','?')[:50]}",
            "description": str(row.get("description", ""))[:120],
            "value": float(row.get("penalty_eur_k", 0)), "unit": "EUR k penalty",
            "threshold_yellow": 50, "threshold_red": 200,
            "alert_level": "RED",
            "confidence": "HIGH",
            "source": str(row.get("source", "")), "source_url": str(row.get("source_url", "")),
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Jurisdiction: {row.get('jurisdiction','?')} | Deadline: {row.get('deadline_date','?')} | {row.get('requirement_type','?')}",
            "abp_assumption_affected": "A9",
            "country": str(row.get("jurisdiction", "")),
            "property_ids": [],
        })

    return indicators


# ─── KIT 2: Energy efficiency gaps ───────────────────────────────────────────

def kit2_energy_efficiency():
    df, err = safe_read("energy_efficiency.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_2", "name": "Portfolio energy intensity gaps",
            "description": "Properties materially above kWh/room-night intensity target",
            "value": None, "unit": "properties", "threshold_yellow": 5, "threshold_red": 10,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Internal Energy Audit", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A9",
            "property_ids": [],
        }]

    if "gap_pct" in df.columns:
        df["gap_pct"] = pd.to_numeric(df["gap_pct"], errors="coerce")
        red_props    = df[df["gap_pct"] <= -30]    # >30% above target = RED
        yellow_props = df[(df["gap_pct"] > -30) & (df["gap_pct"] <= -15)]
        n_red        = len(red_props)
        n_yellow     = len(yellow_props)
        n_total      = len(df)
    else:
        n_red = n_yellow = n_total = 0; red_props = pd.DataFrame()

    # Total capex to fix red properties
    if "capex_needed_eur_k" in df.columns and len(red_props) > 0:
        capex_red = float(red_props["capex_needed_eur_k"].sum())
    else:
        capex_red = 0

    red_ids = list(red_props["property_id"].astype(str)) if "property_id" in red_props.columns else []

    if n_red >= 8:
        level = "RED"
        rec   = f"{n_red}/{n_total} properties >30% above energy target — EUR {capex_red:.0f}k capex required; carbon penalty risk escalating."
    elif n_red >= 4 or n_yellow >= 8:
        level = "YELLOW"
        rec   = f"{n_red} RED + {n_yellow} YELLOW properties — phased energy capex programme to be approved at next investment committee."
    else:
        level = "GREEN"
        rec   = f"{n_total - n_red - n_yellow} of {n_total} properties meeting or near energy targets."

    indicators.append({
        "kit": "KIT_2", "name": "Portfolio energy intensity gaps",
        "description": "Properties materially above kWh/room-night intensity target",
        "value": n_red, "unit": "properties >30% above target",
        "threshold_yellow": 4, "threshold_red": 8,
        "alert_level": level,
        "confidence": get_confidence(n_total, "official"),
        "source": "Internal Energy Audit", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A9",
        "detail": {"properties_audited": n_total, "red_gt30pct_above": n_red, "yellow_15_30pct_above": n_yellow,
                   "capex_red_eur_k": round(capex_red, 0)},
        "property_ids": red_ids,
    })

    # Worst single property
    if n_total > 0 and "gap_pct" in df.columns:
        worst = df.loc[df["gap_pct"].idxmin()]
        w_level = "RED" if float(worst["gap_pct"]) <= -30 else ("YELLOW" if float(worst["gap_pct"]) <= -15 else "GREEN")
        indicators.append({
            "kit": "KIT_2", "name": f"Worst energy gap — {worst.get('property_id','?')}",
            "description": "Property furthest above energy intensity target",
            "value": float(worst["gap_pct"]), "unit": "% gap to target",
            "threshold_yellow": -15, "threshold_red": -30,
            "alert_level": w_level,
            "confidence": "HIGH",
            "source": "Internal Energy Audit", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"{worst.get('property_name','?')} ({worst.get('country','?')}): {worst.get('energy_intensity_kwh_per_room_night','?')} kWh/RN vs target {worst.get('target_kwh_per_room_night','?')} — capex EUR {worst.get('capex_needed_eur_k','?')}k",
            "abp_assumption_affected": "A9",
            "property_id": str(worst.get("property_id", "")), "country": str(worst.get("country", "")),
        })

    return indicators


# ─── KIT 3: Carbon reporting progress ────────────────────────────────────────

def kit3_carbon_reporting():
    df, err = safe_read("carbon_reporting.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_3", "name": "Carbon reduction trajectory vs 2030 target",
            "description": "Scope 1 + 2 emissions progress against 2030 reduction commitments",
            "value": None, "unit": "pathways off-track", "threshold_yellow": 2, "threshold_red": 4,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Internal Carbon Report / GHG Protocol", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A9",
            "property_ids": [],
        }]

    if "on_track" in df.columns:
        off_track = df[df["on_track"].str.upper() == "NO"]
        on_track  = df[df["on_track"].str.upper() == "YES"]
        n_off     = len(off_track)
        n_on      = len(on_track)
    else:
        n_off = len(df); n_on = 0; off_track = df

    n_total = len(df)

    if n_off >= 5:
        level = "RED"
        rec   = f"{n_off}/{n_total} Scope 1+2 pathways off-track for 2030 — SBTi commitment at risk; CSRD reporting exposure."
    elif n_off >= 3:
        level = "YELLOW"
        rec   = f"{n_off}/{n_total} carbon pathways off-track — accelerate decarbonisation investments to maintain 2030 target."
    else:
        level = "GREEN"
        rec   = f"{n_on}/{n_total} Scope 1+2 pathways on track for 2030 target — continue current trajectory."

    indicators.append({
        "kit": "KIT_3", "name": "Carbon reduction trajectory vs 2030 target",
        "description": "Scope 1 + 2 emissions progress against 2030 reduction commitments",
        "value": n_off, "unit": "pathways off-track",
        "threshold_yellow": 3, "threshold_red": 5,
        "alert_level": level,
        "confidence": get_confidence(n_total, "official"),
        "source": "Internal Carbon Report / GHG Protocol", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A9",
        "detail": {"pathways_tracked": n_total, "off_track": n_off, "on_track": n_on},
        "property_ids": [],
    })
    return indicators


# ─── KIT 4: Labour standards ─────────────────────────────────────────────────

def kit4_labour_standards():
    df, err = safe_read("labour_standards.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_4", "name": "Labour standards audit findings",
            "description": "ETI/SA8000 audit results and labour rights compliance across portfolio",
            "value": None, "unit": "critical findings", "threshold_yellow": 1, "threshold_red": 2,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Internal HR Audit", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A9",
            "property_ids": [],
        }]

    if "audit_result" in df.columns:
        critical   = df[df["audit_result"].str.upper().str.contains("CRITICAL")]
        improve    = df[df["audit_result"].str.upper().str.contains("IMPROVEMENT")]
        satisfact  = df[df["audit_result"].str.upper().str.contains("SATISFACTORY")]
        n_critical = len(critical)
        n_improve  = len(improve)
    else:
        n_critical = n_improve = 0; critical = pd.DataFrame()

    if "modern_slavery_risk_level" in df.columns:
        n_high_ms = int((df["modern_slavery_risk_level"].str.upper() == "HIGH").sum())
    else:
        n_high_ms = 0

    critical_ids = list(critical["property_id"].astype(str)) if "property_id" in critical.columns else []

    if n_critical >= 1 or n_high_ms >= 1:
        level = "RED"
        rec   = f"{n_critical} critical finding(s) + {n_high_ms} high modern-slavery-risk properties — immediate remediation and legal review."
    elif n_improve >= 2:
        level = "YELLOW"
        rec   = f"{n_improve} properties with 'Improvement Needed' labour audits — 90-day remediation plan required."
    else:
        level = "GREEN"
        rec   = f"All audited properties satisfactory — no critical labour rights findings."

    indicators.append({
        "kit": "KIT_4", "name": "Labour standards audit findings",
        "description": "ETI/SA8000 audit results and labour rights compliance across portfolio",
        "value": n_critical, "unit": "critical findings",
        "threshold_yellow": 0, "threshold_red": 1,
        "alert_level": level,
        "confidence": get_confidence(len(df), "official"),
        "source": "Internal HR Audit", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A9",
        "detail": {"audited_properties": len(df), "critical_findings": n_critical, "improvement_needed": n_improve,
                   "high_modern_slavery_risk": n_high_ms},
        "property_ids": critical_ids,
    })

    # Flag each critical property
    for _, row in critical.iterrows():
        indicators.append({
            "kit": "KIT_4", "name": f"Critical labour finding — {row.get('property_id','?')}",
            "description": f"Critical audit finding requiring immediate remediation",
            "value": int(row.get("grievance_cases_open", 0)), "unit": "open grievance cases",
            "threshold_yellow": 2, "threshold_red": 5,
            "alert_level": "RED",
            "confidence": "HIGH",
            "source": str(row.get("auditor", "")), "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"{row.get('property_id','?')} ({row.get('country','?')}): {row.get('audit_result','?')} | Living wage: {row.get('living_wage_compliant','?')} | Modern slavery: {row.get('modern_slavery_risk_level','?')}",
            "abp_assumption_affected": "A9",
            "property_id": str(row.get("property_id", "")), "country": str(row.get("country", "")),
        })

    return indicators


# ─── Main run ─────────────────────────────────────────────────────────────────

def run():
    indicators = []
    indicators += kit1_regulatory_deadlines()
    indicators += kit2_energy_efficiency()
    indicators += kit3_carbon_reporting()
    indicators += kit4_labour_standards()

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

    print(f"ESG & Compliance: {len(indicators)} indicators — overall {overall}")
    return output


if __name__ == "__main__":
    run()
