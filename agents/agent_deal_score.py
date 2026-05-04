"""
Agent — Deal Score Model
Combines Agents 1 (Entry), 2 (Competitive), 6 (Regulatory) into a single
0-100 opportunity score per market. Writes outputs/alerts_deal_score.json.

Scoring model:
  Component          Weight   Source
  ─────────────────  ──────   ────────────────────────────────────────
  Supply headroom      22%    Agent 1 KIT_1 — pipeline % of existing stock
  Demand strength      22%    Agent 1 KIT_2 — forward booking pace vs PY
  FX stability         18%    Agent 1 KIT_3 — currency depreciation vs EUR
  Competitive risk     18%    Agent 2 KIT_1 — rival signings in market
  Cost environment     12%    Agent 6 KIT_1+KIT_2 — energy & labour costs
  Regulatory risk       8%    Agent 6 KIT_3 — policy / macro risks

Score bands:
  75–100  STRONG    Proceed — conditions favourable
  50–74   WATCH     Conditional — address risks before signing LOI
  25–49   CAUTION   Significant headwinds — revisit market timing
   0–24   PAUSE     Multiple critical risks — hold; escalate to committee
"""

import json
import os
from datetime import datetime, timezone

AGENT_NAME = "deal_score"
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "outputs", f"alerts_{AGENT_NAME}.json")
OUT_DIR  = os.path.join(ROOT, "outputs")

WEIGHTS = {
    "supply":      0.22,
    "demand":      0.22,
    "fx":          0.18,
    "competitive": 0.18,
    "cost":        0.12,
    "regulatory":  0.08,
}

BANDS = [
    (75, "STRONG",  "GREEN",  "Proceed — conditions are favourable for LOI."),
    (50, "WATCH",   "YELLOW", "Conditional — address flagged risks before signing."),
    (25, "CAUTION", "RED",    "Significant headwinds — revisit market timing."),
    ( 0, "PAUSE",   "RED",    "Multiple critical risks — hold and escalate to committee."),
]

# Maps entry market country → regulatory country keys used in Agent 6
COUNTRY_REG_MAP = {
    "Poland":       {"labour": "Poland",  "energy": "EU-PL"},
    "Germany":      {"labour": "Germany", "energy": "EU-DE"},
    "Italy":        {"labour": "Italy",   "energy": "EU-IT"},
    "Spain":        {"labour": "Spain",   "energy": "EU-ES"},
    "France":       {"labour": "France",  "energy": "EU-FR"},
    "Netherlands":  {"labour": "Netherlands", "energy": "EU-NL"},
}

NEUTRAL_SCORE = 72  # Used when no regulatory data is available for a market


# ─── Loaders ──────────────────────────────────────────────────────────────────

def _load(filename):
    path = os.path.join(OUT_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _ind(indicators, market=None, country=None, kit=None):
    """Find first matching indicator by market/country/kit."""
    for i in indicators:
        if kit and i.get("kit") != kit:
            continue
        if market and i.get("market") == market:
            return i
        if country and i.get("country") == country:
            return i
    return None


# ─── Component scorers (each returns 0-100) ───────────────────────────────────

def score_supply(pipeline_pct):
    """Supply headroom. Higher pipeline % = worse."""
    if pipeline_pct is None:
        return NEUTRAL_SCORE, "No data"
    if pipeline_pct < 8:
        s, note = 92, f"Pipeline {pipeline_pct:.1f}% — very low supply pressure"
    elif pipeline_pct < 10:
        s, note = 80, f"Pipeline {pipeline_pct:.1f}% — healthy headroom"
    elif pipeline_pct < 13:
        s, note = 58, f"Pipeline {pipeline_pct:.1f}% — supply building, monitor"
    elif pipeline_pct < 15:
        s, note = 42, f"Pipeline {pipeline_pct:.1f}% — above YELLOW threshold"
    elif pipeline_pct < 20:
        s, note = 22, f"Pipeline {pipeline_pct:.1f}% — RED: oversupply risk"
    else:
        s, note = 8,  f"Pipeline {pipeline_pct:.1f}% — severe oversupply"
    return round(s), note


def score_demand(pace_pct):
    """Demand strength. Lower booking pace = worse."""
    if pace_pct is None:
        return NEUTRAL_SCORE, "No data"
    if pace_pct >= 100:
        s, note = 95, f"Booking pace {pace_pct:.0f}% — ahead of prior year"
    elif pace_pct >= 95:
        s, note = 85, f"Booking pace {pace_pct:.0f}% — strong"
    elif pace_pct >= 90:
        s, note = 68, f"Booking pace {pace_pct:.0f}% — YELLOW: softening"
    elif pace_pct >= 82:
        s, note = 45, f"Booking pace {pace_pct:.0f}% — below YELLOW threshold"
    elif pace_pct >= 75:
        s, note = 25, f"Booking pace {pace_pct:.0f}% — RED: demand weakness"
    else:
        s, note = 10, f"Booking pace {pace_pct:.0f}% — severe demand drop"
    return round(s), note


def score_fx(fx_pct):
    """FX stability. Higher depreciation = worse."""
    if fx_pct is None:
        return NEUTRAL_SCORE, "No data"
    fx_abs = abs(fx_pct)
    if fx_abs < 3:
        s, note = 95, f"FX {fx_abs:.1f}% vs EUR — very stable"
    elif fx_abs < 8:
        s, note = 82, f"FX {fx_abs:.1f}% vs EUR — within tolerance"
    elif fx_abs < 12:
        s, note = 58, f"FX {fx_abs:.1f}% vs EUR — YELLOW: re-price term sheets"
    elif fx_abs < 15:
        s, note = 40, f"FX {fx_abs:.1f}% vs EUR — approaching RED threshold"
    elif fx_abs < 20:
        s, note = 18, f"FX {fx_abs:.1f}% vs EUR — RED: H1 triggered"
    else:
        s, note = 5,  f"FX {fx_abs:.1f}% vs EUR — severe depreciation"
    return round(s), note


def score_competitive(comp_level, rival=None, prop=None):
    """Competitive pressure. RED rival signing = urgency + risk."""
    if comp_level == "RED":
        rival_str = f" ({rival}: {prop})" if rival else ""
        return 32, f"Rival signed{rival_str} — accelerate or stand down"
    elif comp_level == "YELLOW":
        rival_str = f" ({rival})" if rival else ""
        return 60, f"Rival activity{rival_str} — monitor closely"
    elif comp_level == "GREEN":
        return 82, "No rival signing detected — first-mover advantage possible"
    else:
        return NEUTRAL_SCORE, "No competitive data for this market"


def score_cost(labour_level, energy_level):
    """Operating cost environment from regulatory data."""
    rank = {"RED": 0, "YELLOW": 1, "GREEN": 2, None: 1}
    combined = rank.get(labour_level, 1) + rank.get(energy_level, 1)
    if combined == 4:
        return 90, "Both labour and energy costs stable"
    elif combined == 3:
        return 72, "Minor cost pressure on one dimension"
    elif combined == 2:
        if labour_level == "RED" or energy_level == "RED":
            return 42, f"Cost RED: labour={labour_level}, energy={energy_level}"
        return 58, "Moderate cost pressure — re-baseline P&L"
    elif combined == 1:
        return 30, f"Significant cost pressure: labour={labour_level}, energy={energy_level}"
    else:
        return 15, "Both labour and energy costs RED — severe margin impact"


def score_regulatory(policy_level, notes=None):
    """Policy / macro regulatory risk."""
    if policy_level == "RED":
        return 28, f"Active compliance risk{': ' + notes if notes else ''}"
    elif policy_level == "YELLOW":
        return 62, f"Policy watch{': ' + notes if notes else ''}"
    elif policy_level == "GREEN":
        return 88, "No active regulatory risks flagged"
    else:
        return NEUTRAL_SCORE, "No regulatory data for this market"


# ─── Market scoring ───────────────────────────────────────────────────────────

def score_market(market_name, country, entry_inds, comp_inds, reg_inds):
    """Return a full score dict for one market."""
    components = {}

    # ── 1. Supply ──────────────────────────────────────────────────────────────
    sup_ind = _ind(entry_inds, market=market_name, kit="KIT_1")
    sup_val = float(sup_ind["value"]) if sup_ind else None
    sup_s, sup_note = score_supply(sup_val)
    components["supply"] = {
        "score": sup_s, "weight": WEIGHTS["supply"],
        "weighted": round(sup_s * WEIGHTS["supply"], 1),
        "level": sup_ind["alert_level"] if sup_ind else "NO_DATA",
        "detail": sup_note,
        "label": "Supply headroom",
    }

    # ── 2. Demand ──────────────────────────────────────────────────────────────
    dem_ind = _ind(entry_inds, market=market_name, kit="KIT_2")
    dem_val = float(dem_ind["value"]) if dem_ind else None
    dem_s, dem_note = score_demand(dem_val)
    components["demand"] = {
        "score": dem_s, "weight": WEIGHTS["demand"],
        "weighted": round(dem_s * WEIGHTS["demand"], 1),
        "level": dem_ind["alert_level"] if dem_ind else "NO_DATA",
        "detail": dem_note,
        "label": "Demand strength",
    }

    # ── 3. FX ──────────────────────────────────────────────────────────────────
    fx_ind = _ind(entry_inds, market=market_name, kit="KIT_3")
    fx_val = float(fx_ind["value"]) if fx_ind else None
    fx_s, fx_note = score_fx(fx_val)
    components["fx"] = {
        "score": fx_s, "weight": WEIGHTS["fx"],
        "weighted": round(fx_s * WEIGHTS["fx"], 1),
        "level": fx_ind["alert_level"] if fx_ind else "NO_DATA",
        "detail": fx_note,
        "label": "FX stability",
    }

    # ── 4. Competitive ─────────────────────────────────────────────────────────
    comp_ind = next(
        (i for i in comp_inds
         if i.get("kit") == "KIT_1" and i.get("market") == market_name),
        None
    )
    comp_level = comp_ind["alert_level"] if comp_ind else "NO_DATA"
    rival      = comp_ind.get("rival") if comp_ind else None
    prop       = comp_ind.get("value") if comp_ind else None
    comp_s, comp_note = score_competitive(comp_level, rival, prop)
    components["competitive"] = {
        "score": comp_s, "weight": WEIGHTS["competitive"],
        "weighted": round(comp_s * WEIGHTS["competitive"], 1),
        "level": comp_level,
        "detail": comp_note,
        "label": "Competitive pressure",
    }

    # ── 5. Cost environment ────────────────────────────────────────────────────
    reg_keys     = COUNTRY_REG_MAP.get(country, {})
    labour_ind   = _ind(reg_inds, country=reg_keys.get("labour"), kit="KIT_2") if reg_keys else None
    energy_ind   = _ind(reg_inds, market=reg_keys.get("energy"),  kit="KIT_1") if reg_keys else None
    labour_level = labour_ind["alert_level"] if labour_ind else None
    energy_level = energy_ind["alert_level"] if energy_ind else None
    cost_s, cost_note = score_cost(labour_level, energy_level)
    components["cost"] = {
        "score": cost_s, "weight": WEIGHTS["cost"],
        "weighted": round(cost_s * WEIGHTS["cost"], 1),
        "level": ("RED" if "RED" in [labour_level, energy_level]
                  else "YELLOW" if "YELLOW" in [labour_level, energy_level]
                  else "GREEN" if labour_level == "GREEN" else "NO_DATA"),
        "detail": cost_note,
        "label": "Cost environment",
    }

    # ── 6. Regulatory risk ─────────────────────────────────────────────────────
    # Use worst policy indicator relevant to this market/country
    policy_inds = [
        i for i in reg_inds
        if i.get("kit") == "KIT_3"
        and (country in str(i.get("value", ""))
             or market_name in str(i.get("value", ""))
             or not (i.get("market") or i.get("country")))   # EU-wide
    ]
    if policy_inds:
        rank = {"RED": 2, "YELLOW": 1, "GREEN": 0}
        worst_pol = max(policy_inds, key=lambda x: rank.get(x["alert_level"], 0))
        pol_level = worst_pol["alert_level"]
        pol_notes = str(worst_pol.get("value", ""))[:60]
    else:
        pol_level = "NO_DATA"
        pol_notes = None
    reg_s, reg_note = score_regulatory(pol_level, pol_notes)
    components["regulatory"] = {
        "score": reg_s, "weight": WEIGHTS["regulatory"],
        "weighted": round(reg_s * WEIGHTS["regulatory"], 1),
        "level": pol_level,
        "detail": reg_note,
        "label": "Regulatory risk",
    }

    # ── Total ──────────────────────────────────────────────────────────────────
    total = round(sum(c["weighted"] for c in components.values()))
    total = max(0, min(100, total))

    # Band
    band_label, band, alert_level, band_rec = "PAUSE", "PAUSE", "RED", BANDS[-1][3]
    for threshold, bl, al, rec in BANDS:
        if total >= threshold:
            band_label, band, alert_level, band_rec = bl, bl, al, rec
            break

    # Top risk (lowest weighted component relative to max possible)
    worst_comp = min(components.items(), key=lambda x: x[1]["weighted"] / (x[1]["weight"] * 100))
    top_risk = f"{worst_comp[1]['label']}: {worst_comp[1]['detail']}"

    return {
        "market":          market_name,
        "country":         country,
        "score":           total,
        "band":            band,
        "band_label":      band_label,
        "alert_level":     alert_level,
        "recommendation":  band_rec,
        "top_risk":        top_risk,
        "components":      components,
    }


# ─── Main run ─────────────────────────────────────────────────────────────────

def run():
    entry      = _load("alerts_entry.json")
    competitive = _load("alerts_competitive.json")
    regulatory = _load("alerts_regulatory.json")

    if not entry:
        print("Deal score: alerts_entry.json missing — run agent_entry first.")
        return {}

    entry_inds = entry.get("indicators", [])
    comp_inds  = (competitive or {}).get("indicators", [])
    reg_inds   = (regulatory  or {}).get("indicators", [])

    scored = []
    for m in entry.get("markets", []):
        result = score_market(
            m["market"], m["country"],
            entry_inds, comp_inds, reg_inds
        )
        scored.append(result)

    # Sort: highest score first
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Overall status = worst band across all markets
    levels = [m["alert_level"] for m in scored]
    rank   = {"RED": 2, "YELLOW": 1, "GREEN": 0}
    overall = max(levels, key=lambda l: rank.get(l, 0)) if levels else "NO_DATA"

    output = {
        "agent":          AGENT_NAME,
        "generated_at":   datetime.now(timezone.utc).isoformat(),
        "overall_status": overall,
        "scoring_version": "1.0",
        "weights":        WEIGHTS,
        "markets":        scored,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Deal score: {len(scored)} market(s) scored.")
    for m in scored:
        bar = "#" * (m["score"] // 5) + "." * (20 - m["score"] // 5)
        print(f"  {m['score']:3d}/100  [{bar}]  {m['band']:<8}  {m['market']}")

    return output


if __name__ == "__main__":
    run()
