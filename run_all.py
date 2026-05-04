"""Run all 7 source agents (including Agent 8 — Operations), then the orchestrator."""
import sys
import os
import traceback


def append_history_snapshot(system_status):
    import json
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "history.json")
    snapshot = {
        "timestamp":      system_status.get("generated_at", ""),
        "overall_status": system_status.get("overall_status", "NO_DATA"),
        "red_count":      system_status.get("indicator_counts", {}).get("RED", 0),
        "yellow_count":   system_status.get("indicator_counts", {}).get("YELLOW", 0),
        "green_count":    system_status.get("indicator_counts", {}).get("GREEN", 0),
        "agent_status":   system_status.get("agent_status", {}),
        "abp_at_risk":    system_status.get("abp_at_risk", []),
    }
    history = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
    history.append(snapshot)
    history = history[-52:]  # keep newest 52 entries (1 year at weekly cadence)
    json.dump(history, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "agents"))

import agent_entry
import agent_competitive
import agent_revenue
import agent_owner
import agent_talent
import agent_regulatory
import agent_operations
import agent_orchestrator

if __name__ == "__main__":
    print("=" * 60)
    print("Radisson CI — running all agents")
    print("=" * 60)
    failed = []
    for mod in (agent_entry, agent_competitive, agent_revenue,
                agent_owner, agent_talent, agent_regulatory, agent_operations):
        name = mod.__name__
        try:
            mod.run()
        except Exception:
            failed.append(name)
            print(f"  [ERROR] {name} failed — skipping. Details:")
            traceback.print_exc()
    print("-" * 60)
    try:
        system_status = agent_orchestrator.run()
        try:
            append_history_snapshot(system_status)
            print("History snapshot saved.")
        except Exception as he:
            print(f"  [WARN] History snapshot failed: {he}")
    except Exception:
        failed.append("agent_orchestrator")
        print("[ERROR] Orchestrator failed:")
        traceback.print_exc()
    # Trend tracker — runs after all agents
    try:
        sys.path.insert(0, os.path.join(HERE, "scripts"))
        import track_trends
        track_trends.run()
    except Exception as te:
        print(f"  [WARN] Trend tracker failed: {te}")

    print("=" * 60)
    if failed:
        print(f"WARNING: {len(failed)} agent(s) failed: {', '.join(failed)}")
    print("Done. Open dashboard/index.html or dashboard/board.html.")
