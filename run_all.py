"""Run all 7 source agents (including Agent 8 — Operations), then the orchestrator."""
import sys
import os

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
    for mod in (agent_entry, agent_competitive, agent_revenue,
                agent_owner, agent_talent, agent_regulatory, agent_operations):
        mod.run()
    print("-" * 60)
    agent_orchestrator.run()
    print("=" * 60)
    print("Done. Open dashboard/index.html or dashboard/board.html.")
