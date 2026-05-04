"""
Track per-market CI trends across runs.

Reads current agent outputs → appends to outputs/trend_history.json
→ computes streaks / direction → writes outputs/market_trends.json

Called automatically at the end of run_all.py.
"""
import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "outputs")

# Map EU country codes (Agent 6) to human names
MARKET_LABELS = {
    "EU-DE": "Germany", "EU-PL": "Poland", "EU-IT": "Italy",
    "EU-ES": "Spain",   "EU-FR": "France", "EU-UK": "UK",
    "EU-NL": "Netherlands", "EU-BE": "Belgium", "EU-AT": "Austria",
}

STATUS_RANK = {"RED": 3, "YELLOW": 2, "GREEN": 1, "NO_DATA": 0}


def _worst(a, b):
    return a if STATUS_RANK.get(a, 0) >= STATUS_RANK.get(b, 0) else b


def _load(filename):
    path = os.path.join(OUT, filename)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ─── Step 1: snapshot ─────────────────────────────────────────────────────────

def build_market_snapshot():
    """Return dict {market_name: worst_status} from Agents 1, 2, 6."""
    entry      = _load("alerts_entry.json")
    competitive = _load("alerts_competitive.json")
    regulatory = _load("alerts_regulatory.json")

    markets = {}  # name → worst status seen this run

    def add(raw_name, status):
        name = MARKET_LABELS.get(raw_name, raw_name).strip()
        if not name:
            return
        markets[name] = _worst(markets.get(name, "GREEN"), status)

    # Agent 1 — pre-aggregated market array
    if entry and entry.get("markets"):
        for m in entry["markets"]:
            add(m["market"], m["status"])

    # Agent 2 — KIT_1 market signings only (market-level)
    if competitive and competitive.get("indicators"):
        for ind in competitive["indicators"]:
            if ind.get("kit") == "KIT_1" and ind.get("market"):
                add(ind["market"], ind["alert_level"])

    # Agent 6 — energy (market EU-xx) + labour (country field)
    if regulatory and regulatory.get("indicators"):
        for ind in regulatory["indicators"]:
            loc = ind.get("market") or ind.get("country")
            if loc:
                add(loc, ind["alert_level"])

    return markets


# ─── Step 2: append to history ────────────────────────────────────────────────

def append_trend_history(market_snapshot):
    """Append one row to trend_history.json (capped at 52 entries)."""
    path = os.path.join(OUT, "trend_history.json")
    history = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            history = json.load(f)

    history.append({
        "run_at":  datetime.now(timezone.utc).isoformat(),
        "markets": market_snapshot,
    })
    history = history[-52:]  # 1 year at weekly cadence

    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    return history


# ─── Step 3: compute trends ───────────────────────────────────────────────────

def compute_trends(history):
    """
    For each market in history, compute:
      current_status, prev_status, streak (consecutive runs),
      direction (escalating / improving / stable),
      history list (last 10, most recent first).
    """
    if not history:
        return {}

    # Collect all market names ever seen
    all_markets = set()
    for snap in history:
        all_markets.update(snap.get("markets", {}).keys())

    trends = {}
    for market in all_markets:
        series = [
            snap["markets"].get(market, "NO_DATA")
            for snap in history
        ]                          # oldest → newest

        current = series[-1]
        prev    = series[-2] if len(series) >= 2 else current

        # Streak: consecutive identical status from the end
        streak = 0
        for s in reversed(series):
            if s == current:
                streak += 1
            else:
                break

        # Direction based on last two runs
        curr_rank = STATUS_RANK.get(current, 0)
        prev_rank = STATUS_RANK.get(prev, 0)
        if curr_rank > prev_rank:
            direction = "escalating"
        elif curr_rank < prev_rank:
            direction = "improving"
        else:
            direction = "stable"

        trends[market] = {
            "current_status": current,
            "prev_status":    prev,
            "streak":         streak,
            "direction":      direction,
            "history":        list(reversed(series[-10:])),   # most recent first
        }

    return trends


# ─── Step 4: write market_trends.json ────────────────────────────────────────

def run():
    snapshot = build_market_snapshot()
    history  = append_trend_history(snapshot)
    trends   = compute_trends(history)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_count":    len(history),
        "markets":      trends,
    }

    path = os.path.join(OUT, "market_trends.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Console summary
    n = len(trends)
    print(f"  Trend tracker: {n} market(s) tracked over {len(history)} run(s).")
    dir_icon = {"escalating": "^", "improving": "v", "stable": "-"}
    for market, t in sorted(trends.items(), key=lambda x: -STATUS_RANK.get(x[1]["current_status"], 0)):
        icon  = dir_icon.get(t["direction"], " ")
        streak_txt = f"{t['streak']} run{'s' if t['streak'] != 1 else ''}"
        print(f"    {t['current_status']:6}  {icon}  {market:<25} {streak_txt}")

    return output


if __name__ == "__main__":
    run()
