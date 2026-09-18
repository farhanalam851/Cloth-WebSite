from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_invoice_pdf(order):
    """Builds a simple, professional invoice PDF for a paid order and
    returns it as an in-memory buffer, ready to be served as a download."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph('ClothBrand', styles['Title']))
    elements.append(Paragraph(f'Tax Invoice — Order #{order.id}', styles['Heading2']))
    elements.append(Spacer(1, 10))

    bill_to_lines = [f'<b>Bill To:</b> {order.full_name}']
    if order.company_name:
        bill_to_lines.append(f'Company: {order.company_name}')
    bill_to_lines.append(f'{order.address_line}, {order.city}, {order.state} {order.postal_code}, {order.country}')
    if order.gst_number:
        bill_to_lines.append(f'GSTIN: {order.gst_number}')
    bill_to_lines.append(f'Email: {order.email} &middot; Phone: {order.phone}')

    for line in bill_to_lines:
        elements.append(Paragraph(line, styles['Normal']))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(f'Order Date: {order.created_at.strftime("%d %b %Y")}', styles['Normal']))
    if order.razorpay_payment_id:
        elements.append(Paragraph(f'Payment Reference: {order.razorpay_payment_id}', styles['Normal']))
    elements.append(Spacer(1, 16))

    data = [['Product', 'Size / Colour', 'Qty', 'Unit Price (Rs.)', 'Amount (Rs.)']]
    for item in order.items.all():
        variant_label = f'{item.size} / {item.color}' if (item.size or item.color) else '—'
        data.append([
            item.product.name,
            variant_label,
            str(item.quantity),
            f'{item.price:.2f}',
            f'{item.get_cost():.2f}',
        ])

    table = Table(data, colWidths=[65 * mm, 35 * mm, 15 * mm, 30 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1c1c1c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 14))

    totals_data = [
        ['Subtotal', f'Rs. {order.get_subtotal():.2f}'],
        [f'GST ({order.tax_rate_percent}%)', f'Rs. {order.tax_amount:.2f}'],
        ['Shipping', f'Rs. {order.shipping_amount:.2f}'],
        ['Total', f'Rs. {order.get_total_cost():.2f}'],
    ]
    totals_table = Table(totals_data, colWidths=[140 * mm, 35 * mm])
    totals_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('LINEABOVE', (0, -1), (-1, -1), 0.75, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 24))

    elements.append(Paragraph(
        'This is a computer-generated invoice and does not require a signature.',
        styles['Italic']
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
