import PyPDF2
import pdfplumber
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import tempfile
import os

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def pdf_to_excel(pdf_path: str) -> str:
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                data.extend(table)
    
    if not data:
        text = extract_text_from_pdf(pdf_path)
        lines = text.split('\n')
        data = [[line] for line in lines if line.strip()]
    
    df = pd.DataFrame(data)
    
    output_path = tempfile.mktemp(suffix='.xlsx')
    df.to_excel(output_path, index=False)
    
    return output_path

def excel_to_pdf(excel_path: str) -> str:
    df = pd.read_excel(excel_path)
    
    output_path = tempfile.mktemp(suffix='.pdf')
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    
    data = [df.columns.tolist()] + df.values.tolist()
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    doc.build([table])
    
    return output_path