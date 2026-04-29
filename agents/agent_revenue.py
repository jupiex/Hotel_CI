"""Agent 3 - Revenue Intelligence. Property-level rate parity, demand events, review scores."""
import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "revenue"
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


def conf(n, source_type="industry"):
    if source_type == "official" and n >= 5:
        return "HIGH"
    return "MEDIUM" if n >= 3 else "LOW"


def kit1_parity():
    indicators = []
    df, err = safe_read("rate_parity.csv")
    if err:
        return [{"kit": "KIT_1", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_1", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        gap = float(r["parity_gap_pct"])
        if gap > 5:
            level, rec = "RED", f"OTA undercutting Radisson.com by {gap:.1f}%. Re-price within 24h."
        elif gap > 2:
            level, rec = "YELLOW", "Minor parity drift. Verify rate plan mapping."
        else:
            level, rec = "GREEN", "Parity intact."
        indicators.append({
            "kit": "KIT_1",
            "name": "OTA rate parity gap",
            "property": r["property_name"],
            "market": r["market"],
            "value": round(gap, 1),
            "unit": "%",
            "threshold_yellow": 2,
            "threshold_red": 5,
            "alert_level": level,
            "confidence": conf(n, "industry"),
            "source": r.get("source", "OTA Insight"),
            "source_url": "https://www.otainsight.com",
            "capture_date": r.get("date", ""),
            "recommendation": rec,
        })
    return indicators


def kit2_events():
    indicators = []
    df, err = safe_read("demand_events.csv")
    if err:
        return [{"kit": "KIT_2", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_2", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        in_fcst = str(r["in_forecast"]).strip().lower() in ("true", "1", "yes")
        attendance = int(r["estimated_attendance"])
        if attendance > 10000 and not in_fcst:
            level = "RED"
            rec = "Major event missing from forecast. Push rates +15-25% on event nights."
        elif not in_fcst:
            level = "YELLOW"
            rec = "Confirm with revenue manager."
        else:
            level = "GREEN"
            rec = "In forecast."
        indicators.append({
            "kit": "KIT_2",
            "name": "Demand event vs forecast",
            "market": r["market"],
            "value": f"{r['event_name']} ({attendance:,})",
            "unit": "",
            "alert_level": level,
            "confidence": conf(n, "industry"),
            "source": "PredictHQ",
            "source_url": r.get("source_url", ""),
            "capture_date": r.get("event_date", ""),
            "recommendation": rec,
        })
    return indicators


def kit3_reviews():
    indicators = []
    df, err = safe_read("review_scores.csv")
    if err:
        return [{"kit": "KIT_3", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_3", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        delta = float(r["score_delta_30d"])
        comp_gap = float(r["radisson_score"]) - float(r["comp_set_avg_score"])
        if delta <= -0.3:
            level = "RED"
            rec = "Score dropping fast. Brief GM; pull guest comments for root cause."
        elif comp_gap < -0.2:
            level = "YELLOW"
            rec = "Trailing comp set. Review service recovery program."
        else:
            level = "GREEN"
            rec = "On track."
        indicators.append({
            "kit": "KIT_3",
            "name": "Review score velocity vs comp set",
            "property": r["property_name"],
            "value": round(delta, 2),
            "unit": "30d delta",
            "alert_level": level,
            "confidence": conf(n, "industry"),
            "source": r.get("platform", "Booking.com"),
            "source_url": "https://www.revinate.com",
            "capture_date": r.get("date", ""),
            "recommendation": rec,
        })
    return indicators


def run():
    indicators = kit1_parity() + kit2_events() + kit3_reviews()
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
