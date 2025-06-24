import os
import csv
import uuid
import zipfile
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image, Paragraph, Table, TableStyle, Spacer, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_report_files(company, solution, auditor, audit_date, results, upload_folder):
    output_csv = os.path.join(upload_folder, f"audit_result_{uuid.uuid4()}.csv")
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([f"Audit Report for {company}"])
        writer.writerow([f"Solution: {solution}"])
        writer.writerow([f"Auditor: {auditor}"])
        writer.writerow([f"Date: {audit_date}"])
        writer.writerow([])
        writer.writerow(['Rule', 'Result', 'Current Value', 'Expected Value'])
        writer.writerows(results)

    pdf_path = output_csv.replace('.csv', '.pdf')
    generate_pdf(output_csv, pdf_path)

    safe_company = company.replace(" ", "_").replace("/", "_")
    safe_date = audit_date.replace(":", "-").replace(" ", "_")
    zip_filename = f"audit_{safe_company}_{safe_date}.zip"
    zip_path = os.path.join(upload_folder, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(output_csv, os.path.basename(output_csv))
        zipf.write(pdf_path, os.path.basename(pdf_path))

    return zip_path

def generate_pdf(csv_path, pdf_path):
    with open(csv_path, newline='') as csvfile:
        reader = list(csv.reader(csvfile))
        metadata, headers, rows = [], [], []

        for row in reader:
            if not row:
                continue
            elif len(row) == 1 and ":" in row[0]:
                metadata.append(row[0])
            elif not headers and "Rule" in row:
                headers = row
            elif len(row) >= 4:
                rows.append(row)

        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=50)
        elements, styles = [], getSampleStyleSheet()
        styleN = ParagraphStyle(name='Normal', fontSize=9, leading=12)

        logo_path = os.path.join("logo", "logo_dataprotect.png")
        if os.path.exists(logo_path):
            img = Image(logo_path, width=100, height=40)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, 20))

        elements.append(Paragraph("Audit Report", styles['Title']))
        elements.append(Spacer(1, 12))
        for line in metadata:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 20))

        table_data = [[Paragraph(h, styleN) for h in headers]] + [[Paragraph(c, styleN) for c in row] for row in rows]

        table = Table(table_data, repeatRows=1, colWidths=[2*inch, 1*inch, 2.3*inch, 2.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e73632")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)
        doc.build(elements)
