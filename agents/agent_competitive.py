"""Agent 2 - Competitive Surveillance.
Tracks rival signings (esp. in Radisson target markets), capability hires, loyalty changes.
"""
import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "competitive"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", AGENT_NAME)
OUT_PATH = os.path.join(ROOT, "outputs", f"alerts_{AGENT_NAME}.json")

TECH_CATEGORIES = {"tech", "commercial"}
SENIOR_LEVELS = {"VP", "SVP", "EVP", "C-level", "Head", "Director"}


def safe_read(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        return pd.read_csv(path), None
    except FileNotFoundError:
        return None, f"File not found: {filename}"
    except Exception as e:
        return None, f"Error reading {filename}: {e}"


def confidence(n, source_type="industry"):
    if source_type == "official" and n >= 5:
        return "HIGH"
    if n >= 10:
        return "MEDIUM"
    if n >= 3:
        return "MEDIUM"
    return "LOW"


def kit1_signings():
    indicators = []
    df, err = safe_read("competitor_signings.csv")
    if err:
        return [{"kit": "KIT_1", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_1", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        in_target = str(r.get("in_radisson_target_market", "")).strip().lower() in ("true", "1", "yes")
        level = "RED" if in_target else "YELLOW"
        rec = ("Rival signed in our target market. Accelerate Radisson term-sheet for any "
               "live opportunity in same submarket.") if in_target else "Monitor."
        indicators.append({
            "kit": "KIT_1",
            "name": "Rival signing in target market",
            "rival": r["rival"],
            "market": r["market"],
            "country": r["country"],
            "value": r["property_name"],
            "unit": "",
            "alert_level": level,
            "confidence": confidence(n, "industry"),
            "source": "Press / STR Pipeline",
            "source_url": r.get("source_url", ""),
            "capture_date": r.get("signing_date", ""),
            "recommendation": rec,
        })
    return indicators


def kit2_capability_hires():
    indicators = []
    df, err = safe_read("rival_job_postings.csv")
    if err:
        return [{"kit": "KIT_2", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_2", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        is_senior = str(r.get("seniority", "")).strip() in SENIOR_LEVELS
        is_strategic = str(r.get("category", "")).strip() in TECH_CATEGORIES
        if is_senior and is_strategic:
            level = "RED"
            rec = "Rival is investing in capability Radisson lacks. Brief CIO/CCO."
        elif is_strategic:
            level = "YELLOW"
            rec = "Watch hire trajectory at this rival."
        else:
            level = "GREEN"
            rec = "Routine ops hire."
        indicators.append({
            "kit": "KIT_2",
            "name": "Rival capability hire",
            "rival": r["rival"],
            "value": f"{r['seniority']} {r['role_title']}",
            "unit": "",
            "alert_level": level,
            "confidence": confidence(n, "industry"),
            "source": "LinkedIn job postings",
            "source_url": r.get("linkedin_url", ""),
            "capture_date": r.get("date_posted", ""),
            "recommendation": rec,
        })
    return indicators


def kit3_loyalty():
    indicators = []
    df, err = safe_read("loyalty_changes.csv")
    if err:
        return [{"kit": "KIT_3", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_3", "alert_level": "NO_DATA"}]
    n = len(df)
    SEV = {"LOW": "GREEN", "MED": "YELLOW", "HIGH": "RED"}
    for _, r in df.iterrows():
        level = SEV.get(str(r.get("severity", "LOW")).upper(), "YELLOW")
        if str(r.get("change_type", "")).lower() == "devaluation":
            level = "RED"
        rec = ("Devaluation may push rival's elites to switch. Brief loyalty team; "
               "consider opportunistic status-match campaign.") if level == "RED" else "Monitor T&Cs."
        indicators.append({
            "kit": "KIT_3",
            "name": "Rival loyalty rule change",
            "rival": r["rival"],
            "value": r["change_description"],
            "unit": "",
            "alert_level": level,
            "confidence": confidence(n, "official"),
            "source": "Loyalty T&Cs",
            "source_url": r.get("source_url", ""),
            "capture_date": r.get("effective_date", ""),
            "recommendation": rec,
        })
    return indicators


def run():
    indicators = kit1_signings() + kit2_capability_hires() + kit3_loyalty()
    levels = [i.get("alert_level") for i in indicators]
    overall = "RED" if "RED" in levels else "YELLOW" if "YELLOW" in levels else \
              "GREEN" if all(l == "GREEN" for l in levels) else "NO_DATA"
    output = {
        "agent": AGENT_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overall_status": overall,
        "indicators": indicators,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Agent {AGENT_NAME}: {overall} - {len(indicators)} indicators")
    return output


if __name__ == "__main__":
    run()
