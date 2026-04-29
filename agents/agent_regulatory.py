"""Agent 6 - Regulatory & Macro. Energy futures, labour, policy."""
import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "regulatory"
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


def conf(n, source_type="official"):
    if source_type == "official" and n >= 5:
        return "HIGH"
    return "MEDIUM" if n >= 3 else "LOW"


def kit1_energy():
    indicators = []
    df, err = safe_read("energy_costs.csv")
    if err:
        return [{"kit": "KIT_1", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_1", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        qoq = float(r["qoq_change_pct"])
        if qoq >= 20:
            level, rec = "RED", f"Energy +{qoq:.1f}% QoQ. Hedge forward 12 months; review tariff renegotiation."
        elif qoq >= 10:
            level, rec = "YELLOW", "Cost pressure building. Run sensitivity model."
        else:
            level, rec = "GREEN", "Stable."
        indicators.append({
            "kit": "KIT_1",
            "name": "Energy futures (QoQ)",
            "market": r["market"],
            "value": round(qoq, 1),
            "unit": "% QoQ",
            "threshold_yellow": 10,
            "threshold_red": 20,
            "alert_level": level,
            "confidence": conf(n, "official"),
            "source": "EEX",
            "source_url": r.get("source_url", ""),
            "capture_date": r.get("date", ""),
            "recommendation": rec,
        })
    return indicators


def kit2_labour():
    indicators = []
    df, err = safe_read("labour_regulation.csv")
    if err:
        return [{"kit": "KIT_2", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_2", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        wage = float(r.get("wage_change_pct", 0) or 0)
        if wage >= 5:
            level, rec = "RED", f"Wage +{wage:.1f}%. Re-baseline labour cost in P&L; review service-model design."
        elif wage >= 3:
            level, rec = "YELLOW", "Modest wage pressure. Monitor."
        else:
            level, rec = "GREEN", "Within trend."
        indicators.append({
            "kit": "KIT_2",
            "name": "Labour cost change",
            "country": r["country"],
            "value": round(wage, 1),
            "unit": "%",
            "alert_level": level,
            "confidence": conf(n, "official"),
            "source": "Eurostat / national",
            "source_url": r.get("source_url", ""),
            "capture_date": r.get("effective_date", ""),
            "recommendation": rec,
        })
    return indicators


def kit3_policy():
    indicators = []
    df, err = safe_read("policy_tracker.csv")
    if err:
        return [{"kit": "KIT_3", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_3", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        months = int(r.get("months_to_compliance", 99) or 99)
        status = str(r.get("status", "")).lower()
        if status == "effective" and months <= 24:
            level = "RED"
            rec = "Live or imminent compliance deadline. Confirm CAPEX & process readiness."
        elif status in ("passed", "effective"):
            level = "YELLOW"
            rec = "On the calendar. Owner: legal."
        else:
            level = "YELLOW" if status == "proposed" else "GREEN"
            rec = "Proposed - track."
        indicators.append({
            "kit": "KIT_3",
            "name": "Policy tracker",
            "value": f"{r['policy_name']} ({status})",
            "unit": "",
            "alert_level": level,
            "confidence": conf(n, "official"),
            "source": "EUR-Lex / gazette",
            "source_url": r.get("source_url", ""),
            "capture_date": r.get("effective_date", ""),
            "recommendation": rec,
        })
    return indicators


def run():
    indicators = kit1_energy() + kit2_labour() + kit3_policy()
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
