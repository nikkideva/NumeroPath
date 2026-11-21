from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from .interpretations import get_number_meaning, build_combined_summary

def create_pdf(profile: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Combined Numerology Report", styles["Title"]),
        Spacer(1, 6*mm),
        Paragraph(f"Name: {profile['name']}", styles["Normal"]),
        Paragraph(f"Date of birth: {profile['dob']}", styles["Normal"]),
        Spacer(1, 5*mm),
        Paragraph("Core numbers", styles["Heading2"]),
    ]
    rows = [
        ["Calculation", "Result"],
        ["Vedic Mulank", str(profile["mulank"])],
        ["Vedic Bhagyank", str(profile["bhagyank"])],
        ["Chaldean name compound", str(profile["name_compound"])],
        ["Chaldean name root", str(profile["name_root"])],
        ["Personal year", str(profile["personal_year"])],
        ["Personal month", str(profile["personal_month"])],
    ]
    table = Table(rows, colWidths=[85*mm, 65*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#20283A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8B8B8")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [table, Spacer(1, 5*mm), Paragraph("Traditional interpretations", styles["Heading2"])]
    for label, key in [
        ("Mulank", "mulank"), ("Bhagyank", "bhagyank"), ("Name root", "name_root")
    ]:
        number = profile[key]
        meaning = get_number_meaning(number)
        story.append(Paragraph(
            f"<b>{label} {number}</b> — {meaning['theme']}. "
            f"Strength theme: {meaning['strength']}. "
            f"Reflection point: {meaning['watchout']}. "
            f"Traditional colour association: {meaning['colour']}; "
            f"day: {meaning['day']}.",
            styles["BodyText"]
        ))
        story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Combined reading", styles["Heading2"]))
    for line in build_combined_summary(profile):
        story.append(Paragraph(line, styles["BodyText"]))
        story.append(Spacer(1, 2*mm))
    story += [
        Spacer(1, 5*mm),
        Paragraph(
            "Method note: This report uses one stated Chaldean letter mapping and "
            "a simplified Vedic-style 1–9 reduction. Traditions and practitioners "
            "may use different rules. Numerology is a cultural/spiritual practice, "
            "not a scientifically validated way to predict personality or events. "
            "Lucky-number ranking is an app-defined heuristic, not a guarantee.",
            styles["Italic"]
        )
    ]
    doc.build(story)
    return buffer.getvalue()
