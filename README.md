# Radisson CI — Early Warning System

8-agent Competitive Intelligence prototype for Radisson Hotel Group. Modelled on the Inditex CI agent ([live demo](https://luciagonzadavi-code.github.io/Inteligencia-empresarial-II/)).

## What it does

Reads CSV data → applies threshold logic → writes per-agent JSON alerts → orchestrator evaluates ABP assumptions and emits a board brief.

## Agents

| # | Agent | Question | User | Status |
|---|---|---|---|---|
| 1 | Market Entry | Where and when should we sign next? | Development director | ✓ |
| 2 | Competitive Surveillance | What are Marriott/Hilton/IHG/Accor doing? | Strategy team | ✓ |
| 3 | Revenue Intelligence | Are we leaving money on the table? | Revenue managers | ✓ |
| 4 | Owner & Partner | Which owners are at renewal risk? | Asset management | ✓ |
| 5 | Talent & Capability | What capabilities are rivals building? | HR / Strategy | ✓ |
| 6 | Regulatory & Macro | What policy/cost shocks are coming? | CFO / Legal | ✓ |
| 7 | Orchestrator | What does the board need to know? | Board / CEO | ✓ |
| 8 | Property Operations | What does my hotel need to fix today? | General Manager | ✓ |

## Quickstart

```bash
pip install -r requirements.txt

# Refresh CSVs from real public sources (FX, wages, energy)
python scripts/fetch_real_data.py

# Run all 8 agents and orchestrator
python run_all.py

# Serve dashboards locally
python -m http.server 8000
# Then open: http://localhost:8000/dashboard/index.html
#       or: http://localhost:8000/dashboard/board.html
```

For Claude-authored board briefs, set `ANTHROPIC_API_KEY` (see `.env.example`).

## Real vs sample data

Some sources are free and public — `scripts/fetch_real_data.py` pulls them automatically:

| Indicator | Real source | Status |
|---|---|---|
| FX vs EUR (PLN, USD, GBP, …) | ECB via [Frankfurter API](https://api.frankfurter.dev) | ✓ live |
| Minimum wages (EU) | [Eurostat earn_mw_cur](https://ec.europa.eu/eurostat) | ✓ live |
| Energy prices (EU) | [Eurostat nrg_pc_202](https://ec.europa.eu/eurostat) | ✓ live (best effort) |

These remain manual or paywalled — drop your real exports into the same CSV schema:

| Indicator | Source | How to plug in |
|---|---|---|
| Supply pipeline | STR / CoStar | Replace `data/entry/supply_pipeline.csv` |
| Forward booking pace | OAG | Replace `data/entry/demand_signals.csv` |
| Rate parity | OTA Insight / RateGain | Replace `data/revenue/rate_parity.csv` |
| Review scores | Revinate / TrustYou | Replace `data/revenue/review_scores.csv` |
| Talent moves | LinkedIn | Replace `data/competitive/`, `data/talent/` |
| Contract calendar | Reltio MDM | Replace `data/owner/contract_calendar.csv` |
| Daily KPIs | Opera PMS via Synapse | Replace `data/operations/daily_kpis.csv` |

## Architecture

```
CSV inputs → Python threshold logic → alerts_*.json → static HTML dashboard
                                                   → Claude API (Agent 7)
                                                   → board_brief.md
```

No backend, no database, no auth. Future: Azure Synapse writes CSVs to Azure Blob nightly; agents read from Blob.

## ABP assumptions tracked

| ID | Assumption |
|---|---|
| A1 | Owner signs at standard fee structure (3–4% mgmt fee) |
| A2 | RevPAR breakeven within 36 months of opening |
| A3 | No cannibalisation in same submarket |
| A4 | Energy & labour cost increases stay within 10% YoY |
| A5 | Loyalty programme retains share against rival devaluations |

Agent 7 evaluates each on every run: `HOLDING / WATCH / AT_RISK / BREACHED`.

## Hedging actions

| ID | Trigger | Owner | Action |
|---|---|---|---|
| H1 | FX depreciation >15% vs EUR | Development Director | Pause LOI; add FX floor clause |
| H2 | Pipeline >15% of existing supply | Development Director | Deprioritise market; redirect BD effort |
| H3 | 2+ simultaneous REDs in same market | Chief Development Officer | 90-day hold; escalate to Development Committee |

## License

This is an internal Radisson Hotel Group prototype. All hotel chain references are illustrative. Sample data is synthetic.
