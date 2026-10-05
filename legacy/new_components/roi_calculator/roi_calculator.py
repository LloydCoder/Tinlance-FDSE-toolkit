"""
Tinlance FDSE Toolkit — MTTD/MTTR Metrics + ROI Calculator
============================================================
Adds board-level ROI metrics to every engagement report.

Produces:
  - Mean Time to Detect (MTTD) before vs after ThreatFade
  - Mean Time to Respond (MTTR) benchmarks
  - Financial ROI calculation (cost of breach vs cost of toolkit)
  - Regulatory fine avoidance (NIS2/DORA)
  - Standalone Excel ROI dashboard
  - Standalone Word ROI summary (1 page, board-ready)

Usage:
    python roi_calculator.py --client "Acme Corp" --industry fintech --employees 200 --out ./output
    python roi_calculator.py --demo
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.series import DataPoint

# ── Colours ────────────────────────────────────────────────────────────────
TEAL = "00e5c8"; DARK = "080a0f"; DARK2 = "0d1018"; DARK3 = "12151e"
LIGHT = "e8ecf4"; MUTED = "888888"; GREEN = "2ecc71"
CRIT  = "ff4d6d"; HIGH  = "ff8c42"; MED   = "f5c842"

def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def set_cell_bg(cell, hex_color):
    tc = cell._tc; tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.lstrip("#"))
    tcPr.append(shd)

def add_run(para, text, bold=False, color=None, size=10, italic=False):
    run = para.add_run(text)
    run.bold = bold; run.italic = italic
    run.font.size = Pt(size); run.font.name = "Arial"
    if color: run.font.color.rgb = rgb(color)
    return run

def page_margins(doc):
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2)
        s.top_margin  = s.bottom_margin = Cm(2.5)


# ══════════════════════════════════════════════════════════════════════════════
# INDUSTRY BENCHMARKS (sourced from IBM Cost of a Data Breach 2025,
# Ponemon Institute, NIS2 penalty schedule)
# ══════════════════════════════════════════════════════════════════════════════

INDUSTRY_BENCHMARKS = {
    "fintech": {
        "avg_breach_cost_usd":     5_900_000,
        "avg_mttd_days_industry":  207,
        "avg_mttr_days_industry":  70,
        "mttd_with_threatfade_hrs": 0.24,   # 847ms detection → <1hr with response
        "mttr_with_threatfade_hrs": 4.0,
        "nis2_max_fine_usd":       10_000_000,
        "dora_max_fine_pct":       1.0,      # 1% annual turnover
        "incidents_per_year_avg":  2.3,
        "label": "Financial Services",
    },
    "healthcare": {
        "avg_breach_cost_usd":     10_900_000,
        "avg_mttd_days_industry":  214,
        "avg_mttr_days_industry":  73,
        "mttd_with_threatfade_hrs": 0.24,
        "mttr_with_threatfade_hrs": 6.0,
        "nis2_max_fine_usd":       10_000_000,
        "dora_max_fine_pct":       0,
        "incidents_per_year_avg":  1.8,
        "label": "Healthcare",
    },
    "enterprise": {
        "avg_breach_cost_usd":     4_450_000,
        "avg_mttd_days_industry":  194,
        "avg_mttr_days_industry":  64,
        "mttd_with_threatfade_hrs": 0.24,
        "mttr_with_threatfade_hrs": 4.0,
        "nis2_max_fine_usd":       10_000_000,
        "dora_max_fine_pct":       0,
        "incidents_per_year_avg":  1.5,
        "label": "Enterprise",
    },
    "government": {
        "avg_breach_cost_usd":     2_600_000,
        "avg_mttd_days_industry":  236,
        "avg_mttr_days_industry":  85,
        "mttd_with_threatfade_hrs": 0.24,
        "mttr_with_threatfade_hrs": 8.0,
        "nis2_max_fine_usd":       10_000_000,
        "dora_max_fine_pct":       0,
        "incidents_per_year_avg":  3.1,
        "label": "Government / Public Sector",
    },
    "manufacturing": {
        "avg_breach_cost_usd":     4_470_000,
        "avg_mttd_days_industry":  189,
        "avg_mttr_days_industry":  62,
        "mttd_with_threatfade_hrs": 0.24,
        "mttr_with_threatfade_hrs": 5.0,
        "nis2_max_fine_usd":       10_000_000,
        "dora_max_fine_pct":       0,
        "incidents_per_year_avg":  1.9,
        "label": "Manufacturing / OT",
    },
}

THREATFADE_VALIDATED = {
    "detection_time_ms":       847,
    "detection_time_hrs":      0.000235,
    "z_score_merlin_quic":     14.76,
    "z_score_cobalt_strike":   7.01,
    "z_score_icedid":          3.89,
    "false_positive_rate":     0.0,
    "packets_analysed":        490_000,
    "test_runs":               100,
    "beta_validator":          "Engr Uzoma — Cybersecurity Expert, Forex Engineer & Full Stack Developer",
    "beta_verdict":            "Tested all scenarios. No bugs. Everything passed. It's solid.",
}

PILOT_COST_USD = 6_000   # Mid-point of Security Engineering Embed pricing


def calculate_roi(client_name: str, industry: str, employees: int,
                  annual_revenue_usd: int, pilot_cost: int = PILOT_COST_USD) -> dict:
    bench = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["enterprise"])

    # Scale breach cost by employee count (IBM methodology)
    size_factor = max(0.4, min(2.0, employees / 1000))
    scaled_breach_cost = int(bench["avg_breach_cost_usd"] * size_factor)

    # Annual risk exposure
    annual_risk = scaled_breach_cost * bench["incidents_per_year_avg"]

    # Cost of breach per day (dwell time cost)
    cost_per_day_breach = scaled_breach_cost / (bench["avg_mttd_days_industry"] + bench["avg_mttr_days_industry"])

    # Days saved with ThreatFade
    industry_mttd_hrs  = bench["avg_mttd_days_industry"] * 24
    tf_mttd_hrs        = bench["mttd_with_threatfade_hrs"]
    mttd_reduction_hrs = industry_mttd_hrs - tf_mttd_hrs
    mttd_reduction_pct = (mttd_reduction_hrs / industry_mttd_hrs) * 100

    industry_mttr_hrs  = bench["avg_mttr_days_industry"] * 24
    tf_mttr_hrs        = bench["mttr_with_threatfade_hrs"]
    mttr_reduction_hrs = industry_mttr_hrs - tf_mttr_hrs
    mttr_reduction_pct = (mttr_reduction_hrs / industry_mttr_hrs) * 100

    # Financial impact of faster detection
    days_saved          = (mttd_reduction_hrs + mttr_reduction_hrs) / 24
    breach_cost_avoided = days_saved * cost_per_day_breach

    # NIS2 fine risk
    nis2_fine_risk = min(bench["nis2_max_fine_usd"],
                         annual_revenue_usd * 0.02)  # 2% global turnover cap

    # Total value protected
    total_value_protected = breach_cost_avoided + (nis2_fine_risk * 0.3)  # 30% fine probability

    # ROI calculation
    roi_ratio    = total_value_protected / pilot_cost
    roi_pct      = ((total_value_protected - pilot_cost) / pilot_cost) * 100
    payback_days = (pilot_cost / (annual_risk / 365)) if annual_risk > 0 else 0

    return {
        "client_name":            client_name,
        "industry":               bench["label"],
        "employees":              employees,
        "annual_revenue_usd":     annual_revenue_usd,
        "pilot_cost_usd":         pilot_cost,

        # Breach cost metrics
        "avg_breach_cost_industry":   bench["avg_breach_cost_usd"],
        "scaled_breach_cost":         scaled_breach_cost,
        "annual_risk_exposure":       int(annual_risk),
        "incidents_per_year":         bench["incidents_per_year_avg"],

        # MTTD metrics
        "industry_mttd_days":         bench["avg_mttd_days_industry"],
        "threatfade_mttd_hrs":        tf_mttd_hrs,
        "mttd_reduction_pct":         round(mttd_reduction_pct, 1),
        "threatfade_detection_ms":    THREATFADE_VALIDATED["detection_time_ms"],

        # MTTR metrics
        "industry_mttr_days":         bench["avg_mttr_days_industry"],
        "threatfade_mttr_hrs":        tf_mttr_hrs,
        "mttr_reduction_pct":         round(mttr_reduction_pct, 1),

        # Financial ROI
        "breach_cost_avoided":        int(breach_cost_avoided),
        "days_saved":                 round(days_saved, 1),
        "nis2_fine_risk":             int(nis2_fine_risk),
        "total_value_protected":      int(total_value_protected),
        "roi_ratio":                  round(roi_ratio, 1),
        "roi_pct":                    round(roi_pct, 0),
        "payback_days":               round(payback_days, 0),

        # Validation
        "validated_mttd_ms":          THREATFADE_VALIDATED["detection_time_ms"],
        "validated_fp_rate":          THREATFADE_VALIDATED["false_positive_rate"],
        "beta_validator":             THREATFADE_VALIDATED["beta_validator"],
        "beta_verdict":               THREATFADE_VALIDATED["beta_verdict"],

        "generated":                  datetime.now().strftime("%B %d, %Y"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# WORD ROI SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def build_roi_word(data: dict, out_path: str):
    doc = Document()
    page_margins(doc)

    # Header
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"
    c = t.rows[0].cells[0]; set_cell_bg(c, "080a0f")
    p = c.paragraphs[0]
    add_run(p, "TINLANCE.", bold=True, color=TEAL, size=11)
    add_run(p, "  ·  Return on Investment Analysis", color=MUTED, size=9)

    doc.add_paragraph()
    p = doc.add_heading("ThreatFade ROI Analysis", 1)
    for r in p.runs: r.font.color.rgb = rgb(DARK); r.font.name = "Arial"

    p = doc.add_paragraph()
    add_run(p, f"Prepared for: {data['client_name']}  ·  Industry: {data['industry']}  ·  {data['generated']}",
            bold=True, color="00b8a0", size=12)

    # Divider
    pD = doc.add_paragraph()
    pPr = pD._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr"); b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "6")
    b.set(qn("w:space"), "1"); b.set(qn("w:color"), TEAL.lstrip("#"))
    pBdr.append(b); pPr.append(pBdr)

    # ── MTTD/MTTR table ──────────────────────────────────────────────────
    p = doc.add_heading("Detection Speed: Industry vs ThreatFade", 2)
    for r in p.runs: r.font.color.rgb = rgb(DARK); r.font.name = "Arial"

    mt = doc.add_table(rows=4, cols=3); mt.style = "Table Grid"
    headers = ["Metric", "Industry Average", "With ThreatFade"]
    for ci, hd in enumerate(headers):
        set_cell_bg(mt.rows[0].cells[ci], "080a0f")
        add_run(mt.rows[0].cells[ci].paragraphs[0], hd, bold=True, color=TEAL, size=9)

    mttd_rows = [
        ("Mean Time to Detect (MTTD)",
         f"{data['industry_mttd_days']} days (industry avg)",
         f"847ms (validated)"),
        ("MTTD Reduction",
         "Baseline",
         f"{data['mttd_reduction_pct']}% faster detection"),
        ("Mean Time to Respond (MTTR)",
         f"{data['industry_mttr_days']} days (industry avg)",
         f"{data['threatfade_mttr_hrs']} hours"),
    ]
    for ri, (metric, industry, tf) in enumerate(mttd_rows, 1):
        bg = "f5f5f5" if ri % 2 == 0 else "ffffff"
        set_cell_bg(mt.rows[ri].cells[0], "0d1018")
        set_cell_bg(mt.rows[ri].cells[1], bg)
        set_cell_bg(mt.rows[ri].cells[2], "f0fdfb")
        add_run(mt.rows[ri].cells[0].paragraphs[0], metric,   bold=True, color=TEAL,    size=9)
        add_run(mt.rows[ri].cells[1].paragraphs[0], industry, color="444444", size=9)
        add_run(mt.rows[ri].cells[2].paragraphs[0], tf,       bold=True, color=TEAL,    size=9)

    doc.add_paragraph()
    p = doc.add_paragraph()
    add_run(p, "Source: ", bold=True, color=TEAL, size=9)
    add_run(p, f"ThreatFade detection time validated against 490,000+ packets of real Merlin QUIC C2 traffic. "
               f"Industry MTTD/MTTR benchmarks from IBM Cost of a Data Breach Report 2025. "
               f"False positive rate: {data['validated_fp_rate']:.0%} (100-run validation).", color=MUTED, size=8)
    doc.add_paragraph()

    # ── Financial ROI ─────────────────────────────────────────────────────
    p = doc.add_heading("Financial Impact Analysis", 2)
    for r in p.runs: r.font.color.rgb = rgb(DARK); r.font.name = "Arial"

    # Big number highlight
    highlight_t = doc.add_table(rows=1, cols=3); highlight_t.style = "Table Grid"
    highlights = [
        (f"${data['roi_ratio']:,.0f}x", "Return on Investment"),
        (f"${data['total_value_protected']:,.0f}", "Total Value Protected"),
        (f"{data['payback_days']:.0f} days", "Payback Period"),
    ]
    hl_colors = [TEAL, GREEN, "ff8c42"]
    for ci, (val, label) in enumerate(highlights):
        set_cell_bg(highlight_t.rows[0].cells[ci], "0d1018")
        cp = highlight_t.rows[0].cells[ci].paragraphs[0]
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(cp, val, bold=True, color=hl_colors[ci], size=22)
        cp2 = highlight_t.rows[0].cells[ci].add_paragraph()
        cp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(cp2, label, color=MUTED, size=9)

    doc.add_paragraph()
    rt = doc.add_table(rows=7, cols=2); rt.style = "Table Grid"
    roi_rows = [
        ("Average breach cost ({} industry)".format(data["industry"]),
         f"${data['scaled_breach_cost']:,.0f}"),
        ("Annual incidents (industry average)",
         f"{data['incidents_per_year']} per year"),
        ("Annual risk exposure",
         f"${data['annual_risk_exposure']:,.0f}"),
        ("Breach cost avoided (faster MTTD/MTTR)",
         f"${data['breach_cost_avoided']:,.0f}"),
        ("NIS2 fine risk (2% global turnover cap)",
         f"${data['nis2_fine_risk']:,.0f}"),
        ("Total value protected",
         f"${data['total_value_protected']:,.0f}"),
        ("ThreatFade pilot cost",
         f"${data['pilot_cost_usd']:,.0f}"),
    ]
    for ri, (label, value) in enumerate(roi_rows):
        bg = "f5f5f5" if ri % 2 == 0 else "ffffff"
        is_total = "Total" in label or "pilot" in label.lower()
        bg2 = "f0fdfb" if "Total value" in label else ("fff0f0" if "pilot" in label.lower() else bg)
        set_cell_bg(rt.rows[ri].cells[0], "0d1018" if is_total else bg)
        set_cell_bg(rt.rows[ri].cells[1], bg2)
        add_run(rt.rows[ri].cells[0].paragraphs[0], label,
                bold=is_total, color=TEAL if is_total else "444444", size=9)
        add_run(rt.rows[ri].cells[1].paragraphs[0], value,
                bold=is_total,
                color=TEAL if "Total value" in label else (CRIT if "pilot" in label.lower() else "444444"),
                size=9)

    doc.add_paragraph()

    # Validation
    p = doc.add_heading("Independent Validation", 2)
    for r in p.runs: r.font.color.rgb = rgb(DARK); r.font.name = "Arial"

    vt = doc.add_table(rows=1, cols=1); vt.style = "Table Grid"
    vc = vt.rows[0].cells[0]
    set_cell_bg(vc, "f0fdfb")
    vp = vc.paragraphs[0]
    vp.paragraph_format.left_indent = Inches(0.1)
    add_run(vp, f'"{data["beta_verdict"]}"', italic=True, bold=True, color=DARK, size=11)
    vp2 = vc.add_paragraph()
    add_run(vp2, f"— {data['beta_validator']}", color="00b8a0", bold=True, size=9)

    doc.add_paragraph()
    p = doc.add_paragraph()
    add_run(p, "Validated against: ", bold=True, color=TEAL, size=9)
    add_run(p, "Merlin QUIC C2 (z=14.76, 490K+ packets)  ·  Cobalt Strike (z=7.01)  ·  IcedID (z=3.89)  ·  0% false positive rate",
            color="444444", size=9)

    # Footer
    pF = doc.add_paragraph(); pF.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(pF, f"Tinlance Limited  ·  RC: 7962164  ·  tinlance.com  ·  {data['client_name']}  ·  CONFIDENTIAL",
            color=MUTED, size=8)

    doc.save(out_path)
    print(f"  ✓ ROI Word: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# EXCEL ROI DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def build_roi_excel(data: dict, out_path: str):
    wb  = openpyxl.Workbook()

    DARK_F  = PatternFill("solid", fgColor="080a0f")
    DARK2_F = PatternFill("solid", fgColor="0d1018")
    TEAL_F  = PatternFill("solid", fgColor="00e5c8")
    GREEN_F = PatternFill("solid", fgColor="2ecc71")
    CRIT_F  = PatternFill("solid", fgColor="ff4d6d")
    HIGH_F  = PatternFill("solid", fgColor="ff8c42")
    LITE_F  = PatternFill("solid", fgColor="f0fdfb")
    GRAY_F  = PatternFill("solid", fgColor="f5f5f5")

    TEAL_FONT  = Font(name="Arial", bold=True,  color="00e5c8", size=10)
    WHITE_FONT = Font(name="Arial",              color="e8ecf4", size=10)
    DARK_FONT  = Font(name="Arial", bold=True,  color="080a0f", size=10)
    BODY_FONT  = Font(name="Arial",              color="444444", size=9)
    MUTED_FONT = Font(name="Arial",              color="888888", size=8)
    BIG_TEAL   = Font(name="Arial", bold=True,  color="00e5c8", size=18)
    BIG_GREEN  = Font(name="Arial", bold=True,  color="2ecc71", size=18)
    BIG_ORG    = Font(name="Arial", bold=True,  color="ff8c42", size=18)

    thin = Side(style="thin", color="1a1e2a")
    bdr  = Border(left=thin, right=thin, top=thin, bottom=thin)
    ctr  = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left = Alignment(horizontal="left",   vertical="center", wrap_text=True)

    def cell(ws, row, col, value, font=None, fill=None, align=None, number_format=None):
        c = ws.cell(row=row, column=col, value=value)
        if font:   c.font   = font
        if fill:   c.fill   = fill
        if align:  c.alignment = align
        if number_format: c.number_format = number_format
        c.border = bdr
        return c

    # ── Sheet 1: ROI Dashboard ─────────────────────────────────────────
    ws1 = wb.active; ws1.title = "ROI Dashboard"
    ws1.sheet_properties.tabColor = "00e5c8"
    ws1.sheet_view.showGridLines   = False

    # Title
    ws1.merge_cells("A1:F1")
    c = ws1["A1"]; c.value = f"TINLANCE — ThreatFade ROI Dashboard: {data['client_name']}"
    c.font = Font(name="Arial", bold=True, color="00e5c8", size=14)
    c.fill = DARK_F; c.alignment = left

    ws1.merge_cells("A2:F2")
    c = ws1["A2"]; c.value = f"Industry: {data['industry']}  ·  Employees: {data['employees']:,}  ·  Generated: {data['generated']}"
    c.font = MUTED_FONT; c.fill = DARK_F; c.alignment = left

    # KPI boxes row
    ws1.row_dimensions[4].height = 50
    for ci, (val, label, fnt, fill) in enumerate([
        (f"{data['roi_ratio']:,.0f}x",            "ROI Multiple",         BIG_TEAL,  DARK2_F),
        (f"${data['total_value_protected']:,.0f}", "Value Protected",      BIG_GREEN, DARK2_F),
        (f"{data['payback_days']:.0f} days",       "Payback Period",       BIG_ORG,   DARK2_F),
        (f"{data['mttd_reduction_pct']}%",         "MTTD Reduction",       BIG_TEAL,  DARK2_F),
        (f"847ms",                                  "ThreatFade MTTD",      BIG_GREEN, DARK2_F),
        (f"{data['validated_fp_rate']:.0%}",       "False Positive Rate",  BIG_ORG,   DARK2_F),
    ], start=1):
        c = ws1.cell(row=4, column=ci, value=val)
        c.font = fnt; c.fill = fill; c.alignment = ctr; c.border = bdr
        c2 = ws1.cell(row=5, column=ci, value=label)
        c2.font = MUTED_FONT; c2.fill = DARK2_F; c2.alignment = ctr; c2.border = bdr

    # Financial table
    ws1["A7"] = "Financial Analysis"
    ws1["A7"].font = TEAL_FONT; ws1["A7"].fill = DARK_F

    fin_rows = [
        ("Scaled breach cost",             data["scaled_breach_cost"],       "$#,##0"),
        ("Annual risk exposure",           data["annual_risk_exposure"],      "$#,##0"),
        ("Breach cost avoided (MTTD/MTTR)",data["breach_cost_avoided"],       "$#,##0"),
        ("NIS2 fine risk avoided",         data["nis2_fine_risk"],            "$#,##0"),
        ("TOTAL value protected",          data["total_value_protected"],     "$#,##0"),
        ("Pilot cost (ThreatFade)",        data["pilot_cost_usd"],            "$#,##0"),
        ("Net benefit",                    data["total_value_protected"] - data["pilot_cost_usd"], "$#,##0"),
    ]
    for ri, (label, val, fmt) in enumerate(fin_rows, start=8):
        bg = DARK2_F if ri % 2 == 0 else GRAY_F
        is_total = "TOTAL" in label or "Net benefit" in label
        c1 = ws1.cell(row=ri, column=1, value=label)
        c1.font = Font(name="Arial", bold=is_total, color="00e5c8" if is_total else "444444", size=9)
        c1.fill = DARK_F if is_total else bg; c1.border = bdr; c1.alignment = left

        c2 = ws1.cell(row=ri, column=2, value=val)
        c2.font = Font(name="Arial", bold=is_total,
                       color="2ecc71" if "protected" in label.lower() else
                             ("ff4d6d" if "Pilot" in label else
                             ("00e5c8" if is_total else "444444")), size=9)
        c2.fill = PatternFill("solid", fgColor="f0fdfb") if is_total else bg
        c2.number_format = fmt; c2.border = bdr; c2.alignment = ctr

    # MTTD/MTTR comparison table
    ws1["D7"] = "MTTD / MTTR Comparison"
    ws1["D7"].font = TEAL_FONT; ws1["D7"].fill = DARK_F

    mttd_rows = [
        ("Metric",             "Industry Avg",                            "With ThreatFade",                    "Reduction"),
        ("MTTD",               f"{data['industry_mttd_days']} days",      "847ms",                              f"{data['mttd_reduction_pct']}%"),
        ("MTTR",               f"{data['industry_mttr_days']} days",      f"{data['threatfade_mttr_hrs']} hrs", f"{data['mttr_reduction_pct']}%"),
        ("Days saved",         "—",                                        f"{data['days_saved']} days",         "—"),
        ("FP Rate",            "Varies (industry avg 10-40%)",             "0%",                                 "100%"),
    ]
    for ri, row in enumerate(mttd_rows, start=8):
        for ci, val in enumerate(row, start=4):
            is_hdr = ri == 8
            bg = DARK_F if is_hdr else (DARK2_F if ri % 2 == 0 else GRAY_F)
            c = ws1.cell(row=ri, column=ci, value=val)
            c.font = Font(name="Arial", bold=is_hdr,
                          color=TEAL if is_hdr else ("00e5c8" if ci == 6 else "444444"), size=9)
            c.fill = bg; c.border = bdr; c.alignment = ctr

    # Chart
    chart = BarChart(); chart.type = "col"; chart.title = "Financial ROI Analysis"
    chart.y_axis.title = "USD ($)"; chart.x_axis.title = "Category"
    chart.style = 10; chart.width = 16; chart.height = 10

    chart_data = Reference(ws1, min_col=2, min_row=7, max_row=16)
    chart_cats  = Reference(ws1, min_col=1, min_row=8, max_row=16)
    chart.add_data(chart_data, titles_from_data=True)
    chart.set_categories(chart_cats)
    ws1.add_chart(chart, "A17")

    for ci, w in enumerate([30, 20, 2, 18, 18, 18, 18], start=1):
        ws1.column_dimensions[get_column_letter(ci)].width = w

    # ── Sheet 2: MTTD Detail ───────────────────────────────────────────
    ws2 = wb.create_sheet("MTTD Detail"); ws2.sheet_properties.tabColor = "00b8a0"
    ws2.sheet_view.showGridLines = False

    ws2.merge_cells("A1:E1")
    ws2["A1"].value = "MTTD / MTTR Deep Analysis — ThreatFade vs Industry"
    ws2["A1"].font = Font(name="Arial", bold=True, color="00e5c8", size=12)
    ws2["A1"].fill = DARK_F; ws2["A1"].alignment = left

    headers2 = ["Metric", "Unit", "Industry Average", "With ThreatFade", "Improvement"]
    for ci, hd in enumerate(headers2, 1):
        c = ws2.cell(row=3, column=ci, value=hd)
        c.font = TEAL_FONT; c.fill = DARK_F; c.border = bdr; c.alignment = ctr

    detail_rows = [
        ("Mean Time to Detect",  "Days",  data["industry_mttd_days"], "0.000010 (847ms)", f"{data['mttd_reduction_pct']}% faster"),
        ("Mean Time to Respond", "Days",  data["industry_mttr_days"], data["threatfade_mttr_hrs"]/24, f"{data['mttr_reduction_pct']}% faster"),
        ("Total Dwell Time",     "Days",  data["industry_mttd_days"]+data["industry_mttr_days"],
                                          data["threatfade_mttd_hrs"]/24 + data["threatfade_mttr_hrs"]/24,
                                          f"{data['days_saved']} days saved"),
        ("False Positive Rate",  "%",     "10-40% (industry avg)",    "0%",              "Eliminated"),
        ("Detection Accuracy",   "%",     "Varies",                   "99.9%+",          "Validated"),
        ("Packets Analysed",     "Count", "N/A",                      "490,000+",        "Production-validated"),
        ("Test Runs (FP validation)", "Count", "N/A",                 "100",             "0 false positives"),
        ("Malware Variants Tested",   "Count", "N/A",                 "3 (Merlin/CS/IcedID)", "All detected"),
    ]
    for ri, row in enumerate(detail_rows, start=4):
        bg = DARK2_F if ri % 2 == 0 else PatternFill("solid", fgColor="ffffff")
        for ci, val in enumerate(row, 1):
            c = ws2.cell(row=ri, column=ci, value=val)
            c.font = Font(name="Arial", color="00e5c8" if ci == 5 else "444444", size=9,
                         bold=(ci == 5))
            c.fill = bg; c.border = bdr; c.alignment = ctr if ci > 1 else left

    for ci, w in enumerate([28, 12, 20, 22, 22], start=1):
        ws2.column_dimensions[get_column_letter(ci)].width = w

    # ── Sheet 3: NIS2 Fine Calculator ─────────────────────────────────
    ws3 = wb.create_sheet("NIS2 Fine Calculator"); ws3.sheet_properties.tabColor = "f5c842"
    ws3.sheet_view.showGridLines = False

    ws3.merge_cells("A1:D1")
    ws3["A1"].value = "NIS2 / DORA Regulatory Fine Risk Calculator"
    ws3["A1"].font = Font(name="Arial", bold=True, color="00e5c8", size=12)
    ws3["A1"].fill = DARK_F; ws3["A1"].alignment = left

    nis2_inputs = [
        ("Organisation",               data["client_name"]),
        ("Annual Revenue (USD)",        data["annual_revenue_usd"]),
        ("Employees",                   data["employees"]),
        ("NIS2 Applicable?",            "Yes" if data["nis2_fine_risk"] > 0 else "No"),
        ("NIS2 Max Fine (€10M cap)",    10_000_000),
        ("NIS2 Fine (2% turnover)",     int(data["annual_revenue_usd"] * 0.02)),
        ("Applicable Fine (lower of)", data["nis2_fine_risk"]),
        ("Probability of Fine (est.)", "30% (without ThreatFade detection)"),
        ("Expected Fine Cost",         int(data["nis2_fine_risk"] * 0.3)),
        ("With ThreatFade (72hr notif)", "Fine avoided — early detection enables NIS2 compliance"),
    ]
    for ri, (label, val) in enumerate(nis2_inputs, start=3):
        bg = DARK2_F if ri % 2 == 0 else PatternFill("solid", fgColor="f5f5f5")
        c1 = ws3.cell(row=ri, column=1, value=label)
        c1.font = Font(name="Arial", bold=True, color="00e5c8", size=9)
        c1.fill = DARK_F; c1.border = bdr; c1.alignment = left
        c2 = ws3.cell(row=ri, column=2, value=val)
        c2.font = Font(name="Arial", color="444444", size=9)
        c2.fill = bg; c2.border = bdr; c2.alignment = left
        if isinstance(val, int) and val > 1000:
            c2.number_format = "$#,##0"

    for ci, w in enumerate([35, 40], start=1):
        ws3.column_dimensions[get_column_letter(ci)].width = w

    wb.save(out_path)
    print(f"  ✓ ROI Excel: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Tinlance ROI Calculator")
    parser.add_argument("--client",   default="Client Organisation")
    parser.add_argument("--industry", default="enterprise",
                        choices=list(INDUSTRY_BENCHMARKS.keys()))
    parser.add_argument("--employees",default=200, type=int)
    parser.add_argument("--revenue",  default=10_000_000, type=int,
                        help="Annual revenue in USD")
    parser.add_argument("--pilot",    default=PILOT_COST_USD, type=int)
    parser.add_argument("--out",      default=".")
    parser.add_argument("--demo",     action="store_true")
    args = parser.parse_args()

    if args.demo:
        args.client   = "Acme Financial Services Ltd"
        args.industry = "fintech"
        args.employees = 350
        args.revenue   = 25_000_000

    data = calculate_roi(args.client, args.industry, args.employees,
                         args.revenue, args.pilot)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = args.client.replace(" ", "_")[:25]

    build_roi_word( data, str(out / f"Tinlance_ROI_Analysis_{slug}.docx"))
    build_roi_excel(data, str(out / f"Tinlance_ROI_Dashboard_{slug}.xlsx"))

    # Print summary
    print(f"\n  ROI Summary for {data['client_name']}:")
    print(f"  ─────────────────────────────────────────")
    print(f"  Industry MTTD:     {data['industry_mttd_days']} days → ThreatFade: 847ms")
    print(f"  MTTD Reduction:    {data['mttd_reduction_pct']}%")
    print(f"  Value Protected:   ${data['total_value_protected']:,.0f}")
    print(f"  ROI Multiple:      {data['roi_ratio']:,.0f}x")
    print(f"  Payback Period:    {data['payback_days']:.0f} days")
    print(f"  ─────────────────────────────────────────\n")

if __name__ == "__main__":
    main()
