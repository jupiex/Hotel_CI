"""Agent 8 - Property Operations Dashboard.
Answers: What specific problems does each hotel need to solve this week?
Primary user: General Manager — daily.

Three KITs:
  KIT_1 — Daily KPIs vs budget (RevPAR, occupancy)
  KIT_2 — Staffing gaps (under/overstaffing by department)
  KIT_3 — Open maintenance issues (severity + hours open + guest-facing)
"""
import json
import os
from datetime import datetime, timezone

import pandas as pd

AGENT_NAME = "operations"
ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", AGENT_NAME)
OUT_PATH = os.path.join(ROOT, "outputs", f"alerts_{AGENT_NAME}.json")

# RevPAR vs budget thresholds
REVPAR_THRESHOLDS = {"yellow": 90, "red": 80}   # % of budget
# Staffing gap thresholds (negative = understaffed)
STAFF_THRESHOLDS = {"yellow": -15, "red": -25}  # % gap
# Maintenance: hours open before alert (guest-facing)
MAINT_HOURS = {"yellow": 24, "red": 48}
# Maintenance: hours open (non-guest-facing high severity)
MAINT_HOURS_INTERNAL = {"yellow": 36, "red": 72}


def safe_read(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        return pd.read_csv(path), None
    except FileNotFoundError:
        return None, f"File not found: {filename}"
    except Exception as e:
        return None, f"Error reading {filename}: {e}"


def conf(n):
    return "HIGH" if n >= 5 else "MEDIUM" if n >= 3 else "LOW"


def kit1_daily_kpis():
    indicators = []
    df, err = safe_read("daily_kpis.csv")
    if err:
        return [{"kit": "KIT_1", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_1", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        revpar_vs_budget = float(r["revpar_vs_budget_pct"])
        occ = float(r["occupancy_pct"])
        revpar = float(r["revpar_eur"])

        if revpar_vs_budget <= REVPAR_THRESHOLDS["red"]:
            level = "RED"
            rec = (f"RevPAR at {revpar_vs_budget:.1f}% of budget. "
                   f"Revenue manager to review rate strategy today. "
                   f"Check OTA parity and unrestricted availability.")
        elif revpar_vs_budget <= REVPAR_THRESHOLDS["yellow"]:
            level = "YELLOW"
            rec = (f"RevPAR tracking below budget. "
                   f"Review group pickup and corporate account pace.")
        else:
            level = "GREEN"
            rec = "RevPAR on or above budget."

        indicators.append({
            "kit": "KIT_1",
            "name": "RevPAR vs budget",
            "property": r["property_name"],
            "property_id": r["property_id"],
            "value": f"{revpar_vs_budget:.1f}% of budget (€{revpar:.0f} RevPAR, {occ:.1f}% occ)",
            "unit": "",
            "revpar_eur": round(revpar, 1),
            "occupancy_pct": round(occ, 1),
            "revpar_vs_budget_pct": round(revpar_vs_budget, 1),
            "revpar_vs_prior_year_pct": round(float(r["revpar_vs_prior_year_pct"]), 1),
            "threshold_yellow": REVPAR_THRESHOLDS["yellow"],
            "threshold_red": REVPAR_THRESHOLDS["red"],
            "alert_level": level,
            "confidence": conf(n),
            "source": r.get("source", "Opera PMS via Synapse"),
            "source_url": "",
            "capture_date": r.get("date", ""),
            "recommendation": rec,
        })
    return indicators


def kit2_staffing():
    indicators = []
    df, err = safe_read("staffing_levels.csv")
    if err:
        return [{"kit": "KIT_2", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_2", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        gap = float(r["gap_pct"])
        dept = r["department"]
        prop = r["property_name"]
        pid = r["property_id"]

        if gap <= STAFF_THRESHOLDS["red"]:
            level = "RED"
            rec = (f"{dept} understaffed by {abs(gap):.0f}%. "
                   f"Activate agency / cross-training cover immediately. "
                   f"GM to assess service impact.")
        elif gap <= STAFF_THRESHOLDS["yellow"]:
            level = "YELLOW"
            rec = f"{dept} below target. Monitor shift coverage."
        else:
            level = "GREEN"
            rec = "Staffing within normal range."

        indicators.append({
            "kit": "KIT_2",
            "name": "Staffing gap by department",
            "property": prop,
            "property_id": pid,
            "value": f"{dept}: {gap:+.1f}%",
            "unit": "",
            "department": dept,
            "gap_pct": round(gap, 1),
            "required": int(r["required_headcount"]),
            "actual": int(r["actual_headcount"]),
            "alert_level": level,
            "confidence": conf(n),
            "source": "HR system",
            "source_url": "",
            "capture_date": r.get("date", ""),
            "recommendation": rec,
            "notes": r.get("notes", ""),
        })
    return indicators


def kit3_maintenance():
    indicators = []
    df, err = safe_read("maintenance_flags.csv")
    if err:
        return [{"kit": "KIT_3", "alert_level": "ERROR", "error": err}]
    if df.empty:
        return [{"kit": "KIT_3", "alert_level": "NO_DATA"}]
    n = len(df)
    for _, r in df.iterrows():
        hours = float(r["hours_open"])
        severity = str(r["severity"]).lower()
        guest_facing = str(r["guest_facing"]).strip().lower() in ("true", "1", "yes")
        status = str(r["status"]).lower()

        if status == "resolved":
            level = "GREEN"
            rec = "Resolved."
        else:
            # Guest-facing: stricter SLA
            thresholds = MAINT_HOURS if guest_facing else MAINT_HOURS_INTERNAL
            if severity == "high" and hours >= thresholds["red"]:
                level = "RED"
                rec = (f"High-severity {'guest-facing ' if guest_facing else ''}issue "
                       f"open {hours:.0f}h. Escalate to Director of Engineering; "
                       f"brief impacted guests; activate contingency.")
            elif severity == "high" or hours >= thresholds["yellow"]:
                level = "YELLOW"
                rec = f"Issue open {hours:.0f}h. Confirm resolution ETA today."
            else:
                level = "GREEN"
                rec = "Within SLA."

        indicators.append({
            "kit": "KIT_3",
            "name": "Open maintenance issue",
            "property": r["property_name"],
            "property_id": r["property_id"],
            "value": f"{r['issue_type']} — {r['location']} ({hours:.0f}h open)",
            "unit": "",
            "issue_id": r["issue_id"],
            "severity": severity,
            "hours_open": round(hours, 0),
            "guest_facing": guest_facing,
            "status": status,
            "alert_level": level,
            "confidence": conf(n),
            "source": "Maintenance management system",
            "source_url": "",
            "capture_date": r.get("reported_date", ""),
            "recommendation": rec,
            "notes": r.get("notes", ""),
        })
    return indicators


def load_esg_franchise_property_alerts():
    """Read property-level indicators from Agent 12 (ESG) and Agent 13 (Franchise).
    Returns a list of synthetic indicator dicts — one per affected property_id."""
    extra = []
    out_dir = os.path.join(ROOT, "outputs")
    priority = {"RED": 3, "YELLOW": 2, "GREEN": 1, "NO_DATA": 0}

    for agent_name in ("esg", "franchise"):
        path = os.path.join(out_dir, f"alerts_{agent_name}.json")
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        for ind in data.get("indicators", []):
            lvl = ind.get("alert_level", "NO_DATA")
            if lvl not in ("RED", "YELLOW"):
                continue

            # Single-property indicator
            pid = ind.get("property_id")
            if pid:
                extra.append({
                    "kit": f"{agent_name.upper()}_ALERT",
                    "name": ind.get("name", ""),
                    "property_id": pid,
                    "property": pid,
                    "value": ind.get("value", ""),
                    "unit": ind.get("unit", ""),
                    "alert_level": lvl,
                    "confidence": ind.get("confidence", "MEDIUM"),
                    "source": agent_name,
                    "source_url": "",
                    "capture_date": ind.get("capture_date", ""),
                    "recommendation": ind.get("recommendation", ""),
                })

            # Multi-property indicator (property_ids list)
            for list_pid in ind.get("property_ids", []):
                if not list_pid:
                    continue
                extra.append({
                    "kit": f"{agent_name.upper()}_ALERT",
                    "name": ind.get("name", ""),
                    "property_id": list_pid,
                    "property": list_pid,
                    "value": ind.get("value", ""),
                    "unit": ind.get("unit", ""),
                    "alert_level": lvl,
                    "confidence": ind.get("confidence", "MEDIUM"),
                    "source": agent_name,
                    "source_url": "",
                    "capture_date": ind.get("capture_date", ""),
                    "recommendation": ind.get("recommendation", ""),
                })

    return extra


def build_property_summaries(indicators):
    """Aggregate per-property: worst alert level across all KITs including ESG + Franchise."""
    by_prop = {}
    for ind in indicators:
        pid = ind.get("property_id")
        if not pid:
            continue
        if pid not in by_prop:
            by_prop[pid] = {
                "property_id": pid,
                "property": ind.get("property", ""),
                "reds": 0, "yellows": 0,
                "kits": {}
            }
        lvl = ind.get("alert_level", "GREEN")
        kit = ind.get("kit", "")
        current_worst = by_prop[pid]["kits"].get(kit, "GREEN")
        priority = {"RED": 3, "YELLOW": 2, "GREEN": 1, "NO_DATA": 0, "ERROR": 0}
        if priority.get(lvl, 0) > priority.get(current_worst, 0):
            by_prop[pid]["kits"][kit] = lvl
        if lvl == "RED":
            by_prop[pid]["reds"] += 1
        elif lvl == "YELLOW":
            by_prop[pid]["yellows"] += 1

    summaries = []
    for pid, info in by_prop.items():
        status = ("RED" if info["reds"] > 0 else
                  "YELLOW" if info["yellows"] > 0 else "GREEN")
        summaries.append({
            "property_id": pid,
            "property": info["property"],
            "status": status,
            "red_count": info["reds"],
            "yellow_count": info["yellows"],
            "kit_summary": info["kits"],
        })
    return sorted(summaries, key=lambda x: {"RED": 0, "YELLOW": 1, "GREEN": 2}.get(x["status"], 3))


def run():
    indicators = kit1_daily_kpis() + kit2_staffing() + kit3_maintenance()
    # Augment with property-level alerts from Agent 12 (ESG) and Agent 13 (Franchise)
    esg_franchise_alerts = load_esg_franchise_property_alerts()
    all_indicators = indicators + esg_franchise_alerts
    property_summaries = build_property_summaries(all_indicators)

    levels = [i.get("alert_level") for i in all_indicators]
    overall = ("RED" if "RED" in levels else
               "YELLOW" if "YELLOW" in levels else
               "GREEN" if all(l == "GREEN" for l in levels) else "NO_DATA")

    out = {
        "agent": AGENT_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overall_status": overall,
        "properties": property_summaries,
        "indicators": all_indicators,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Agent {AGENT_NAME}: {overall} - {len(all_indicators)} indicators across "
          f"{len(property_summaries)} properties")
    return out


if __name__ == "__main__":
    run()
