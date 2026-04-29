"""Agent 5 - Talent & Capability."""
import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "talent"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", AGENT_NAME)
OUT_PATH = os.path.join(ROOT, "outputs", f"alerts_{AGENT_NAME}.json")

SENIOR = {"VP", "SVP", "EVP", "C-level", "Director", "Head"}
STRATEGIC = {"tech", "commercial"}


def safe_read(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        return pd.read_csv(path), None
    except FileNotFoundError:
        return None, f"File not found: {filename}"
    except Exception as e:
        return None, f"Error reading {filename}: {e}"


def conf(n):
    return "MEDIUM" if n >= 3 else "LOW"


def kit1_movements():
    indicators = []
    df, err = safe_read("talent_movements.csv")
    if err:
        return [{"kit": "KIT_1", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_1", "alert_level": "NO_DATA"}]
    n = len(df)

    # Aggregate: count Radisson GM departures in last 60 days
    rad_left = df[(df["company"].str.lower() == "radisson") & (df["direction"].str.lower() == "left")]
    if len(rad_left) >= 2:
        indicators.append({
            "kit": "KIT_1",
            "name": "Radisson GM cluster departure",
            "value": f"{len(rad_left)} GMs left in window",
            "unit": "",
            "alert_level": "RED",
            "confidence": conf(n),
            "source": "LinkedIn profile changes",
            "source_url": "https://www.linkedin.com",
            "capture_date": datetime.utcnow().date().isoformat(),
            "recommendation": "Cluster of GM departures. HR briefing required; check exit-interview themes.",
        })

    for _, r in df.iterrows():
        senior = str(r.get("seniority", "")).strip() in SENIOR
        strategic = str(r.get("category", "")).strip() in STRATEGIC
        joined_rival = (str(r.get("direction", "")).lower() == "joined" and
                        str(r.get("company", "")).lower() != "radisson")
        if joined_rival and senior and strategic:
            level = "RED"
            rec = "Senior strategic hire at rival. Capability gap closing."
        elif joined_rival and strategic:
            level = "YELLOW"
            rec = "Watch."
        else:
            level = "GREEN"
            rec = "Routine."
        indicators.append({
            "kit": "KIT_1",
            "name": "Talent movement",
            "value": f"{r['company']} {r['direction']} {r['seniority']} {r['role_title']}",
            "unit": "",
            "alert_level": level,
            "confidence": conf(n),
            "source": "LinkedIn",
            "source_url": r.get("linkedin_url", ""),
            "capture_date": r.get("effective_date", ""),
            "recommendation": rec,
        })
    return indicators


def kit2_signals():
    indicators = []
    df, err = safe_read("rival_capability_signals.csv")
    if err:
        return [{"kit": "KIT_2", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_2", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        st = str(r.get("signal_type", "")).lower()
        level = "YELLOW" if st in ("product_release", "partnership") else "GREEN"
        indicators.append({
            "kit": "KIT_2",
            "name": "Rival capability signal",
            "value": f"{r['company']}: {r['description']}",
            "unit": "",
            "alert_level": level,
            "confidence": conf(n),
            "source": "Press / company news",
            "source_url": r.get("source_url", ""),
            "capture_date": r.get("date", ""),
            "recommendation": r.get("strategic_implication", "Monitor."),
        })
    return indicators


def run():
    indicators = kit1_movements() + kit2_signals()
    levels = [i.get("alert_level") for i in indicators]
    overall = "RED" if "RED" in levels else "YELLOW" if "YELLOW" in levels else \
              "GREEN" if all(l == "GREEN" for l in levels) else "NO_DATA"
    out = {
        "agent": AGENT_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overall_status": overall,
        "indicators": indicators,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Agent {AGENT_NAME}: {overall} - {len(indicators)} indicators")
    return out


if __name__ == "__main__":
    run()
