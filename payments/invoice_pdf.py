from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def render_invoice_pdf(*, transaction_id: int, customer: str, amount: str, currency: str, date: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Invoice")

    y -= 40
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Transaction ID: {transaction_id}")
    y -= 20
    c.drawString(50, y, f"Customer: {customer}")
    y -= 20
    c.drawString(50, y, f"Amount Paid: {amount} {currency.upper()}")
    y -= 20
    c.drawString(50, y, f"Date: {date}")

    c.showPage()
    c.save()
    return buffer.getvalue()

