"use strict";
const pptxgen = require("pptxgenjs");

// ─── Palette ─────────────────────────────────────────────────────────────────
const NAVY    = "003366";
const WHITE   = "FFFFFF";
const ICE     = "D6E4F0";
const MID     = "1A5276";
const GOLD    = "C9A84C";
const RED_C   = "C0392B";
const AMBER_C = "D68910";
const GREEN_C = "1E8449";
const LIGHT_BG= "F4F6F8";
const BODY    = "2C3E50";
const MUTED   = "6C7A89";

const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.10 });

// ─── Helpers ─────────────────────────────────────────────────────────────────
function addSlideTitle(slide, title, subtitle) {
  // Navy title text — no bars or lines
  slide.addText(title, {
    x: 0.45, y: 0.18, w: 9.1, h: 0.62,
    fontFace: "Calibri", fontSize: 28, bold: true,
    color: NAVY, align: "left", valign: "middle", margin: 0
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.45, y: 0.82, w: 9.1, h: 0.34,
      fontFace: "Calibri", fontSize: 13, color: MUTED,
      align: "left", valign: "top", margin: 0
    });
  }
}

function addFooter(slide) {
  slide.addText("Radisson Hotel Group  ·  Confidential  ·  2026", {
    x: 0.45, y: 5.28, w: 9.1, h: 0.28,
    fontFace: "Calibri", fontSize: 9, color: MUTED,
    align: "left", valign: "middle", margin: 0
  });
}

// ─── Presentation ────────────────────────────────────────────────────────────
let pres = new pptxgen();
pres.layout  = "LAYOUT_16x9";
pres.author  = "Radisson Hotel Group";
pres.title   = "CI Early Warning System — Business Case";
pres.subject = "Investment Summary 2026";

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 1 — TITLE
// ════════════════════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: NAVY };

  // Large title
  s.addText("CI Early Warning System", {
    x: 0.6, y: 1.4, w: 8.8, h: 1.0,
    fontFace: "Calibri", fontSize: 42, bold: true,
    color: WHITE, align: "left", valign: "middle", margin: 0
  });
  // Subtitle
  s.addText("Business Case & Investment Summary", {
    x: 0.6, y: 2.5, w: 8.8, h: 0.55,
    fontFace: "Calibri", fontSize: 20, color: ICE,
    align: "left", valign: "middle", margin: 0
  });
  // Gold rule
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 3.15, w: 1.8, h: 0.055,
    fill: { color: GOLD }, line: { color: GOLD }
  });
  // Company + confidential
  s.addText("Radisson Hotel Group  ·  Confidential  ·  2026", {
    x: 0.6, y: 5.1, w: 8.8, h: 0.38,
    fontFace: "Calibri", fontSize: 11, color: ICE,
    align: "left", valign: "middle", margin: 0
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 2 — THE PROBLEM
// ════════════════════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: WHITE };
  addSlideTitle(s, "What we're solving", null);
  addFooter(s);

  const problems = [
    {
      icon: "!",
      lead: "Blind spots",
      body: "Competitor signings, owner churn risk, and RevPAR pressure are detected weeks late — after the damage is done.",
      col: RED_C
    },
    {
      icon: "⏱",
      lead: "Manual effort",
      body: "Strategy, Revenue, and Asset Management teams spend ~2 days/week aggregating signals that could be automated.",
      col: AMBER_C
    },
    {
      icon: "⊘",
      lead: "No single view",
      body: "The board and CDO have no unified early-warning dashboard — decisions rely on gut feel and fragmented reports.",
      col: NAVY
    }
  ];

  problems.forEach((p, i) => {
    const x = 0.45 + i * 3.08;
    const y = 1.3;
    const w = 2.82;
    const h = 3.5;

    // Card
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h,
      fill: { color: LIGHT_BG },
      line: { color: "E0E6ED", width: 1 },
      shadow: makeShadow()
    });
    // Colour top bar
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h: 0.07,
      fill: { color: p.col }, line: { color: p.col }
    });
    // Icon circle
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.18, y: y + 0.2, w: 0.52, h: 0.52,
      fill: { color: p.col }, line: { color: p.col }
    });
    s.addText(p.icon, {
      x: x + 0.18, y: y + 0.18, w: 0.52, h: 0.54,
      fontFace: "Calibri", fontSize: 18, bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0
    });
    // Lead text
    s.addText(p.lead, {
      x: x + 0.14, y: y + 0.84, w: w - 0.28, h: 0.42,
      fontFace: "Calibri", fontSize: 15, bold: true,
      color: p.col, align: "left", valign: "top", margin: 0
    });
    // Body text
    s.addText(p.body, {
      x: x + 0.14, y: y + 1.3, w: w - 0.28, h: 2.0,
      fontFace: "Calibri", fontSize: 12, color: BODY,
      align: "left", valign: "top", margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 3 — THE SOLUTION
// ════════════════════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: WHITE };
  addSlideTitle(s, "8-Agent CI Early Warning System",
    "Reads data → applies thresholds → alerts the right person before the problem becomes a crisis");
  addFooter(s);

  // LEFT column — agent list background
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.45, y: 1.22, w: 4.5, h: 3.85,
    fill: { color: NAVY }, line: { color: NAVY },
    shadow: makeShadow()
  });
  s.addText("The 8 agents", {
    x: 0.6, y: 1.3, w: 4.2, h: 0.36,
    fontFace: "Calibri", fontSize: 11, bold: true, charSpacing: 3,
    color: ICE, align: "left", valign: "middle", margin: 0
  });

  const agents = [
    "1 · Market Entry — Where to sign next",
    "2 · Competitive Surveillance — What rivals are doing",
    "3 · Revenue Intelligence — RevPAR & rate parity gaps",
    "4 · Owner & Partner — Renewal & churn risk",
    "5 · Talent & Capability — Rival hiring signals",
    "6 · Regulatory & Macro — FX & cost shocks",
    "7 · Orchestrator — Board brief + ABP assumptions",
    "8 · Property Operations — Daily hotel KPIs",
  ];
  s.addText(agents.map((a, i) => ({
    text: a,
    options: { breakLine: i < agents.length - 1, bullet: false }
  })), {
    x: 0.62, y: 1.72, w: 4.2, h: 3.24,
    fontFace: "Calibri", fontSize: 11.5, color: WHITE,
    align: "left", valign: "top", margin: 0, paraSpaceAfter: 5
  });

  // RIGHT column
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.22, w: 4.35, h: 3.85,
    fill: { color: LIGHT_BG }, line: { color: "E0E6ED", width: 1 },
    shadow: makeShadow()
  });
  s.addText("How it works", {
    x: 5.35, y: 1.3, w: 4.0, h: 0.36,
    fontFace: "Calibri", fontSize: 11, bold: true, charSpacing: 3,
    color: NAVY, align: "left", valign: "middle", margin: 0
  });

  const howItems = [
    "Reads CSV exports from Synapse, Reltio, STR, OTA Insight",
    "Applies RED / YELLOW / GREEN threshold logic per KIT",
    "Emits per-agent JSON alerts every morning",
    "Agent 7 evaluates 5 load-bearing ABP assumptions:\nHOLDING → WATCH → AT RISK → BREACHED",
    "Delivers board brief (Claude AI) + GM dashboard",
  ];
  s.addText(howItems.map((t, i) => ({
    text: t,
    options: { bullet: true, breakLine: i < howItems.length - 1, paraSpaceAfter: 6 }
  })), {
    x: 5.35, y: 1.72, w: 4.06, h: 3.26,
    fontFace: "Calibri", fontSize: 11.5, color: BODY,
    align: "left", valign: "top", margin: 0
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 4 — ABP ASSUMPTIONS
// ════════════════════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: WHITE };
  addSlideTitle(s, "What gets monitored — ABP Assumptions",
    "Agent 7 evaluates these on every run and flags the board when an assumption is at risk");
  addFooter(s);

  const rows = [
    [
      { text: "ID",  options: { bold: true, color: WHITE, fill: { color: NAVY }, align: "center" } },
      { text: "Assumption", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
      { text: "Escalation trigger", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
    ],
    ["A1", "Owner signs at standard fee structure (3–4% mgmt fee)", "Owner churn or fee pressure signals"],
    ["A2", "RevPAR breakeven within 36 months of opening", "Pipeline / demand / RevPAR RED alerts"],
    ["A3", "No cannibalisation in same submarket", "Rival signing in same market"],
    ["A4", "Energy & labour costs within 10% YoY", "Wage or energy RED in Regulatory agent"],
    ["A5", "Loyalty programme retains share vs rival devaluations", "Loyalty / devaluation signals"],
  ];

  // Style alternating data rows
  const styledRows = rows.map((row, ri) => {
    if (ri === 0) return row;
    const bg = ri % 2 === 0 ? "EAF2F8" : WHITE;
    return row.map(cell => ({
      text: cell,
      options: { fill: { color: bg }, color: BODY, align: cell === rows[ri][0] ? "center" : "left" }
    }));
  });

  s.addTable(styledRows, {
    x: 0.45, y: 1.22, w: 9.1, h: 3.8,
    fontFace: "Calibri", fontSize: 12,
    border: { pt: 0.5, color: "C8D6E5" },
    colW: [0.55, 4.45, 4.1],
    rowH: 0.62
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 5 — INVESTMENT / COST
// ════════════════════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: WHITE };
  addSlideTitle(s, "Investment required",
    "Assuming Azure Synapse + Reltio already licensed");
  addFooter(s);

  // Hero callout
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.45, y: 1.18, w: 9.1, h: 0.88,
    fill: { color: NAVY }, line: { color: NAVY },
    shadow: makeShadow()
  });
  s.addText([
    { text: "Most likely cost: ", options: { bold: false } },
    { text: "£8,000 – £18,000 / year", options: { bold: true } },
    { text: "  (if data licences already held)", options: { bold: false, fontSize: 13, color: ICE } }
  ], {
    x: 0.6, y: 1.2, w: 8.9, h: 0.82,
    fontFace: "Calibri", fontSize: 20, color: WHITE,
    align: "center", valign: "middle", margin: 0
  });

  const rows = [
    [
      { text: "Item", options: { bold: true, color: WHITE, fill: { color: MID } } },
      { text: "Status", options: { bold: true, color: WHITE, fill: { color: MID }, align: "center" } },
      { text: "New spend", options: { bold: true, color: WHITE, fill: { color: MID }, align: "center" } },
      { text: "Notes", options: { bold: true, color: WHITE, fill: { color: MID } } },
    ],
    ["Azure Synapse + Blob",      "✓ Licensed",  "~£200/yr marginal",     "Minimal extra storage"],
    ["Reltio MDM (owner data)",   "✓ Licensed",  "£0",                    "Already feeds Agents 4 & 8"],
    ["STR / CoStar (pipeline)",   "Likely ✓",    "£0 – £40,000",          "Check with Strategy team"],
    ["OTA Insight / RateGain",    "Likely ✓",    "£0 – £16,000",          "Check with Revenue team"],
    ["Claude AI API (Agent 7)",   "—",           "~£400/yr",              "Less than one minibar/day"],
    ["Dev time (connect pipes)",  "—",           "£5,000 – £12,000",      "~10–15 days, one-off"],
    ["OAG / LinkedIn (optional)", "—",           "£16,000 – £55,000",     "Phase 2 if needed"],
    [
      { text: "TOTAL (data already licensed)", options: { bold: true, color: NAVY, fill: { color: "D5E8F8" } } },
      { text: "",                              options: { bold: true, fill: { color: "D5E8F8" } } },
      { text: "£5,600 – £12,600/yr",          options: { bold: true, color: NAVY, fill: { color: "D5E8F8" }, align: "center" } },
      { text: "",                              options: { bold: true, fill: { color: "D5E8F8" } } },
    ],
  ];

  const styledRows = rows.map((row, ri) => {
    if (ri === 0) return row;
    if (ri === rows.length - 1) return row; // already styled
    const bg = ri % 2 === 0 ? "EAF2F8" : WHITE;
    return [
      { text: row[0], options: { fill: { color: bg }, color: BODY } },
      { text: row[1], options: { fill: { color: bg }, color: ri <= 2 ? GREEN_C : BODY, bold: ri <= 2, align: "center" } },
      { text: row[2], options: { fill: { color: bg }, color: BODY, align: "center" } },
      { text: row[3], options: { fill: { color: bg }, color: MUTED } },
    ];
  });

  s.addTable(styledRows, {
    x: 0.45, y: 2.14, w: 9.1, h: 3.0,
    fontFace: "Calibri", fontSize: 11,
    border: { pt: 0.5, color: "C8D6E5" },
    colW: [2.55, 1.4, 1.8, 3.35],
    rowH: 0.36
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 6 — ROI / VALUE
// ════════════════════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: WHITE };
  addSlideTitle(s, "Why it pays back",
    "One avoided mistake covers years of running cost");
  addFooter(s);

  const boxes = [
    {
      title: "FASTER DECISIONS",
      color: NAVY,
      bullets: [
        "Rival signings flagged within 24h vs 2–3 weeks",
        "Board brief ready every Monday morning, automated",
        "GM dashboard highlights top 3 property issues daily",
      ]
    },
    {
      title: "PROTECTED PIPELINE",
      color: MID,
      bullets: [
        "H1: FX floor clause added before LOI signed → avoids ~€200K+ per deal",
        "H2: BD effort redirected from oversupplied markets",
        "H3: 90-day hold triggered before cannibalisation confirmed",
      ]
    },
    {
      title: "REDUCED MANUAL EFFORT",
      color: GREEN_C,
      bullets: [
        "~2 days/week per team freed from report aggregation",
        "3 teams × ~300 analyst hours/year recovered",
        "At £60/hr blended rate = ~£18,000/yr in capacity",
      ]
    }
  ];

  boxes.forEach((box, i) => {
    const x = 0.45 + i * 3.08;
    const y = 1.18;
    const w = 2.85;
    const h = 3.95;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h,
      fill: { color: LIGHT_BG },
      line: { color: "E0E6ED", width: 1 },
      shadow: makeShadow()
    });
    // Colour top bar
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h: 0.08,
      fill: { color: box.color }, line: { color: box.color }
    });
    // Title
    s.addText(box.title, {
      x: x + 0.14, y: y + 0.14, w: w - 0.28, h: 0.5,
      fontFace: "Calibri", fontSize: 12, bold: true, charSpacing: 1.5,
      color: box.color, align: "left", valign: "top", margin: 0
    });
    // Bullets
    s.addText(box.bullets.map((b, bi) => ({
      text: b,
      options: { bullet: true, breakLine: bi < box.bullets.length - 1, paraSpaceAfter: 8 }
    })), {
      x: x + 0.1, y: y + 0.72, w: w - 0.2, h: 3.1,
      fontFace: "Calibri", fontSize: 11.5, color: BODY,
      align: "left", valign: "top", margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 7 — ROADMAP
// ════════════════════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: WHITE };
  addSlideTitle(s, "From prototype to production",
    "Already built. 3 steps to go live.");
  addFooter(s);

  const phases = [
    {
      phase: "Phase 1",
      when: "Week 1–2",
      title: "Connect data pipes",
      color: GREEN_C,
      items: [
        "Wire Synapse & Reltio exports → CSV schemas",
        "Set ANTHROPIC_API_KEY for Claude board briefs",
        "Schedule daily automated run",
      ],
      cost: "Dev time only"
    },
    {
      phase: "Phase 2",
      when: "Month 1",
      title: "Validate thresholds",
      color: AMBER_C,
      items: [
        "Tune RED/YELLOW thresholds with Strategy & Revenue teams",
        "Add real STR competitive data",
        "Board & GM dashboard review + sign-off",
      ],
      cost: "Included in dev estimate"
    },
    {
      phase: "Phase 3",
      when: "Quarter 2",
      title: "Scale & automate",
      color: NAVY,
      items: [
        "Add OAG demand feed",
        "GitHub Actions nightly pipeline",
        "Enable public board dashboard URL via Azure Static Web Apps",
      ],
      cost: "Phase 2 data licences if needed"
    }
  ];

  phases.forEach((ph, i) => {
    const x = 0.45 + i * 3.08;
    const y = 1.18;
    const w = 2.88;
    const h = 3.95;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h,
      fill: { color: LIGHT_BG },
      line: { color: "E0E6ED", width: 1 },
      shadow: makeShadow()
    });
    // Colour top bar
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h: 0.08,
      fill: { color: ph.color }, line: { color: ph.color }
    });

    // Phase badge + when
    s.addText(ph.phase, {
      x: x + 0.14, y: y + 0.14, w: 1.1, h: 0.32,
      fontFace: "Calibri", fontSize: 11, bold: true,
      color: ph.color, align: "left", valign: "middle", margin: 0
    });
    s.addText(ph.when, {
      x: x + 1.3, y: y + 0.14, w: w - 1.44, h: 0.32,
      fontFace: "Calibri", fontSize: 11, color: MUTED,
      align: "right", valign: "middle", margin: 0
    });

    // Title
    s.addText(ph.title, {
      x: x + 0.14, y: y + 0.52, w: w - 0.28, h: 0.4,
      fontFace: "Calibri", fontSize: 13, bold: true,
      color: BODY, align: "left", valign: "middle", margin: 0
    });

    // Bullets
    s.addText(ph.items.map((item, bi) => ({
      text: item,
      options: { bullet: true, breakLine: bi < ph.items.length - 1, paraSpaceAfter: 7 }
    })), {
      x: x + 0.1, y: y + 1.0, w: w - 0.2, h: 2.5,
      fontFace: "Calibri", fontSize: 11, color: BODY,
      align: "left", valign: "top", margin: 0
    });

    // Cost chip
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.14, y: y + 3.54, w: w - 0.28, h: 0.3,
      fill: { color: ph.color }, line: { color: ph.color }
    });
    s.addText(ph.cost, {
      x: x + 0.14, y: y + 3.54, w: w - 0.28, h: 0.3,
      fontFace: "Calibri", fontSize: 10, bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 8 — ASK / NEXT STEPS
// ════════════════════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("What we need to proceed", {
    x: 0.55, y: 0.22, w: 8.9, h: 0.62,
    fontFace: "Calibri", fontSize: 28, bold: true,
    color: WHITE, align: "left", valign: "middle", margin: 0
  });

  const actions = [
    {
      num: "1",
      title: "APPROVE",
      when: "This week",
      color: GREEN_C,
      lines: [
        "Sign off £5,600 – £12,600/yr incremental budget",
        "Or confirm data licences already held → £0 new spend",
      ]
    },
    {
      num: "2",
      title: "CONNECT",
      when: "Weeks 1–2",
      color: GOLD,
      lines: [
        "Identify data owners: STR, OTA Insight, Opera PMS",
        "10–15 days dev time to wire pipes into prototype",
      ]
    },
    {
      num: "3",
      title: "LAUNCH",
      when: "Month 1",
      color: ICE,
      lines: [
        "Daily automated run live",
        "Board dashboard accessible to CDO + CEO",
        "GM dashboard live for pilot properties",
      ]
    }
  ];

  actions.forEach((a, i) => {
    const x = 0.45 + i * 3.08;
    const y = 1.1;
    const w = 2.88;
    const h = 3.8;

    // Card
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h,
      fill: { color: MID }, line: { color: "1F618D", width: 1 },
      shadow: makeShadow()
    });

    // Number circle
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.18, y: y + 0.18, w: 0.52, h: 0.52,
      fill: { color: a.color }, line: { color: a.color }
    });
    s.addText(a.num, {
      x: x + 0.18, y: y + 0.17, w: 0.52, h: 0.54,
      fontFace: "Calibri", fontSize: 18, bold: true,
      color: a.color === ICE ? NAVY : WHITE,
      align: "center", valign: "middle", margin: 0
    });

    s.addText(a.title, {
      x: x + 0.82, y: y + 0.22, w: 1.9, h: 0.3,
      fontFace: "Calibri", fontSize: 13, bold: true, charSpacing: 1.5,
      color: a.color, align: "left", valign: "middle", margin: 0
    });
    s.addText(a.when, {
      x: x + 0.82, y: y + 0.56, w: 1.9, h: 0.26,
      fontFace: "Calibri", fontSize: 10, color: ICE,
      align: "left", valign: "middle", margin: 0
    });

    s.addText(a.lines.map((l, li) => ({
      text: l,
      options: { bullet: true, breakLine: li < a.lines.length - 1, paraSpaceAfter: 8 }
    })), {
      x: x + 0.18, y: y + 0.98, w: w - 0.36, h: 2.7,
      fontFace: "Calibri", fontSize: 11.5, color: WHITE,
      align: "left", valign: "top", margin: 0
    });
  });

  // Bottom callout
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.45, y: 5.06, w: 9.1, h: 0.38,
    fill: { color: GOLD }, line: { color: GOLD }
  });
  s.addText("Prototype is fully built and running. This is a wiring exercise, not a build.", {
    x: 0.45, y: 5.06, w: 9.1, h: 0.38,
    fontFace: "Calibri", fontSize: 12, bold: true,
    color: NAVY, align: "center", valign: "middle", margin: 0
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 9 — ARCHITECTURE
// ════════════════════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: WHITE };
  addSlideTitle(s, "Technical architecture",
    "No new infrastructure required beyond what Radisson already operates");
  addFooter(s);

  // Architecture flow — boxes + arrows
  const flowItems = [
    { label: "Azure Synapse\nReltio MDM\nSTR / OTA Insight",  color: MID,     x: 0.35 },
    { label: "CSV exports\n(nightly)",                         color: MUTED,   x: 2.5  },
    { label: "8 Python\nAgents",                               color: NAVY,    x: 4.55 },
    { label: "JSON\nalerts",                                   color: MID,     x: 6.6  },
    { label: "Static HTML\nDashboard",                         color: GREEN_C, x: 8.5  },
  ];

  const fy = 1.5;
  const bw = 1.85;
  const bh = 1.1;

  flowItems.forEach((item, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: item.x, y: fy, w: bw, h: bh,
      fill: { color: item.color }, line: { color: item.color },
      shadow: makeShadow()
    });
    s.addText(item.label, {
      x: item.x, y: fy, w: bw, h: bh,
      fontFace: "Calibri", fontSize: 11, bold: true, color: WHITE,
      align: "center", valign: "middle", margin: 4
    });
    // Arrow (except after last)
    if (i < flowItems.length - 1) {
      const ax = item.x + bw;
      s.addShape(pres.shapes.LINE, {
        x: ax, y: fy + bh / 2, w: 0.22, h: 0,
        line: { color: MUTED, width: 1.5 }
      });
    }
  });

  // Claude branch arrow down from JSON alerts box
  const jx = 6.6;
  s.addShape(pres.shapes.LINE, {
    x: jx + bw / 2, y: fy + bh, w: 0, h: 0.42,
    line: { color: MUTED, width: 1.5 }
  });
  // Claude API box
  s.addShape(pres.shapes.RECTANGLE, {
    x: jx, y: fy + bh + 0.42, w: bw, h: 0.9,
    fill: { color: GOLD }, line: { color: GOLD },
    shadow: makeShadow()
  });
  s.addText("Claude API\n(Agent 7)", {
    x: jx, y: fy + bh + 0.42, w: bw, h: 0.9,
    fontFace: "Calibri", fontSize: 11, bold: true, color: NAVY,
    align: "center", valign: "middle", margin: 4
  });
  // Board brief box
  s.addShape(pres.shapes.LINE, {
    x: jx + bw, y: fy + bh + 0.42 + 0.45, w: 0.62, h: 0,
    line: { color: MUTED, width: 1.5 }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: jx + bw + 0.62, y: fy + bh + 0.42, w: bw, h: 0.9,
    fill: { color: ICE }, line: { color: "C8D6E5", width: 1 },
    shadow: makeShadow()
  });
  s.addText("Board Brief\n(Markdown)", {
    x: jx + bw + 0.62, y: fy + bh + 0.42, w: bw, h: 0.9,
    fontFace: "Calibri", fontSize: 11, bold: true, color: NAVY,
    align: "center", valign: "middle", margin: 4
  });

  // Bullet points
  const bullets = [
    "No backend server, no database, no auth layer required",
    "Runs as a scheduled Azure Function or GitHub Actions workflow",
    "Outputs are static files — zero infrastructure to maintain",
    "All agent logic is open, auditable Python — no black box",
    "Claude API call is one HTTP request per day — cost is negligible",
  ];
  s.addText(bullets.map((b, i) => ({
    text: b,
    options: { bullet: true, breakLine: i < bullets.length - 1, paraSpaceAfter: 3 }
  })), {
    x: 0.35, y: 3.7, w: 9.2, h: 1.45,
    fontFace: "Calibri", fontSize: 11.5, color: BODY,
    align: "left", valign: "top", margin: 0
  });
}

// ─── Write file ──────────────────────────────────────────────────────────────
const outPath = "C:\\Users\\JALA\\OneDrive - Carlson Rezidor\\Project CI\\radisson-ci-agent\\Hotel_CI_Business_Case.pptx";
pres.writeFile({ fileName: outPath })
  .then(() => console.log("✓ Saved:", outPath))
  .catch(err => { console.error("✗ Error:", err); process.exit(1); });
