"""
Agent 10 — Brand Perception Intelligence
Monitors online review score velocity, sentiment themes, press coverage sentiment,
and social media signals across the Radisson portfolio.

KITs:
  KIT_1  Review score velocity — properties with declining scores
  KIT_2  Negative sentiment themes — emerging complaint clusters
  KIT_3  Press coverage sentiment — negative article volume
  KIT_4  Social media negative signals — viral/trending issues
"""

import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "brand"
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "brand")
OUT_DIR  = os.path.join(ROOT, "outputs")
OUT_PATH = os.path.join(OUT_DIR, f"alerts_{AGENT_NAME}.json")

ABP_ASSUMPTIONS = {
    "A7": "Brand review scores maintain ≥4.0 average across portfolio — no systemic decline",
}
HEDGING_ACTIONS = [
    "Activate 48-hour guest recovery protocol for any property hitting 3.8 or below",
    "Weekly sentiment dashboard review with VP Operations and VP Marketing",
    "Pre-approved crisis communication templates for viral social media events",
]

# Thresholds
SCORE_RED    = 3.8   # below this = RED for any single property
SCORE_YELLOW = 4.0   # below this = YELLOW
VELOCITY_RED    = -0.3  # score drop ≥0.3 in 3 months = RED
VELOCITY_YELLOW = -0.15


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


# ─── KIT 1: Review score velocity ─────────────────────────────────────────────

def kit1_review_scores():
    df, err = safe_read("review_scores.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_1", "name": "Portfolio review score velocity",
            "description": "Rate of change in guest review scores (TripAdvisor + Google) across portfolio",
            "value": None, "unit": "properties", "threshold_yellow": 1, "threshold_red": 3,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "TripAdvisor / Google Reviews", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A7",
        }]

    numeric_cols = ["score_current", "score_3m_ago"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Per-property average score across platforms
    if "score_current" in df.columns and "property_id" in df.columns:
        prop_avg = df.groupby("property_id").agg(
            score_current=("score_current", "mean"),
            score_3m_ago=("score_3m_ago", "mean"),
            country=("country", "first"),
        ).reset_index()
        prop_avg["velocity"] = prop_avg["score_current"] - prop_avg["score_3m_ago"]
        n_red    = int((prop_avg["score_current"] < SCORE_RED).sum())
        n_yellow = int(((prop_avg["score_current"] >= SCORE_RED) & (prop_avg["score_current"] < SCORE_YELLOW)).sum())
        n_vel_red = int((prop_avg["velocity"] <= VELOCITY_RED).sum())
    else:
        n_red = n_yellow = n_vel_red = 0

    n_props = len(prop_avg) if "prop_avg" in dir() else 0

    if n_red >= 2 or n_vel_red >= 3:
        level = "RED"
        rec   = f"{n_red} propert(ies) below 3.8; {n_vel_red} with score drop ≥0.3 pts in 3 months — urgent guest recovery action required."
    elif n_red >= 1 or n_yellow >= 2 or n_vel_red >= 1:
        level = "YELLOW"
        rec   = f"{n_red + n_yellow} propert(ies) at or below 4.0 — GM coaching and service recovery plan needed."
    else:
        level = "GREEN"
        rec   = f"All {n_props} reviewed properties maintaining ≥4.0 scores — no systemic decline."

    indicators.append({
        "kit": "KIT_1", "name": "Portfolio review score velocity",
        "description": "Rate of change in guest review scores (TripAdvisor + Google) across portfolio",
        "value": n_red + n_yellow, "unit": "properties at/below 4.0",
        "threshold_yellow": 1, "threshold_red": 2,
        "alert_level": level,
        "confidence": get_confidence(n_props, "official"),
        "source": "TripAdvisor / Google Reviews", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A7",
        "detail": {"properties_reviewed": n_props, "below_3_8": n_red, "3_8_to_4_0": n_yellow, "score_drop_3m": n_vel_red},
    })

    # Flag worst property
    if n_props > 0:
        worst = prop_avg.loc[prop_avg["score_current"].idxmin()]
        w_level = "RED" if worst["score_current"] < SCORE_RED else ("YELLOW" if worst["score_current"] < SCORE_YELLOW else "GREEN")
        indicators.append({
            "kit": "KIT_1", "name": f"Lowest score property — {worst['property_id']}",
            "description": "Property with the lowest average review score across all platforms",
            "value": round(float(worst["score_current"]), 2), "unit": "avg score (0-5)",
            "threshold_yellow": 4.0, "threshold_red": 3.8,
            "alert_level": w_level,
            "confidence": get_confidence(n_props, "official"),
            "source": "TripAdvisor / Google Reviews", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Property {worst['property_id']} ({worst['country']}) avg {worst['score_current']:.2f} — velocity {worst['velocity']:+.2f} pts vs 3 months ago.",
            "abp_assumption_affected": "A7",
            "property_id": str(worst["property_id"]), "country": str(worst["country"]),
        })

    return indicators


# ─── KIT 2: Negative sentiment themes ─────────────────────────────────────────

def kit2_sentiment_themes():
    df, err = safe_read("sentiment_themes.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_2", "name": "Negative sentiment theme clusters",
            "description": "Complaint theme clusters showing significant YoY growth in negative mentions",
            "value": None, "unit": "themes", "threshold_yellow": 2, "threshold_red": 4,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "ReviewPro / Internal Sentiment Monitor", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A7",
        }]

    if "sentiment" in df.columns and "change_pct" in df.columns:
        df["change_pct"] = pd.to_numeric(df["change_pct"], errors="coerce")
        neg = df[df["sentiment"].str.lower() == "negative"].copy()
        n_surging = int((neg["change_pct"] >= 80).sum())   # ≥80% increase = RED
        n_rising  = int(((neg["change_pct"] >= 30) & (neg["change_pct"] < 80)).sum())
    else:
        n_surging = n_rising = 0

    if n_surging >= 3:
        level = "RED"
        rec   = f"{n_surging} negative themes surging ≥80% YoY — systemic service failures require immediate COO escalation."
    elif n_surging >= 1 or n_rising >= 3:
        level = "YELLOW"
        rec   = f"{n_surging} surging + {n_rising} rising negative themes — targeted improvement programmes needed."
    else:
        level = "GREEN"
        rec   = "No significant surges in negative sentiment themes — brand perception stable."

    indicators.append({
        "kit": "KIT_2", "name": "Negative sentiment theme clusters",
        "description": "Complaint theme clusters showing significant YoY growth in negative mentions",
        "value": n_surging, "unit": "surging themes (≥80% growth)",
        "threshold_yellow": 1, "threshold_red": 3,
        "alert_level": level,
        "confidence": get_confidence(len(df), "market"),
        "source": "ReviewPro / Internal Sentiment Monitor", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A7",
        "detail": {"surging_80pct": n_surging, "rising_30_80pct": n_rising},
    })

    # Top surging theme
    if "change_pct" in df.columns and n_surging > 0:
        neg_sorted = neg.sort_values("change_pct", ascending=False)
        top = neg_sorted.iloc[0]
        indicators.append({
            "kit": "KIT_2", "name": f"Top negative theme — {top.get('theme','?')}",
            "description": "Fastest-growing negative guest complaint theme across portfolio",
            "value": float(top["change_pct"]), "unit": "% change YoY in mentions",
            "threshold_yellow": 30, "threshold_red": 80,
            "alert_level": "RED" if float(top["change_pct"]) >= 80 else "YELLOW",
            "confidence": get_confidence(len(df), "market"),
            "source": "ReviewPro / Internal Sentiment Monitor", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Theme '{top.get('theme','?')}' at {top.get('property_id','?')} ({top.get('country','?')}): \"{top.get('sample_verbatim','')}\"",
            "abp_assumption_affected": "A7",
            "property_id": str(top.get("property_id", "")), "country": str(top.get("country", "")),
        })

    return indicators


# ─── KIT 3: Press coverage sentiment ─────────────────────────────────────────

def kit3_press_coverage():
    df, err = safe_read("press_coverage.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_3", "name": "Press coverage sentiment",
            "description": "Volume and sentiment of press articles mentioning Radisson brand",
            "value": None, "unit": "articles", "threshold_yellow": 2, "threshold_red": 4,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Media Monitor / Google Alerts", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A7",
        }]

    if "sentiment" in df.columns:
        n_neg = int((df["sentiment"].str.lower() == "negative").sum())
        n_pos = int((df["sentiment"].str.lower() == "positive").sum())
        n_neu = int((df["sentiment"].str.lower() == "neutral").sum())
        n_total = len(df)
        neg_pct = round(n_neg / n_total * 100, 1) if n_total > 0 else 0
    else:
        n_neg = n_pos = n_neu = 0; neg_pct = 0

    if neg_pct >= 40:
        level = "RED"
        rec   = f"{n_neg}/{n_total} articles negative ({neg_pct}%) — press sentiment crisis; PR response team activation required."
    elif neg_pct >= 25:
        level = "YELLOW"
        rec   = f"{n_neg}/{n_total} articles negative ({neg_pct}%) — proactive media engagement recommended."
    else:
        level = "GREEN"
        rec   = f"Press coverage balanced: {n_pos} positive, {n_neu} neutral, {n_neg} negative ({neg_pct}%) — no PR action needed."

    indicators.append({
        "kit": "KIT_3", "name": "Press coverage sentiment",
        "description": "Volume and sentiment of press articles mentioning Radisson brand",
        "value": neg_pct, "unit": "% negative coverage",
        "threshold_yellow": 25, "threshold_red": 40,
        "alert_level": level,
        "confidence": get_confidence(n_total, "market"),
        "source": "Media Monitor / Google Alerts", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A7",
        "detail": {"total_articles": n_total, "positive": n_pos, "neutral": n_neu, "negative": n_neg},
    })
    return indicators


# ─── KIT 4: Social media signals ─────────────────────────────────────────────

def kit4_social_signals():
    df, err = safe_read("social_signals.csv")
    indicators = []

    if err:
        return [{
            "kit": "KIT_4", "name": "Social media negative signals",
            "description": "Negative mentions, viral content and engagement decline on social platforms",
            "value": None, "unit": "properties", "threshold_yellow": 1, "threshold_red": 2,
            "alert_level": "NO_DATA", "confidence": "LOW",
            "source": "Brandwatch / Manual social monitoring", "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Data unavailable: {err}",
            "abp_assumption_affected": "A7",
        }]

    if "metric" in df.columns and "value_current" in df.columns:
        df["value_current"] = pd.to_numeric(df["value_current"], errors="coerce")
        viral = df[
            (df["metric"] == "negative_video_views") & (df["value_current"] >= 100000)
        ]
        n_viral = len(viral)
        n_neg_surge = int(len(df[
            (df["metric"] == "brand_mentions_negative") &
            (pd.to_numeric(df.get("change_pct_yoy", df.get("change_pct_30d", 0)), errors="coerce") >= 100)
        ]))
    else:
        n_viral = n_neg_surge = 0

    if n_viral >= 1:
        level = "RED"
        rec   = f"{n_viral} viral negative social media event(s) detected — immediate crisis response required."
    elif n_neg_surge >= 2:
        level = "YELLOW"
        rec   = f"{n_neg_surge} propert(ies) with negative mention surge ≥100% — social listening and response escalation."
    else:
        level = "GREEN"
        rec   = "No viral negative events or major mention surges detected — social media stable."

    indicators.append({
        "kit": "KIT_4", "name": "Social media negative signals",
        "description": "Negative mentions, viral content and engagement decline on social platforms",
        "value": n_viral, "unit": "viral negative events",
        "threshold_yellow": 0, "threshold_red": 1,
        "alert_level": level,
        "confidence": get_confidence(len(df), "market"),
        "source": "Brandwatch / Manual social monitoring", "source_url": "",
        "capture_date": datetime.now(timezone.utc).date().isoformat(),
        "recommendation": rec,
        "abp_assumption_affected": "A7",
        "detail": {"viral_events_100k_views": n_viral, "negative_mention_surge_properties": n_neg_surge},
    })

    # Flag the worst viral event
    if n_viral > 0:
        worst_viral = viral.loc[viral["value_current"].idxmax()]
        indicators.append({
            "kit": "KIT_4", "name": f"Viral event — {worst_viral.get('property_id','?')}",
            "description": "Highest-view negative social media video/post currently active",
            "value": float(worst_viral["value_current"]), "unit": "views",
            "threshold_yellow": 10000, "threshold_red": 100000,
            "alert_level": "RED",
            "confidence": "HIGH",
            "source": str(worst_viral.get("platform", "")), "source_url": "",
            "capture_date": datetime.now(timezone.utc).date().isoformat(),
            "recommendation": f"Viral negative content at {worst_viral.get('property_id','?')} ({worst_viral.get('country','?')}) — {worst_viral['value_current']:,.0f} views on {worst_viral.get('platform','')}.",
            "abp_assumption_affected": "A7",
            "property_id": str(worst_viral.get("property_id", "")), "country": str(worst_viral.get("country", "")),
        })

    return indicators


# ─── Main run ─────────────────────────────────────────────────────────────────

def run():
    indicators = []
    indicators += kit1_review_scores()
    indicators += kit2_sentiment_themes()
    indicators += kit3_press_coverage()
    indicators += kit4_social_signals()

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

    print(f"Brand Perception: {len(indicators)} indicators — overall {overall}")
    return output


if __name__ == "__main__":
    run()
