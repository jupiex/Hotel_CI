"""
Agent 1 — Market Entry Agent
Reads three CSVs (supply pipeline, demand signals, regulatory/FX),
applies threshold logic, and writes outputs/alerts_entry.json.

Schema and pattern mirror the Inditex prototype.
"""

import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "entry"

# Resolve paths relative to project root (parent of /agents)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "entry")
OUT_PATH = os.path.join(ROOT, "outputs", f"alerts_{AGENT_NAME}.json")

THRESHOLDS = {
    # Higher value = worse
    "pipeline_pct":         {"yellow": 10, "red": 15},
    "fx_depreciation_pct":  {"yellow": 8,  "red": 15},
    # Lower value = worse (invert=True)
    "forward_pace_pct":     {"yellow": 90, "red": 80},
}

ABP_ASSUMPTIONS = {
    "A1": "Target owner signs at Radisson standard fee structure (3-4% mgmt fee)",
    "A2": "RevPAR breakeven achievable within 36 months of opening",
    "A3": "No other Radisson brand already present in same submarket",
}

HEDGING_ACTIONS = {
    "H1": "FX RED: pause LOI negotiations; add FX floor clause to any term sheet",
    "H2": "Pipeline RED: deprioritise market; redirect dev effort to next-priority country",
    "H3": "Two simultaneous REDs: full 90-day hold; escalate to development committee",
}


def get_alert_level(value, threshold_key, invert=False):
    t = THRESHOLDS[threshold_key]
    if invert:
        if value <= t["red"]:
            return "RED"
        if value <= t["yellow"]:
            return "YELLOW"
        return "GREEN"
    if value >= t["red"]:
        return "RED"
    if value >= t["yellow"]:
        return "YELLOW"
    return "GREEN"


def get_confidence(n_records, source_type):
    if source_type == "official" and n_records >= 5:
        return "HIGH"
    if n_records >= 10:
        return "MEDIUM"
    if n_records >= 3:
        return "MEDIUM"
    return "LOW"


def safe_read(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        df = pd.read_csv(path)
        return df, None
    except FileNotFoundError:
        return None, f"File not found: {filename}"
    except Exception as e:
        return None, f"Error reading {filename}: {e}"


def build_kit1_pipeline():
    indicators = []
    df, err = safe_read("supply_pipeline.csv")
    if err:
        return [{"kit": "KIT_1", "name": "Supply pipeline", "alert_level": "ERROR", "error": err}]
    if df is None or df.empty:
        return [{"kit": "KIT_1", "name": "Supply pipeline", "alert_level": "NO_DATA"}]

    n = len(df)
    for _, row in df.iterrows():
        level = get_alert_level(row["pipeline_pct"], "pipeline_pct")
        if level == "RED":
            rec = "Pause market development. Activate H2: redirect to next-priority country."
        elif level == "YELLOW":
            rec = "Monitor weekly. Review submarket exposure."
        else:
            rec = "Continue planned signings."
        indicators.append({
            "kit": "KIT_1",
            "name": "Pipeline rooms vs existing supply",
            "market": row["market"],
            "country": row["country"],
            "value": round(float(row["pipeline_pct"]), 1),
            "unit": "%",
            "threshold_yellow": THRESHOLDS["pipeline_pct"]["yellow"],
            "threshold_red": THRESHOLDS["pipeline_pct"]["red"],
            "alert_level": level,
            "confidence": get_confidence(n, "industry"),
            "source": "STR Pipeline",
            "source_url": row.get("source_url", ""),
            "capture_date": row.get("date", ""),
            "recommendation": rec,
            "abp_assumption_affected": "A2",
        })
    return indicators


def build_kit2_demand():
    indicators = []
    df, err = safe_read("demand_signals.csv")
    if err:
        return [{"kit": "KIT_2", "name": "Demand signals", "alert_level": "ERROR", "error": err}]
    if df is None or df.empty:
        return [{"kit": "KIT_2", "name": "Demand signals", "alert_level": "NO_DATA"}]

    n = len(df)
    for _, row in df.iterrows():
        level = get_alert_level(row["forward_pace_pct"], "forward_pace_pct", invert=True)
        if level == "RED":
            rec = "Demand pace below 80% prior year. Reassess opening-year P&L."
        elif level == "YELLOW":
            rec = "Demand softening. Stress-test breakeven model."
        else:
            rec = "Demand on track."
        indicators.append({
            "kit": "KIT_2",
            "name": "Forward booking pace vs prior year",
            "market": row["market"],
            "country": row["country"],
            "value": round(float(row["forward_pace_pct"]), 1),
            "unit": "% of PY",
            "threshold_yellow": THRESHOLDS["forward_pace_pct"]["yellow"],
            "threshold_red": THRESHOLDS["forward_pace_pct"]["red"],
            "alert_level": level,
            "confidence": get_confidence(n, "industry"),
            "source": "OAG airline capacity",
            "source_url": row.get("source_url", ""),
            "capture_date": row.get("date", ""),
            "recommendation": rec,
            "abp_assumption_affected": "A2",
        })
    return indicators


def build_kit3_regulatory_fx():
    indicators = []
    df, err = safe_read("regulatory_fx.csv")
    if err:
        return [{"kit": "KIT_3", "name": "Regulatory & FX", "alert_level": "ERROR", "error": err}]
    if df is None or df.empty:
        return [{"kit": "KIT_3", "name": "Regulatory & FX", "alert_level": "NO_DATA"}]

    n = len(df)
    for _, row in df.iterrows():
        fx = abs(float(row["fx_vs_eur_6mo_pct"]))
        level = get_alert_level(fx, "fx_depreciation_pct")
        if level == "RED":
            rec = "FX depreciation >15%. Activate H1: pause LOI; add FX floor clause."
        elif level == "YELLOW":
            rec = "FX volatility elevated. Re-price term sheets."
        else:
            rec = "FX stable. No action required."
        indicators.append({
            "kit": "KIT_3",
            "name": "FX depreciation vs EUR (6mo)",
            "market": row["market"],
            "country": row["country"],
            "value": round(fx, 1),
            "unit": "%",
            "threshold_yellow": THRESHOLDS["fx_depreciation_pct"]["yellow"],
            "threshold_red": THRESHOLDS["fx_depreciation_pct"]["red"],
            "alert_level": level,
            "confidence": get_confidence(n, "official"),
            "source": "ECB exchange rate feed",
            "source_url": row.get("source_url", ""),
            "capture_date": row.get("date", ""),
            "policy_notes": row.get("policy_notes", ""),
            "recommendation": rec,
            "abp_assumption_affected": "A1",
        })
    return indicators


def derive_market_status(indicators):
    """Aggregate per-market: count REDs across KITs, trigger H3 if 2+."""
    by_market = {}
    for ind in indicators:
        mk = ind.get("market")
        if not mk:
            continue
        by_market.setdefault(mk, {"country": ind.get("country", ""), "kits": [], "reds": 0, "yellows": 0})
        by_market[mk]["kits"].append({"kit": ind["kit"], "alert_level": ind["alert_level"]})
        if ind["alert_level"] == "RED":
            by_market[mk]["reds"] += 1
        elif ind["alert_level"] == "YELLOW":
            by_market[mk]["yellows"] += 1

    market_summary = []
    for market, info in by_market.items():
        if info["reds"] >= 2:
            status = "RED"
            triggered = ["H3"]
        elif info["reds"] == 1:
            status = "RED"
            triggered = ["H1 or H2 (per KIT)"]
        elif info["yellows"] > 0:
            status = "YELLOW"
            triggered = []
        else:
            status = "GREEN"
            triggered = []
        market_summary.append({
            "market": market,
            "country": info["country"],
            "status": status,
            "red_count": info["reds"],
            "yellow_count": info["yellows"],
            "kits": info["kits"],
            "hedging_triggered": triggered,
        })
    return market_summary


def run():
    indicators = []
    indicators += build_kit1_pipeline()
    indicators += build_kit2_demand()
    indicators += build_kit3_regulatory_fx()

    levels = [i.get("alert_level") for i in indicators]
    if "RED" in levels:
        overall = "RED"
    elif "YELLOW" in levels:
        overall = "YELLOW"
    elif all(l in ("GREEN",) for l in levels):
        overall = "GREEN"
    else:
        overall = "NO_DATA"

    market_summary = derive_market_status(indicators)

    output = {
        "agent": AGENT_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overall_status": overall,
        "abp_assumptions": ABP_ASSUMPTIONS,
        "hedging_actions": HEDGING_ACTIONS,
        "markets": market_summary,
        "indicators": indicators,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Agent {AGENT_NAME}: {overall} — {len(indicators)} indicators across {len(market_summary)} markets")
    print(f"Wrote {OUT_PATH}")
    return output


if __name__ == "__main__":
    run()
