# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
import io
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from .utils import safe_text, slugify
import pandas as pd


def wrap_text(text: str, max_chars: int = 90):
    words = safe_text(text).split()
    lines = []
    current = []
    length = 0
    for w in words:
        if length + len(w) + 1 > max_chars:
            lines.append(" ".join(current))
            current = [w]
            length = len(w)
        else:
            current.append(w)
            length += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return lines or ["-"]


def generate_pdf_bytes(row: pd.Series) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    x_margin = 0.9 * inch
    y = height - 1.0 * inch

    def draw_heading(text):
        nonlocal y
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_margin, y, text)
        y -= 0.3 * inch

    def draw_label_value(label, value):
        nonlocal y
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_margin, y, label)
        c.setFont("Helvetica", 10)
        c.drawString(x_margin + 140, y, safe_text(value))
        y -= 0.22 * inch

    def draw_block(label, text):
        nonlocal y
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_margin, y, label)
        y -= 0.2 * inch
        c.setFont("Helvetica", 10)
        for line in wrap_text(text):
            if y < 0.75 * inch:
                c.showPage()
                y = height - 1.0 * inch
                c.setFont("Helvetica", 10)
            c.drawString(x_margin, y, line)
            y -= 0.18 * inch
        y -= 0.12 * inch

    name = safe_text(row.get("name", ""))
    primary_role = safe_text(row.get("primary_role", ""))
    secondary_role = safe_text(row.get("secondary_role", ""))
    tier = safe_text(row.get("tier", ""))
    score = safe_text(row.get("signal_strength", ""))
    rec = safe_text(row.get("Recommendation", ""))
    rec_conf = safe_text(row.get("Recommendation_Confidence", ""))
    desc = safe_text(row.get("description", ""))
    strengths = safe_text(row.get("Strengths", ""))
    weaknesses = safe_text(row.get("Weaknesses", ""))

    draw_heading("AI Talent Engine – Candidate Report")

    draw_label_value("Name:", name)
    draw_label_value("Primary role:", primary_role)
    draw_label_value("Secondary role:", secondary_role)
    draw_label_value("Tier:", tier)
    draw_label_value("Score:", score)
    draw_label_value("Recommendation:", f"{rec} ({rec_conf}%)")

    y -= 0.1 * inch
    draw_block("Summary / Description", desc)
    draw_block("Strengths", strengths)
    draw_block("Weaknesses / Gaps", weaknesses)

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def generate_pdf_filename(row: pd.Series) -> str:
    name = safe_text(row.get("name", "candidate"))
    return f"{slugify(name)}.pdf"

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
