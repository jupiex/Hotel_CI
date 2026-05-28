"""
Agent 9 — M&A Intelligence
Monitors distressed hotel assets, fund portfolio exit signals, PE exits, and
competitor disposals that represent acquisition or management-contract opportunities.

KITs:
  KIT_1  Distressed asset pipeline — count and discount depth
  KIT_2  Fund / portfolio exit signals — mandate imminence
  KIT_3  PE fund exit readiness — vintage age and value
  KIT_4  Competitor disposals — strategic opportunity
"""

import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "ma"
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "ma")
OUT_DIR  = os.path.join(ROOT, "outputs")
OUT_PATH = os.path.join(OUT_DIR, f"alerts_{AGENT_NAME}.json")

ABP_ASSUMPTIONS = {
    "A6": "M&A pipeline provides ≥2 actionable acquisition targets per quarter",
}
HEDGING_ACTIONS = [
    "Maintain pre-approved term sheet templates for distressed acquisitions",
    "Establish standing NDA with top-3 EMEA hotel transaction advisors",
    "Brief investment committee monthly on active pipeline",
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

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


# ─── KIT 1: Distressed asset pipeline ─────────────────────────────────────────

def kit1_distressed_assets():
    df, err = safe_read("distressed_assets.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_1", "name": "Distressed asset pipeline",
            "description": "Count and discount depth of distressed hotel assets available for acquisition",
            "value": None, "unit": "assets", "threshold_yellow": 3, "threshold_red": 1,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "CoStar / CBRE Distressed Monitor", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A6",
        }]

    # Count assets by discount band
    n_total = len(df)
    n_deep_discount = int((df["discount_to_book_pct"] >= 25).sum()) if "discount_to_book_pct" in df.columns else 0
    n_moderate      = int((df["discount_to_book_pct"].between(15, 24.99)).sum()) if "discount_to_book_pct" in df.columns else 0

    if n_total >= 6 and n_deep_discount >= 3:
        level = "GREEN"
        rec   = f"{n_total} distressed assets in pipeline; {n_deep_discount} at ≥25% discount — strong acquisition opportunity."
    elif n_total >= 3:
        level = "YELLOW"
        rec   = f"{n_total} distressed assets identified; monitor for deepening distress before LOI."
    else:
        level = "RED"
        rec   = f"Only {n_total} distressed asset(s) in pipeline — insufficient acquisition optionality."

    indicators.append({
        "kit": "KIT_1", "name": "Distressed asset pipeline",
        "description": "Count and discount depth of distressed hotel assets available for acquisition",
        "value": n_total, "unit": "assets",
        "threshold_yellow": 3, "threshold_red": 1,
        "alert_level": level,
        "confidence": get_confidence(n_total, "market"),
        "source": "CoStar / CBRE Distressed Monitor", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A6",
        "detail": {"total_assets": n_total, "deep_discount_25pct_plus": n_deep_discount, "moderate_discount": n_moderate},
    })

    # Top opportunity per country
    if "discount_to_book_pct" in df.columns:
        best = df.loc[df["discount_to_book_pct"].idxmax()]
        indicators.append({
            "kit": "KIT_1", "name": "Best distressed acquisition — discount",
            "description": "Single highest-discount distressed hotel asset currently in market",
            "value": float(best["discount_to_book_pct"]), "unit": "% discount to book",
            "threshold_yellow": 20, "threshold_red": 10,
            "alert_level": "GREEN" if float(best["discount_to_book_pct"]) >= 25 else "YELLOW",
            "confidence": get_confidence(n_total, "market"),
            "source": str(best.get("source", "")), "source_url": str(best.get("source_url", "")),
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Top target: {best.get('asset_name','?')} in {best.get('city','?')}, {best.get('country','?')} — {best.get('distress_type','?')}.",
            "abp_assumption_affected": "A6",
            "market": str(best.get("city", "")), "country": str(best.get("country", "")),
        })

    return indicators


# ─── KIT 2: Fund / portfolio exit signals ─────────────────────────────────────

def kit2_portfolio_signals():
    df, err = safe_read("portfolio_signals.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_2", "name": "Fund portfolio exit signals",
            "description": "Active fund mandates and portfolio sales expected to reach market",
            "value": None, "unit": "signals", "threshold_yellow": 2, "threshold_red": 0,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Preqin / JLL Capital Markets", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A6",
        }]

    n = len(df)
    n_portfolio_sale = int((df["exit_signal"].str.contains("Portfolio sale|Secondary", case=False, na=False)).sum()) \
        if "exit_signal" in df.columns else n

    if n >= 5:
        level = "GREEN"
        rec   = f"{n} active fund exit signals detected — strong pipeline of portfolio opportunities."
    elif n >= 3:
        level = "YELLOW"
        rec   = f"{n} fund exit signals — monitor mandate timelines for Q2/Q3 2026 decisions."
    else:
        level = "RED"
        rec   = f"Only {n} fund exit signal(s) — insufficient pipeline from institutional sellers."

    indicators.append({
        "kit": "KIT_2", "name": "Fund portfolio exit signals",
        "description": "Active fund mandates and portfolio sales expected to reach market",
        "value": n, "unit": "active signals",
        "threshold_yellow": 3, "threshold_red": 1,
        "alert_level": level,
        "confidence": get_confidence(n, "market"),
        "source": "Preqin / JLL Capital Markets", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A6",
        "detail": {"portfolio_sale_signals": n_portfolio_sale},
    })
    return indicators


# ─── KIT 3: PE exit readiness ─────────────────────────────────────────────────

def kit3_pe_exits():
    df, err = safe_read("pe_exits.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_3", "name": "PE fund exit readiness",
            "description": "Private equity funds approaching end of hold period with hotel portfolios",
            "value": None, "unit": "funds", "threshold_yellow": 3, "threshold_red": 1,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Mergermarket / Dealogic", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A6",
        }]

    current_year = datetime.now().year
    if "planned_exit_year" in df.columns:
        df["planned_exit_year"] = pd.to_numeric(df["planned_exit_year"], errors="coerce")
        n_imminent = int((df["planned_exit_year"] <= current_year + 1).sum())
    else:
        n_imminent = len(df)

    total_value = float(df["implied_value_eur_m"].sum()) if "implied_value_eur_m" in df.columns else 0

    if n_imminent >= 5:
        level = "GREEN"
        rec   = f"{n_imminent} PE exits imminent (≤{current_year+1}); total implied value EUR {total_value:.0f}m — exceptional deal flow."
    elif n_imminent >= 3:
        level = "YELLOW"
        rec   = f"{n_imminent} PE exits approaching — engage advisors to position Radisson as preferred acquirer."
    else:
        level = "RED"
        rec   = f"Only {n_imminent} imminent PE exit(s) — limited deal flow from private equity sector."

    indicators.append({
        "kit": "KIT_3", "name": "PE fund exit readiness",
        "description": "Private equity funds approaching end of hold period with hotel portfolios",
        "value": n_imminent, "unit": "imminent exits",
        "threshold_yellow": 3, "threshold_red": 1,
        "alert_level": level,
        "confidence": get_confidence(len(df), "market"),
        "source": "Mergermarket / Dealogic", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A6",
        "detail": {"total_pe_exits_tracked": len(df), "imminent_exits": n_imminent, "total_implied_value_eur_m": round(total_value, 1)},
    })
    return indicators


# ─── KIT 4: Competitor disposals ──────────────────────────────────────────────

def kit4_competitor_disposals():
    df, err = safe_read("competitor_disposals.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_4", "name": "Competitor disposal signals",
            "description": "Hotels being disposed of by competitors creating management contract opportunities",
            "value": None, "unit": "disposals", "threshold_yellow": 2, "threshold_red": 0,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Hospitality Investor / RCA", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A6",
        }]

    n = len(df)
    n_franchise_term = int((df["disposal_type"].str.contains("termination|termination", case=False, na=False)).sum()) \
        if "disposal_type" in df.columns else 0
    total_rooms = int(df["rooms"].sum()) if "rooms" in df.columns else 0

    if n >= 4:
        level = "GREEN"
        rec   = f"{n} competitor disposals active; {total_rooms} total rooms — proactively approach sellers."
    elif n >= 2:
        level = "YELLOW"
        rec   = f"{n} competitor disposals — screen for management contract conversion opportunities."
    else:
        level = "RED"
        rec   = f"Only {n} competitor disposal(s) — limited conversion pipeline from rivals."

    indicators.append({
        "kit": "KIT_4", "name": "Competitor disposal signals",
        "description": "Hotels being disposed of by competitors creating management contract opportunities",
        "value": n, "unit": "active disposals",
        "threshold_yellow": 2, "threshold_red": 1,
        "alert_level": level,
        "confidence": get_confidence(n, "market"),
        "source": "Hospitality Investor / RCA", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A6",
        "detail": {"franchise_terminations": n_franchise_term, "total_rooms_available": total_rooms},
    })
    return indicators


# ─── Main run ─────────────────────────────────────────────────────────────────

def run():
    indicators = []
    indicators += kit1_distressed_assets()
    indicators += kit2_portfolio_signals()
    indicators += kit3_pe_exits()
    indicators += kit4_competitor_disposals()

    overall = compute_overall(indicators)

    output = {
        "agent":             AGENT_NAME,
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "overall_status":    overall,
        "abp_assumptions":   ABP_ASSUMPTIONS,
        "hedging_actions":   HEDGING_ACTIONS,
        "indicators":        indicators,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"M&A Intelligence: {len(indicators)} indicators — overall {overall}")
    return output


if __name__ == "__main__":
    run()
