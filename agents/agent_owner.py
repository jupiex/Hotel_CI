"""Agent 4 - Owner & Partner Intelligence.
Joins contract calendar + review-score trajectory; flags churn risk.
"""
import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "owner"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", AGENT_NAME)
OUT_PATH = os.path.join(ROOT, "outputs", f"alerts_{AGENT_NAME}.json")


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


def kit1_owner_risk():
    indicators = []
    df, err = safe_read("owner_risk.csv")
    if err:
        return [{"kit": "KIT_1", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_1", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        months = int(r["months_to_expiry"])
        score_drop = float(r["score_delta_90d"])
        competing = str(r["competing_operator_signal"]).strip().lower() in ("true", "1", "yes")
        # Logic: contract <18mo + (score drop >0.3 OR competing operator) -> RED
        churn_signal = (months <= 18 and score_drop <= -0.3) or (months <= 24 and competing)
        if churn_signal:
            level = "RED"
            triggers = []
            if months <= 18 and score_drop <= -0.3:
                triggers.append(f"score down {score_drop} with only {months} months to expiry")
            if competing:
                triggers.append("competing operator approached owner")
            rec = ("Churn risk: " + "; ".join(triggers) +
                   ". Asset management should open renewal conversation now.")
        elif months <= 24:
            level = "YELLOW"
            rec = f"Contract expires in {months} months. Schedule owner review."
        else:
            level = "GREEN"
            rec = "Contract horizon stable."
        indicators.append({
            "kit": "KIT_1",
            "name": "Owner churn risk",
            "property": r["property_name"],
            "value": f"{months}mo to expiry, score Δ {score_drop}",
            "unit": "",
            "alert_level": level,
            "confidence": conf(n),
            "source": "Reltio + Revinate (joined)",
            "source_url": "",
            "capture_date": datetime.utcnow().date().isoformat(),
            "owner_company": r["owner_company"],
            "competing_operator_signal": competing,
            "recommendation": rec,
        })
    return indicators


def run():
    indicators = kit1_owner_risk()
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
