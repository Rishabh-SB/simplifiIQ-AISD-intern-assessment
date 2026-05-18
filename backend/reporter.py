import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(company_name: str, enriched_data: dict) -> str:
    """
    Generates a highly professional 2-page business automation audit report PDF.
    Returns the absolute file path to the generated PDF document.
    """
    # Define file output path
    filename = f"{company_name.replace(' ', '_')}_Automation_Audit.pdf"
    filepath = os.path.join(os.getcwd(), filename)
    
    # Initialize Document with clean margins
    doc = SimpleDocTemplate(
        filepath, 
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    # Custom Palette Setup (Executive Slate & Deep Navy) [cite: 26]
    primary_color = colors.HexColor("#1A365D")   # Deep Corporate Navy
    secondary_color = colors.HexColor("#2B6CB0") # Slate Blue
    text_color = colors.HexColor("#2D3748")      # Dark Charcoal
    bg_light = colors.HexColor("#F7FAFC")        # Soft Grey Background
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Layout Configurations [cite: 26]
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontSize=24, leading=28,
        textColor=primary_color, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'], fontSize=11, leading=14,
        textColor=secondary_color, spaceAfter=20
    )
    section_heading = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'], fontSize=14, leading=18,
        textColor=primary_color, spaceBefore=14, spaceAfter=8, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'], fontSize=10, leading=15,
        textColor=text_color, spaceAfter=10
    )
    
    story = []
    
    # --- Header Banner Component ---
    story.append(Paragraph(f"AI Automation & Growth Audit", title_style))
    story.append(Paragraph(f"Prepared Exclusively for: <b>{company_name}</b>", subtitle_style))
    story.append(Spacer(1, 10))
    
    # --- Section: Corporate Overview Table ---
    story.append(Paragraph("1. Strategic Profile Discovery", section_heading))
    
    profile_table_data = [
        [Paragraph("<b>Target Domain Industry:</b>", body_style), Paragraph(enriched_data.get('industry', 'N/A'), body_style)],
        [Paragraph("<b>Core Value Proposition:</b>", body_style), Paragraph(enriched_data.get('value_prop', 'N/A'), body_style)],
        [Paragraph("<b>Primary Target Audience:</b>", body_style), Paragraph(enriched_data.get('audience', 'N/A'), body_style)]
    ]
    
    profile_table = Table(profile_table_data, colWidths=[150, 380])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 15))
    
    # --- Section: Business Summary ---
    story.append(Paragraph("2. Executive Summary", section_heading))
    story.append(Paragraph(enriched_data.get('summary', 'Analysis ongoing.'), body_style))
    story.append(Spacer(1, 15))
    
    # --- Section: Tailored Transformation Strategies ---
    story.append(Paragraph("3. Target Automation & Scaling Blueprints", section_heading))
    story.append(Paragraph("Based on our assessment of your digital footprint, here are three actionable optimization frameworks:", body_style))
    story.append(Spacer(1, 5))
    
    strategies = [
        ("Architecture Framework Alpha", enriched_data.get('strategy_1', '')),
        ("Process Optimisation Beta", enriched_data.get('strategy_2', '')),
        ("Growth Pipeline Gamma", enriched_data.get('strategy_3', ''))
    ]
    
    for idx, (title, description) in enumerate(strategies, start=1):
        if description:
            item_text = f"<b>{idx}. {title}:</b> {description}"
            story.append(Paragraph(item_text, body_style))
            story.append(Spacer(1, 4))
            
    # --- Footer Note Block ---
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.gray, alignment=1)
    story.append(Paragraph("Confidential Internal Advisory Report — Powered by SimplifIQ Lead Intelligence Platform Engine", footer_style))
    
    # Build the document
    doc.build(story)
    return filepath