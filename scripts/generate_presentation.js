/**
 * Radisson CI EWS — Presentation Generator
 * Generates: Radisson_CI_EWS_Presentacion.pptx
 */

const pptxgen = require("pptxgenjs");
const path = require("path");

// ─── COLOR PALETTE ──────────────────────────────────────────────────────────
const C = {
  NAVY:       "1A2B4A",
  NAVY2:      "1E3A5F",
  NAVY3:      "253A5E",
  NAVY4:      "2E4A74",
  GOLD:       "C9A84C",
  GOLD_LT:    "E8C96A",
  WHITE:      "FFFFFF",
  BG:         "F4F6F8",
  BORDER:     "DDE3EC",
  TXT_DARK:   "1A2B4A",
  TXT_GRAY:   "6B7A8D",
  TXT_ICE:    "A8BEDE",
  RED:        "E74C3C",
  YELLOW:     "F39C12",
  GREEN:      "27AE60",
  BLUE_ACC:   "1A5C8E",
  GREEN_ACC:  "1D6A5A",
  AMBER_ACC:  "C97B00",
  CRIMSON:    "8B1A1A",
};

// Fresh shadow object each call (never reuse — pptxgenjs mutates in-place)
const shadow = () => ({ type: "outer", blur: 8, offset: 3, color: "000000", opacity: 0.12, angle: 135 });

// ─── INIT ───────────────────────────────────────────────────────────────────
let pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10" × 5.625"
pres.author  = "Radisson BI";
pres.title   = "Sistema de Inteligencia Competitiva Automatizada";

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 1 — PORTADA
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.NAVY };

  // Gold left stripe
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.28, h: 5.625,
    fill: { color: C.GOLD }, line: { color: C.GOLD },
  });

  // Decorative right panel
  s.addShape(pres.shapes.RECTANGLE, {
    x: 8.0, y: 0, w: 2.0, h: 5.625,
    fill: { color: C.NAVY3 }, line: { color: C.NAVY3 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 8.4, y: 0.6, w: 1.2, h: 4.4,
    fill: { color: C.NAVY4 }, line: { color: C.NAVY4 },
  });
  // Window grid decoration
  for (let row = 0; row < 5; row++) {
    for (let col = 0; col < 2; col++) {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 8.48 + col * 0.55, y: 0.75 + row * 0.78, w: 0.42, h: 0.55,
        fill: { color: "3A5580" }, line: { color: "4A6590" },
      });
    }
  }

  // Eyebrow label
  s.addText("RADISSON HOTEL GROUP", {
    x: 0.55, y: 0.5, w: 7.2, h: 0.35,
    fontSize: 9, fontFace: "Calibri", color: C.GOLD,
    charSpacing: 5, bold: false, align: "left", margin: 0,
  });

  // Main title
  s.addText("Sistema de Inteligencia\nCompetitiva Automatizada", {
    x: 0.55, y: 1.05, w: 7.3, h: 2.3,
    fontSize: 36, fontFace: "Georgia", color: C.WHITE,
    bold: true, align: "left", valign: "top",
  });

  // Gold rule
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 3.35, w: 2.8, h: 0.05,
    fill: { color: C.GOLD }, line: { color: C.GOLD },
  });

  // Subtitle
  s.addText("Early Warning System — 13 Agentes de IA", {
    x: 0.55, y: 3.55, w: 7.3, h: 0.45,
    fontSize: 15, fontFace: "Calibri", color: C.TXT_ICE,
    bold: false, align: "left", margin: 0,
  });

  // Footer
  s.addText("Business Intelligence  ·  Radisson Hotel Group  ·  2025", {
    x: 0.55, y: 5.1, w: 7.3, h: 0.35,
    fontSize: 9.5, fontFace: "Calibri", color: "6B8BB5", align: "left", margin: 0,
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 2 — EL PROBLEMA ACTUAL
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("El problema actual", {
    x: 0.45, y: 0.28, w: 9.1, h: 0.6,
    fontSize: 28, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const cards = [
    { icon: "⏱", title: "Tiempo perdido", body: "El equipo de BI dedica horas cada semana a recopilar datos manualmente de múltiples fuentes dispersas." },
    { icon: "🔔", title: "Alertas tardías",  body: "La información llega después del impacto. No existe un mecanismo proactivo de detección temprana." },
    { icon: "🔍", title: "Señales ignoradas", body: "El volumen de datos disponibles hace imposible detectar manualmente todas las señales críticas de mercado." },
    { icon: "📋", title: "Desconexión del ABP", body: "Difícil vincular en tiempo real las señales externas con los supuestos del plan anual (ABP)." },
  ];

  const cW = 2.07, cH = 3.5, startX = 0.42, gap = 0.23;
  cards.forEach((c, i) => {
    const x = startX + i * (cW + gap);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.05, w: cW, h: cH,
      fill: { color: C.WHITE }, line: { color: C.BORDER }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.05, w: cW, h: 0.07,
      fill: { color: C.GOLD }, line: { color: C.GOLD },
    });
    s.addText(c.icon, {
      x: x + 0.05, y: 1.2, w: cW - 0.1, h: 0.7,
      fontSize: 30, align: "center", valign: "middle", margin: 0,
    });
    s.addText(c.title, {
      x: x + 0.12, y: 1.92, w: cW - 0.24, h: 0.42,
      fontSize: 12, fontFace: "Calibri", color: C.NAVY, bold: true, align: "center", margin: 0,
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.3, y: 2.35, w: cW - 0.6, h: 0.03,
      fill: { color: C.BORDER }, line: { color: C.BORDER },
    });
    s.addText(c.body, {
      x: x + 0.12, y: 2.43, w: cW - 0.24, h: 1.9,
      fontSize: 10, fontFace: "Calibri", color: C.TXT_GRAY,
      align: "left", valign: "top", wrap: true, margin: 0,
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 3 — LA SOLUCIÓN
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("La solución: Sistema de 13 Agentes de IA", {
    x: 0.45, y: 0.28, w: 9.1, h: 0.6,
    fontSize: 26, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  // Big "13" circle (right side)
  s.addShape(pres.shapes.OVAL, {
    x: 7.05, y: 0.95, w: 2.5, h: 2.5,
    fill: { color: C.NAVY }, line: { color: C.NAVY }, shadow: shadow(),
  });
  s.addText("13", {
    x: 7.05, y: 0.95, w: 2.5, h: 1.75,
    fontSize: 72, fontFace: "Georgia", color: C.GOLD, bold: true,
    align: "center", valign: "bottom", margin: 0,
  });
  s.addText("Agentes\nespecializados", {
    x: 7.05, y: 2.55, w: 2.5, h: 0.75,
    fontSize: 10, fontFace: "Calibri", color: C.WHITE, align: "center", margin: 0,
  });

  // 4 feature rows
  const feats = [
    { icon: "🤖", h: "Agentes especializados", b: "Cada agente monitoriza un área estratégica de forma autónoma e independiente, sin solapamiento entre ellos." },
    { icon: "⚡", h: "Ejecución automatizada", b: "Se ejecutan de forma programada y generan alertas en tiempo real sin intervención manual del equipo." },
    { icon: "🚦", h: "Dashboard visual con semáforos", b: "Indicadores ROJO / AMARILLO / VERDE con umbral configurable por KPI, por agente y por propiedad." },
    { icon: "🔗", h: "Vinculación directa al ABP", b: "Cada alerta se mapea a uno de los 10 supuestos del plan anual, cerrando el ciclo analítico." },
  ];

  feats.forEach((f, i) => {
    const y = 1.1 + i * 1.02;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.42, y, w: 6.3, h: 0.87,
      fill: { color: C.WHITE }, line: { color: C.BORDER }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.42, y, w: 0.06, h: 0.87,
      fill: { color: C.GOLD }, line: { color: C.GOLD },
    });
    s.addText(f.icon + "  " + f.h, {
      x: 0.62, y: y + 0.07, w: 5.9, h: 0.35,
      fontSize: 12, fontFace: "Calibri", color: C.NAVY, bold: true, align: "left", margin: 0,
    });
    s.addText(f.b, {
      x: 0.62, y: y + 0.43, w: 5.9, h: 0.38,
      fontSize: 10, fontFace: "Calibri", color: C.TXT_GRAY, align: "left", wrap: true, margin: 0,
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 4 — CÓMO FUNCIONA
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("¿Cómo funciona?", {
    x: 0.45, y: 0.28, w: 9.1, h: 0.6,
    fontSize: 28, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const steps = [
    {
      num: "1", label: "DATOS",
      color: C.NAVY2,
      items: ["STR / RevPAR", "Reviews & redes sociales", "ESG & compliance", "Franquicias & M&A", "Talento & RRHH"],
    },
    {
      num: "2", label: "AGENTES IA",
      color: C.NAVY,
      items: ["13 agentes Python", "Motor Claude AI", "Umbrales configurables", "Ejecución semanal", "Sin intervención manual"],
    },
    {
      num: "3", label: "DASHBOARD",
      color: C.GREEN_ACC,
      items: ["Semáforos por KPI", "Vista por propiedad", "ABP en riesgo", "Historial tendencias", "Exportable a PPTX"],
    },
  ];

  const bW = 2.82, bH = 4.15;
  steps.forEach((st, i) => {
    const x = 0.4 + i * (bW + 0.33);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.12, w: bW, h: bH,
      fill: { color: st.color }, line: { color: st.color }, shadow: shadow(),
    });
    // Number circle
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.15, y: 1.2, w: 0.48, h: 0.48,
      fill: { color: C.GOLD }, line: { color: C.GOLD },
    });
    s.addText(st.num, {
      x: x + 0.15, y: 1.2, w: 0.48, h: 0.48,
      fontSize: 14, fontFace: "Georgia", color: C.NAVY, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(st.label, {
      x: x + 0.7, y: 1.22, w: bW - 0.82, h: 0.44,
      fontSize: 13, fontFace: "Calibri", color: C.GOLD, bold: true,
      align: "left", valign: "middle", charSpacing: 2, margin: 0,
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.2, y: 1.73, w: bW - 0.4, h: 0.03,
      fill: { color: C.GOLD_LT }, line: { color: C.GOLD_LT },
    });
    st.items.forEach((item, j) => {
      s.addText("→  " + item, {
        x: x + 0.18, y: 1.84 + j * 0.6, w: bW - 0.32, h: 0.5,
        fontSize: 10.5, fontFace: "Calibri", color: "C8D8EE",
        align: "left", margin: 0,
      });
    });

    // Arrow between boxes
    if (i < 2) {
      const ax = x + bW + 0.04;
      s.addText("▶", {
        x: ax, y: 2.8, w: 0.3, h: 0.4,
        fontSize: 18, color: C.GOLD, align: "center", margin: 0,
      });
    }
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 5 — LOS 13 AGENTES
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("Los 13 Agentes", {
    x: 0.45, y: 0.25, w: 9.1, h: 0.55,
    fontSize: 28, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const cats = [
    { label: "CRECIMIENTO", color: "1E5799",
      agents: ["Entrada competidora", "Intel. competitiva", "Revenue & RevPAR"] },
    { label: "PORTFOLIO",   color: C.GREEN_ACC,
      agents: ["Relaciones owners", "Talento & RRHH", "Operaciones"] },
    { label: "OPORTUNIDADES", color: "7B4A00",
      agents: ["M&A y adquisiciones", "Deal Scoring"] },
    { label: "RIESGOS",     color: C.CRIMSON,
      agents: ["Regulatorio", "Marca & reputación", "Fidelización", "ESG", "Franquicias"] },
  ];

  const cW = 2.12, cH = 4.42, sx = 0.47, gap = 0.22;
  cats.forEach((cat, i) => {
    const x = sx + i * (cW + gap);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 0.98, w: cW, h: cH,
      fill: { color: cat.color }, line: { color: cat.color }, shadow: shadow(),
    });
    s.addText(cat.label, {
      x: x + 0.05, y: 1.08, w: cW - 0.1, h: 0.4,
      fontSize: 9.5, fontFace: "Calibri", color: C.GOLD, bold: true,
      align: "center", charSpacing: 1.5, margin: 0,
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.18, y: 1.5, w: cW - 0.36, h: 0.03,
      fill: { color: C.GOLD_LT }, line: { color: C.GOLD_LT },
    });
    cat.agents.forEach((agent, j) => {
      const ay = 1.62 + j * 0.68;
      s.addShape(pres.shapes.RECTANGLE, {
        x: x + 0.1, y: ay, w: cW - 0.2, h: 0.56,
        fill: { color: "FFFFFF" }, line: { color: "FFFFFF" },
      });
      s.addText(agent, {
        x: x + 0.12, y: ay + 0.01, w: cW - 0.24, h: 0.54,
        fontSize: 10, fontFace: "Calibri", color: cat.color,
        bold: true, align: "center", valign: "middle", wrap: true, margin: 0,
      });
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 6 — IMPACTO ECONÓMICO
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("Agentes de mayor impacto económico", {
    x: 0.45, y: 0.28, w: 9.1, h: 0.55,
    fontSize: 26, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const cards = [
    {
      num: "01", agent: "Agente ESG",
      tag: "Máximo ahorro potencial",
      color: "B22222",
      desc: "Detecta propiedades en riesgo de multas regulatorias (CSRD, EU Taxonomy, EPC ratings). Una sola brecha de compliance puede suponer penalizaciones de cientos de miles de euros por propiedad.",
      impact: "Penalizaciones potenciales:\nhasta €500K+ por propiedad",
    },
    {
      num: "02", agent: "Agente Franquicias",
      tag: "Prevención de impagos",
      color: C.AMBER_ACC,
      desc: "Detecta socios franquiciados en distress financiero antes de que se produzcan impagos. Previene pérdidas de fee revenue y los elevados costes legales de una rescisión contractual.",
      impact: "Rescisión contractual:\n€200K–€1M+ en costes legales",
    },
    {
      num: "03", agent: "Agente M&A",
      tag: "Ventaja competitiva",
      color: C.BLUE_ACC,
      desc: "Identifica hoteles en distress y fondos PE con salida planificada. Permite a Radisson actuar antes que IHG, Marriott o Hilton en oportunidades de adquisición de alto valor.",
      impact: "Adquisiciones a 20–40%\ndescuento sobre valor de libro",
    },
  ];

  const cW = 3.0, cH = 4.0;
  cards.forEach((c, i) => {
    const x = 0.38 + i * (cW + 0.17);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.08, w: cW, h: cH,
      fill: { color: C.WHITE }, line: { color: C.BORDER }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.08, w: cW, h: 0.07,
      fill: { color: c.color }, line: { color: c.color },
    });
    s.addText(c.num, {
      x: x + 0.15, y: 1.18, w: 0.6, h: 0.55,
      fontSize: 24, fontFace: "Georgia", color: c.color, bold: true, align: "left", margin: 0,
    });
    s.addText(c.agent, {
      x: x + 0.15, y: 1.75, w: cW - 0.3, h: 0.4,
      fontSize: 14, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
    });
    s.addText(c.tag, {
      x: x + 0.15, y: 2.15, w: cW - 0.3, h: 0.3,
      fontSize: 9.5, fontFace: "Calibri", color: c.color, bold: true, align: "left", margin: 0,
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.15, y: 2.46, w: cW - 0.3, h: 0.03,
      fill: { color: C.BORDER }, line: { color: C.BORDER },
    });
    s.addText(c.desc, {
      x: x + 0.15, y: 2.54, w: cW - 0.3, h: 1.3,
      fontSize: 10, fontFace: "Calibri", color: C.TXT_GRAY,
      align: "left", valign: "top", wrap: true, margin: 0,
    });
    // Impact box
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.1, y: 3.72, w: cW - 0.2, h: 0.62,
      fill: { color: C.BG }, line: { color: C.BORDER },
    });
    s.addText(c.impact, {
      x: x + 0.15, y: 3.74, w: cW - 0.3, h: 0.58,
      fontSize: 9.5, fontFace: "Calibri", color: c.color, bold: true,
      align: "left", valign: "middle", wrap: true, margin: 0,
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 7 — IMPACTO OPERATIVO
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("Agentes de mayor impacto operativo", {
    x: 0.45, y: 0.28, w: 9.1, h: 0.55,
    fontSize: 26, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const rows = [
    {
      icon: "📈", agent: "Agente Revenue",    color: C.BLUE_ACC,
      desc: "Detecta propiedades con RevPAR por debajo del presupuesto antes de que el trimestre cierre. Monitoriza las 32 propiedades del portfolio simultáneamente y prioriza las críticas.",
      benefit: "Intervención trimestral temprana\n→ recuperación de 5–10% RevPAR por propiedad",
    },
    {
      icon: "⭐", agent: "Agente Marca & Reputación", color: C.AMBER_ACC,
      desc: "Detecta caídas en puntuaciones de reviews (Booking, TripAdvisor, Google) y alerta ante contenido viral negativo antes de que cause daño reputacional y pérdida de conversión.",
      benefit: "+1 punto en review score\n= +3–5% conversion rate (fuente: STR)",
    },
    {
      icon: "🏨", agent: "Agente Operaciones", color: C.GREEN_ACC,
      desc: "Consolida alertas ESG, franquicias y operacionales de las 32 propiedades en un único panel centralizado. Elimina la revisión manual propiedad por propiedad.",
      benefit: "1 panel centralizado\nvs. revisión manual de 32 hoteles = 4–8h/semana",
    },
  ];

  rows.forEach((r, i) => {
    const y = 1.1 + i * 1.47;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.42, y, w: 9.16, h: 1.3,
      fill: { color: C.WHITE }, line: { color: C.BORDER }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.42, y, w: 0.07, h: 1.3,
      fill: { color: r.color }, line: { color: r.color },
    });
    s.addText(r.icon + "  " + r.agent, {
      x: 0.62, y: y + 0.1, w: 3.8, h: 0.38,
      fontSize: 14, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
    });
    s.addText(r.desc, {
      x: 0.62, y: y + 0.5, w: 5.6, h: 0.72,
      fontSize: 10, fontFace: "Calibri", color: C.TXT_GRAY,
      align: "left", valign: "top", wrap: true, margin: 0,
    });
    // Right callout
    s.addShape(pres.shapes.RECTANGLE, {
      x: 6.42, y: y + 0.15, w: 3.06, h: 1.0,
      fill: { color: C.BG }, line: { color: C.BORDER },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 6.42, y: y + 0.15, w: 0.06, h: 1.0,
      fill: { color: r.color }, line: { color: r.color },
    });
    s.addText(r.benefit, {
      x: 6.56, y: y + 0.18, w: 2.84, h: 0.94,
      fontSize: 9.5, fontFace: "Calibri", color: r.color, bold: false,
      align: "left", valign: "middle", wrap: true, margin: 0,
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 8 — CASOS DE USO
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("Casos de uso concretos", {
    x: 0.45, y: 0.25, w: 9.1, h: 0.55,
    fontSize: 26, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const cases = [
    {
      num: "01", color: C.BLUE_ACC,
      trigger: "Un competidor abre un hotel a 500m de RAD007",
      detect:  "Agente de Entrada genera alerta ROJA — supuesto A3 (no canibalización) en riesgo",
      action:  "Revenue Management ajusta pricing de forma inmediata",
    },
    {
      num: "02", color: C.CRIMSON,
      trigger: "3 propiedades en Alemania superan +30% sobre target energético",
      detect:  "Agente ESG genera alerta ROJA — supuesto A9 (compliance ESG) en riesgo",
      action:  "Se activa plan preventivo de inversión en eficiencia energética",
    },
    {
      num: "03", color: C.AMBER_ACC,
      trigger: "Franquiciado acumula 60+ días de impago en facturas pendientes",
      detect:  "Agente Franquicias detecta patrón de distress antes de escalar a disputa legal",
      action:  "Legal y Finance reciben alerta para gestión preventiva del contrato",
    },
    {
      num: "04", color: C.GREEN_ACC,
      trigger: "IHG anuncia devaluación de su programa de fidelización",
      detect:  "Agente Loyalty cuantifica el riesgo de fuga de miembros Radisson Rewards",
      action:  "Marketing lanza campaña de retención de miembros de alto valor",
    },
  ];

  const cW = 4.57, cH = 2.05;
  cases.forEach((c, i) => {
    const x = 0.3  + (i % 2) * (cW + 0.28);
    const y = 1.02 + Math.floor(i / 2) * (cH + 0.22);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: cW, h: cH,
      fill: { color: C.WHITE }, line: { color: C.BORDER }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: cW, h: 0.07,
      fill: { color: c.color }, line: { color: c.color },
    });
    s.addText("Caso " + c.num, {
      x: x + 0.14, y: y + 0.1, w: 1.0, h: 0.26,
      fontSize: 9, fontFace: "Calibri", color: c.color, bold: true, align: "left", margin: 0,
    });
    s.addText(c.trigger, {
      x: x + 0.14, y: y + 0.34, w: cW - 0.28, h: 0.42,
      fontSize: 10.5, fontFace: "Calibri", color: C.NAVY, bold: true,
      align: "left", wrap: true, margin: 0,
    });
    s.addText(c.detect, {
      x: x + 0.14, y: y + 0.82, w: cW - 0.28, h: 0.5,
      fontSize: 9.5, fontFace: "Calibri", color: C.TXT_GRAY,
      align: "left", wrap: true, margin: 0,
    });
    s.addText("→  " + c.action, {
      x: x + 0.14, y: y + 1.56, w: cW - 0.28, h: 0.38,
      fontSize: 9.5, fontFace: "Calibri", color: c.color, bold: true,
      align: "left", wrap: true, margin: 0,
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 9 — VINCULACIÓN ABP
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("Vinculación directa con los supuestos del ABP", {
    x: 0.45, y: 0.26, w: 9.1, h: 0.55,
    fontSize: 24, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const abpRows = [
    ["A1",  "Propietario firma a tarifa estándar (fee 3–4% gestión)",       "Agente Owners"],
    ["A2",  "RevPAR breakeven alcanzable en 36 meses desde apertura",        "Agente Revenue"],
    ["A3",  "Sin otra marca Radisson en el mismo submercado",                 "Agente Entrada"],
    ["A4",  "Costes de energía y laboral: variación máxima +10% anual",      "Agente Regulatorio"],
    ["A5",  "Programa de fidelización mantiene paridad competitiva",          "Agente Fidelización"],
    ["A6",  "Pipeline M&A: mínimo 2 targets accionables por trimestre",       "Agente M&A"],
    ["A7",  "Puntuación media de reviews del portfolio igual o superior a 4.0","Agente Marca"],
    ["A8",  "Radisson Rewards sin pérdida material de cuota de miembros",     "Agente Fidelización"],
    ["A9",  "Compliance ESG sin brechas regulatorias materiales",             "Agente ESG"],
    ["A10", "Menos del 5% del portfolio de franquicias en distress material", "Agente Franquicias"],
  ];

  const headerStyle  = { bold: true, color: C.WHITE,    fill: { color: C.NAVY },   fontFace: "Calibri", fontSize: 10.5 };
  const cellEvenStyle = { color: C.TXT_DARK, fill: { color: "EBF0F7" }, fontFace: "Calibri", fontSize: 10 };
  const cellOddStyle  = { color: C.TXT_DARK, fill: { color: C.WHITE   }, fontFace: "Calibri", fontSize: 10 };

  const tableData = [
    [
      { text: "Supuesto", options: { ...headerStyle, align: "center" } },
      { text: "Descripción del supuesto ABP",  options: { ...headerStyle } },
      { text: "Agente monitor",                options: { ...headerStyle, align: "center" } },
    ],
  ];

  abpRows.forEach((row, i) => {
    const cs = i % 2 === 0 ? cellEvenStyle : cellOddStyle;
    tableData.push([
      { text: row[0], options: { ...cs, align: "center", bold: true, color: C.NAVY,       fill: { color: C.GOLD_LT } } },
      { text: row[1], options: { ...cs } },
      { text: row[2], options: { ...cs, align: "center", bold: true } },
    ]);
  });

  s.addTable(tableData, {
    x: 0.42, y: 0.98, w: 9.16, h: 4.42,
    colW: [0.78, 5.9, 2.48],
    border: { pt: 0.5, color: "C8D4E4" },
    rowH: 0.4,
    fontSize: 10,
    fontFace: "Calibri",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 10 — EL DASHBOARD
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("El Dashboard — alertas en un único panel", {
    x: 0.45, y: 0.26, w: 9.1, h: 0.55,
    fontSize: 26, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const feats = [
    { icon: "🌐", h: "Sin instalación",        d: "Accesible desde cualquier navegador — no requiere software adicional ni VPN." },
    { icon: "🚦", h: "Semáforos por KPI",       d: "Cada agente muestra indicadores ROJO / AMARILLO / VERDE con umbrales configurables." },
    { icon: "🏨", h: "Vista por propiedad",     d: "Panel que muestra qué alertas afectan a cada uno de los 32 hoteles del portfolio." },
    { icon: "📋", h: "Vista ABP en riesgo",     d: "Qué supuestos del plan anual están actualmente en riesgo, con nivel de alerta." },
    { icon: "📊", h: "Historial de tendencias", d: "Evolución semanal de los indicadores — hasta 52 semanas de histórico." },
    { icon: "📤", h: "Exportable a PPTX",       d: "Genera automáticamente una presentación con el resumen ejecutivo del estado del portfolio." },
  ];

  feats.forEach((f, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.38 + col * 4.82;
    const y = 1.1  + row * 1.48;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 4.55, h: 1.28,
      fill: { color: C.WHITE }, line: { color: C.BORDER }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.06, h: 1.28,
      fill: { color: C.GOLD }, line: { color: C.GOLD },
    });
    s.addText(f.icon, {
      x: x + 0.14, y: y + 0.13, w: 0.6, h: 0.6,
      fontSize: 22, align: "center", margin: 0,
    });
    s.addText(f.h, {
      x: x + 0.85, y: y + 0.12, w: 3.55, h: 0.38,
      fontSize: 12, fontFace: "Calibri", color: C.NAVY, bold: true, align: "left", margin: 0,
    });
    s.addText(f.d, {
      x: x + 0.85, y: y + 0.52, w: 3.55, h: 0.68,
      fontSize: 10, fontFace: "Calibri", color: C.TXT_GRAY,
      align: "left", valign: "top", wrap: true, margin: 0,
    });
  });

  // Traffic light visual strip at bottom
  const tlY = 5.06, tlX = 3.6;
  [C.RED, C.YELLOW, C.GREEN].forEach((col, i) => {
    s.addShape(pres.shapes.OVAL, {
      x: tlX + i * 1.05, y: tlY, w: 0.4, h: 0.4,
      fill: { color: col }, line: { color: col },
    });
  });
  s.addText("ROJO  ·  AMARILLO  ·  VERDE", {
    x: tlX - 0.4, y: tlY + 0.42, w: 4.2, h: 0.25,
    fontSize: 8.5, fontFace: "Calibri", color: C.TXT_GRAY, align: "center", margin: 0,
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 11 — ESTADO ACTUAL Y PRÓXIMOS PASOS
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.BG };

  s.addText("Estado actual y próximos pasos", {
    x: 0.45, y: 0.28, w: 9.1, h: 0.55,
    fontSize: 26, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  // LEFT — Done
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.38, y: 1.08, w: 4.3, h: 4.28,
    fill: { color: C.WHITE }, line: { color: C.BORDER }, shadow: shadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.38, y: 1.08, w: 4.3, h: 0.07,
    fill: { color: C.GREEN }, line: { color: C.GREEN },
  });
  s.addText("Estado actual", {
    x: 0.52, y: 1.18, w: 3.9, h: 0.38,
    fontSize: 13, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const done = [
    "13 agentes funcionales y probados",
    "Dashboard operativo (web, sin instalación)",
    "32 propiedades del portfolio configuradas",
    "10 supuestos ABP monitorizados",
    "Historial de tendencias semanal activo",
    "Exportación automática a PowerPoint",
  ];
  done.forEach((item, i) => {
    const y = 1.72 + i * 0.57;
    s.addShape(pres.shapes.OVAL, {
      x: 0.52, y: y + 0.06, w: 0.26, h: 0.26,
      fill: { color: C.GREEN }, line: { color: C.GREEN },
    });
    s.addText("✓", {
      x: 0.52, y: y + 0.06, w: 0.26, h: 0.26,
      fontSize: 8, color: C.WHITE, bold: true, align: "center", valign: "middle", margin: 0,
    });
    s.addText(item, {
      x: 0.85, y, w: 3.7, h: 0.42,
      fontSize: 10.5, fontFace: "Calibri", color: C.TXT_DARK,
      align: "left", valign: "middle", margin: 0,
    });
  });

  // RIGHT — Next steps
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.08, w: 4.52, h: 4.28,
    fill: { color: C.WHITE }, line: { color: C.BORDER }, shadow: shadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.08, w: 4.52, h: 0.07,
    fill: { color: C.GOLD }, line: { color: C.GOLD },
  });
  s.addText("Próximos pasos", {
    x: 5.24, y: 1.18, w: 4.1, h: 0.38,
    fontSize: 13, fontFace: "Georgia", color: C.NAVY, bold: true, align: "left", margin: 0,
  });

  const next = [
    { title: "Fuentes de datos reales",     sub: "STR, TrustYou, Booking, portales ESG" },
    { title: "Ejecución automática semanal", sub: "Scheduler para ejecución sin intervención manual" },
    { title: "Alertas push al equipo",       sub: "Notificaciones automáticas vía email o Teams" },
    { title: "Monitor de salud del sistema", sub: "Agente auto-diagnóstico de calidad de datos" },
  ];
  next.forEach((n, i) => {
    const y = 1.75 + i * 0.87;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 5.24, y, w: 4.22, h: 0.73,
      fill: { color: C.BG }, line: { color: C.BORDER },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 5.24, y, w: 0.06, h: 0.73,
      fill: { color: C.GOLD }, line: { color: C.GOLD },
    });
    s.addText(n.title, {
      x: 5.38, y: y + 0.07, w: 3.95, h: 0.3,
      fontSize: 11, fontFace: "Calibri", color: C.NAVY, bold: true, align: "left", margin: 0,
    });
    s.addText(n.sub, {
      x: 5.38, y: y + 0.38, w: 3.95, h: 0.28,
      fontSize: 9.5, fontFace: "Calibri", color: C.TXT_GRAY, align: "left", margin: 0,
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 12 — CIERRE / RESUMEN
// ════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.NAVY };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.28, h: 5.625,
    fill: { color: C.GOLD }, line: { color: C.GOLD },
  });

  s.addText("En resumen", {
    x: 0.55, y: 0.38, w: 9, h: 0.38,
    fontSize: 11, fontFace: "Calibri", color: C.GOLD, bold: true,
    charSpacing: 4, align: "left", margin: 0,
  });

  s.addText(
    "“Este sistema convierte semanas de análisis manual\nen minutos de lectura automatizada—\npermitiendo al equipo de BI enfocarse en\ndecisiones estratégicas en lugar de en la\nrecopilación de datos.”",
    {
      x: 0.55, y: 0.92, w: 9.0, h: 2.28,
      fontSize: 18, fontFace: "Georgia", color: C.WHITE,
      italic: true, align: "left", valign: "top",
    }
  );

  // 3 callout cards
  const callouts = [
    { icon: "⚡", label: "Velocidad",  sub: "Alertas en minutos,\nno en semanas",       accent: C.GOLD },
    { icon: "🎯", label: "Precisión",  sub: "Umbrales configurables\npor KPI y propiedad", accent: "5BC8F5" },
    { icon: "🔗", label: "Alineación", sub: "Directamente vinculado\nal ABP anual",     accent: "7EE8A2" },
  ];

  callouts.forEach((c, i) => {
    const x = 0.55 + i * 3.1;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 3.4, w: 2.85, h: 1.92,
      fill: { color: C.NAVY3 }, line: { color: C.NAVY4 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 3.4, w: 2.85, h: 0.06,
      fill: { color: c.accent }, line: { color: c.accent },
    });
    s.addText(c.icon, {
      x: x + 0.1, y: 3.48, w: 2.65, h: 0.6,
      fontSize: 24, align: "center", margin: 0,
    });
    s.addText(c.label, {
      x: x + 0.1, y: 4.05, w: 2.65, h: 0.38,
      fontSize: 14, fontFace: "Georgia", color: c.accent,
      bold: true, align: "center", margin: 0,
    });
    s.addText(c.sub, {
      x: x + 0.1, y: 4.44, w: 2.65, h: 0.72,
      fontSize: 10, fontFace: "Calibri", color: C.TXT_ICE,
      align: "center", wrap: true, margin: 0,
    });
  });
}

// ─── WRITE FILE ──────────────────────────────────────────────────────────────
const outPath = path.join(
  "C:\\Users\\JALA\\OneDrive - Carlson Rezidor\\Project CI\\radisson-ci-agent",
  "Radisson_CI_EWS_Presentacion.pptx"
);

pres.writeFile({ fileName: outPath })
  .then(() => console.log("SAVED:", outPath))
  .catch(e => { console.error("ERROR:", e); process.exit(1); });
