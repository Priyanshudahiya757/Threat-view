"""PDF report generation service — professional weekly threat landscape report.

Layout
------
1. Header band  — dark navy with ThreatView branding + report date
2. Executive Summary — 4 stat boxes (total, critical, high, sources)
3. Severity Breakdown table
4. Top Countries table
5. Top Malware Families table
6. Full IOC Listing (up to 50 most-recent, colour-coded by severity)
7. Footer with generation timestamp
"""
from datetime import datetime, timedelta, timezone
from io import BytesIO

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        HRFlowable,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    
    # ── Brand colours ──────────────────────────────────────────────────────────────
    NAVY    = colors.HexColor("#0d1526")
    BLUE    = colors.HexColor("#4c6fff")
    BLUE_LT = colors.HexColor("#e8ecff")
    SILVER  = colors.HexColor("#f1f5f9")
    BORDER  = colors.HexColor("#cbd5e1")
    TEXT    = colors.HexColor("#0f172a")
    MUTED   = colors.HexColor("#64748b")
    
    SEV_COLORS = {
        "critical": colors.HexColor("#f4415c"),
        "high":     colors.HexColor("#f97316"),
        "medium":   colors.HexColor("#f5a623"),
        "low":      colors.HexColor("#3b82f6"),
    }
    
    PAGE_W = A4[0] - 2 * 0.7 * inch   # usable width
    
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False
    PAGE_W = 0
    NAVY = BLUE = BLUE_LT = SILVER = BORDER = TEXT = MUTED = None
    SEV_COLORS = {}

from sqlalchemy import func

from database.db import db
from models.threat import Threat


# ── Helpers ────────────────────────────────────────────────────────────────────

def _sev(v):   return (v or "low").lower()
def _cap(v):   return (v or "—").title()
def _str(v):   return str(v) if v else "—"
def _cnt(col): return db.session.query(col, func.count(Threat.id)).filter(col.isnot(None)).group_by(col).order_by(func.count(Threat.id).desc()).limit(5).all()


def _stat_table(stats: list[tuple[str, str]]) -> Table:
    """Horizontal row of labelled stat boxes."""
    n     = len(stats)
    col_w = PAGE_W / n
    data  = [[Paragraph(f"<b>{v}</b>", ParagraphStyle("sv", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=BLUE))   for _, v in stats],
             [Paragraph(lbl,          ParagraphStyle("sl", fontName="Helvetica",      fontSize=8,  leading=10, textColor=MUTED))    for lbl, _ in stats]]
    t = Table(data, colWidths=[col_w] * n, rowHeights=[28, 14])
    t.setStyle(TableStyle([
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",   (0, 0), (-1, -1), SILVER),
        ("BOX",          (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID",    (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    return t


def _section_table(headers: list[str], rows: list[list], col_widths: list[float]) -> Table:
    """Generic bordered data table with a navy header row."""
    data = [headers] + rows
    t    = Table(data, colWidths=col_widths)
    base = [
        ("BACKGROUND",    (0, 0), (-1, 0),   NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0),   colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),   "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1),  9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1),  [colors.white, SILVER]),
        ("TEXTCOLOR",     (0, 1), (-1, -1),  TEXT),
        ("GRID",          (0, 0), (-1, -1),  0.3, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1),  6),
        ("BOTTOMPADDING", (0, 0), (-1, -1),  6),
        ("LEFTPADDING",   (0, 0), (-1, -1),  8),
    ]
    t.setStyle(TableStyle(base))
    return t


def _ioc_row_style(idx: int, sev: str) -> list:
    """Colour the severity cell and alternate row background."""
    bg    = SILVER if idx % 2 == 0 else colors.white
    s_col = SEV_COLORS.get(sev, MUTED)
    return [
        ("BACKGROUND", (0, idx), (-1, idx), bg),
        ("BACKGROUND", (2, idx), (2, idx),  s_col),
        ("TEXTCOLOR",  (2, idx), (2, idx),  colors.white),
    ]


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_report() -> BytesIO:
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    # ── Data queries ───────────────────────────────────────────────────────────
    total_all      = Threat.query.count()
    total_week     = Threat.query.filter(Threat.created_at >= week_ago).count()
    total_critical = Threat.query.filter(Threat.severity == "critical").count()
    total_high     = Threat.query.filter(Threat.severity == "high").count()
    unique_sources = db.session.query(Threat.source).distinct().count()
    latest_iocs    = Threat.query.order_by(Threat.created_at.desc()).limit(50).all()
    sev_rows       = db.session.query(Threat.severity, func.count(Threat.id)).group_by(Threat.severity).order_by(func.count(Threat.id).desc()).all()
    top_countries  = _cnt(Threat.country)
    top_malware    = _cnt(Threat.malware_family)

    # ── Styles ─────────────────────────────────────────────────────────────────
    base   = getSampleStyleSheet()
    h1     = ParagraphStyle("H1",   fontName="Helvetica-Bold",   fontSize=22, leading=26, textColor=colors.white)
    h2     = ParagraphStyle("H2",   fontName="Helvetica-Bold",   fontSize=13, leading=16, textColor=NAVY,   spaceBefore=14, spaceAfter=6)
    meta_s = ParagraphStyle("Meta", fontName="Helvetica",         fontSize=9,  leading=11, textColor=colors.white)
    body_s = ParagraphStyle("Body", fontName="Helvetica",         fontSize=9,  leading=12, textColor=TEXT)
    foot_s = ParagraphStyle("Foot", fontName="Helvetica-Oblique", fontSize=8,  leading=10, textColor=MUTED)

    story = []

    # ── 1. Header banner ───────────────────────────────────────────────────────
    banner = Table(
        [[Paragraph("ThreatView", h1),
          Paragraph(f"Weekly Threat Landscape Report<br/><font size='9'>{now.strftime('%B %d, %Y  •  %H:%M UTC')}</font>", meta_s)]],
        colWidths=[PAGE_W * 0.45, PAGE_W * 0.55],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (0, -1),  14),
        ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
        ("RIGHTPADDING",  (1, 0), (-1, -1), 14),
        ("LINEBELOW",     (0, 0), (-1, -1), 3, BLUE),
    ]))
    story += [banner, Spacer(1, 14)]

    # ── 2. Executive summary stat boxes ────────────────────────────────────────
    story += [
        Paragraph("Executive Summary", h2),
        _stat_table([
            ("Total Threats",   f"{total_all:,}"),
            ("This Week",       f"{total_week:,}"),
            ("Critical",        f"{total_critical:,}"),
            ("High",            f"{total_high:,}"),
            ("Sources",         f"{unique_sources}"),
        ]),
        Spacer(1, 14),
    ]

    # ── 3. Severity breakdown ──────────────────────────────────────────────────
    if sev_rows:
        story.append(Paragraph("Severity Breakdown", h2))
        rows = [[_cap(s), f"{c:,}", f"{c / total_all * 100:.1f}%" if total_all else "—"] for s, c in sev_rows]
        story += [_section_table(["Severity", "Count", "% of Total"], rows, [PAGE_W * 0.3, PAGE_W * 0.35, PAGE_W * 0.35]), Spacer(1, 14)]

    # ── 4. Top countries ──────────────────────────────────────────────────────
    if top_countries:
        story.append(Paragraph("Top Origin Countries", h2))
        c_rows = [[_cap(c), f"{n:,}"] for c, n in top_countries]
        story += [_section_table(["Country", "Threat Count"], c_rows, [PAGE_W * 0.6, PAGE_W * 0.4]), Spacer(1, 14)]

    # ── 5. Top malware families ────────────────────────────────────────────────
    if top_malware:
        story.append(Paragraph("Top Malware Families", h2))
        m_rows = [[_cap(m), f"{n:,}"] for m, n in top_malware]
        story += [_section_table(["Malware Family", "Occurrences"], m_rows, [PAGE_W * 0.6, PAGE_W * 0.4]), Spacer(1, 14)]

    # ── 6. IOC listing ────────────────────────────────────────────────────────
    story.append(Paragraph(f"Recent Indicators ({len(latest_iocs)} shown)", h2))
    if not latest_iocs:
        story.append(Paragraph("No indicators ingested yet.", body_s))
    else:
        ioc_header = ["Indicator", "Type", "Severity", "Source", "Country", "First Seen"]
        ioc_cw     = [PAGE_W * 0.28, PAGE_W * 0.1, PAGE_W * 0.09, PAGE_W * 0.16, PAGE_W * 0.13, PAGE_W * 0.24]
        ioc_data   = [ioc_header]
        style_cmds = [
            ("BACKGROUND",    (0, 0), (-1, 0),   NAVY),
            ("TEXTCOLOR",     (0, 0), (-1, 0),   colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),   "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1),  8),
            ("GRID",          (0, 0), (-1, -1),  0.3, BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1),  5),
            ("BOTTOMPADDING", (0, 0), (-1, -1),  5),
            ("LEFTPADDING",   (0, 0), (-1, -1),  6),
        ]

        for i, t in enumerate(latest_iocs, start=1):
            sev   = _sev(t.severity)
            since = t.first_seen.strftime("%Y-%m-%d") if t.first_seen else "—"
            ioc_data.append([
                _str(t.indicator)[:45],
                _str(t.indicator_type),
                _cap(t.severity),
                _str(t.source)[:20],
                _str(t.country)[:18],
                since,
            ])
            style_cmds.extend(_ioc_row_style(i, sev))

        ioc_table = Table(ioc_data, colWidths=ioc_cw, repeatRows=1)
        ioc_table.setStyle(TableStyle(style_cmds))
        story.append(ioc_table)

    # ── 7. Footer ─────────────────────────────────────────────────────────────
    story += [
        Spacer(1, 20),
        HRFlowable(width="100%", thickness=0.5, color=BORDER),
        Spacer(1, 6),
        Paragraph(
            f"Generated by ThreatView  •  {now.strftime('%Y-%m-%d %H:%M:%S UTC')}  •  CONFIDENTIAL",
            foot_s,
        ),
    ]

    # ── Build ──────────────────────────────────────────────────────────────────
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="ThreatView Weekly Threat Landscape Report",
        author="ThreatView",
    )
    doc.build(story)
    buffer.seek(0)
    return buffer



def _severity_value(value: str | None) -> str:
    return (value or "Low").title()


def _country_value(value: str | None) -> str:
    return value or "Unknown"


def _malware_value(threat: Threat) -> str:
    # Keep this resilient to schema evolution while preferring explicit malware fields.
    malware = getattr(threat, "malware_family", None) or getattr(threat, "malware", None) or threat.category
    return malware or "N/A"


def generate_report() -> BytesIO:
    generated_at = datetime.now(timezone.utc)
    total_threats = Threat.query.count()
    latest_threats = Threat.query.order_by(Threat.created_at.desc()).limit(20).all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
        title="ThreatView Weekly Threat Landscape Report",
    )

    styles = getSampleStyleSheet()
    separator_style = ParagraphStyle(
        "Separator",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )
    report_title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )

    story = [
        Paragraph("====================================", separator_style),
        Spacer(1, 6),
        Paragraph("ThreatView", styles["Heading1"]),
        Paragraph("Weekly Threat Landscape Report", report_title_style),
        Spacer(1, 4),
        Paragraph(f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}", styles["Normal"]),
        Spacer(1, 6),
        Paragraph("====================================", separator_style),
        Spacer(1, 14),
        Paragraph("Summary", section_header_style),
        Paragraph(f"Total Threats: {total_threats}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Latest Threats", section_header_style),
    ]

    if not latest_threats:
        story.append(Paragraph("No threats available for this reporting window.", styles["Normal"]))
    else:
        for threat in latest_threats:
            details = [
                ["IOC", threat.indicator or "N/A"],
                ["Type", threat.indicator_type or "N/A"],
                ["Severity", _severity_value(threat.severity)],
                ["Source", threat.source or "Unknown"],
                ["Country", _country_value(threat.country)],
                ["Malware", _malware_value(threat)],
            ]
            details_table = Table(details, colWidths=[1.3 * inch, 4.9 * inch])
            details_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
                    ]
                )
            )
            story.extend(
                [
                    details_table,
                    Spacer(1, 6),
                    Paragraph("---", styles["Normal"]),
                    Spacer(1, 8),
                ]
            )

    story.extend([Spacer(1, 14), Paragraph("Generated by ThreatView", styles["Italic"])])

    doc.build(story)
    buffer.seek(0)
    return buffer