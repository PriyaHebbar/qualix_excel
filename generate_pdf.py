import os
import re
import sys
import markdown
from fpdf import FPDF

class QualixPDF(FPDF):
    def header(self):
        # We don't want headers on the cover/first page
        if self.page_no() == 1:
            return
        
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(30, 64, 175)  # HDFC Blue
        self.cell(0, 8, 'QualiX - Enterprise Data Quality & Validation Platform', border=0, new_x="RIGHT", new_y="TOP", align='L')
        self.set_font('helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Standard Operating Procedure (SOP)', border=0, new_x="LMARGIN", new_y="NEXT", align='R')
        
        # Horizontal thin line
        self.set_draw_color(220, 220, 220)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        # Left-aligned footnote
        self.cell(0, 10, 'HDFC Bank - Internal Use Only', border=0, new_x="RIGHT", new_y="TOP", align='L')
        # Right-aligned page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', border=0, new_x="LMARGIN", new_y="NEXT", align='R')

def convert_md_to_pdf(md_path, pdf_path):
    print(f"Reading markdown from: {md_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Preprocess markdown to remove/convert alert boxes and clean tables
    # Convert GitHub Alerts (e.g. > [!NOTE] -> **NOTE:**)
    md_content = re.sub(r'>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', r'**\1:**', md_content)
    
    # Strip blockquote markers but keep paragraph text
    md_content = re.sub(r'^\s*>\s*', '', md_content, flags=re.MULTILINE)

    # Convert Markdown to HTML
    print("Converting Markdown to HTML...")
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    # Strip internal anchor links starting with # to avoid FPDF2 Named Destination errors
    html_content = re.sub(r'<a\b[^>]*href="#[^"]*">(.*?)</a>', r'\1', html_content, flags=re.IGNORECASE)

    # Style definitions for write_html
    # Strip out nested HTML formatting tags from inside table cells (td and th) to satisfy fpdf2's write_html parser
    def strip_tags(match):
        cell_attributes = match.group(1) or ""
        cell_content = match.group(2)
        cleaned_content = re.sub(r'<[^>]+>', '', cell_content)
        return f'<td{cell_attributes}>{cleaned_content}</td>'

    def strip_tags_th(match):
        cell_attributes = match.group(1) or ""
        cell_content = match.group(2)
        cleaned_content = re.sub(r'<[^>]+>', '', cell_content)
        return f'<th{cell_attributes}>{cleaned_content}</th>'

    # Match td/th tags with any optional attributes (like style="text-align: left;")
    html_content = re.sub(r'<td\b([^>]*)>(.*?)</td>', strip_tags, html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<th\b([^>]*)>(.*?)</th>', strip_tags_th, html_content, flags=re.DOTALL | re.IGNORECASE)

    # Wrap in basic HTML structure and style tags
    styled_html = f"""
    <html>
    <head>
    <style>
      body {{ font-family: helvetica; font-size: 10pt; color: #333333; line-height: 1.5; }}
      h1 {{ color: #1E40AF; font-size: 22pt; font-weight: bold; margin-top: 15px; margin-bottom: 15px; }}
      h2 {{ color: #1E40AF; font-size: 14pt; font-weight: bold; margin-top: 15px; margin-bottom: 10px; border-bottom: 1px solid #E5E7EB; }}
      h3 {{ color: #2563EB; font-size: 11pt; font-weight: bold; margin-top: 10px; margin-bottom: 5px; }}
      p {{ margin-bottom: 8px; }}
      ul {{ margin-left: 15px; margin-bottom: 8px; }}
      li {{ margin-bottom: 4px; }}
      strong {{ font-weight: bold; color: #1E293B; }}
      b {{ font-weight: bold; color: #1E293B; }}
      table {{ border-collapse: collapse; width: 100%; margin-top: 10px; margin-bottom: 10px; }}
      th {{ background-color: #1E40AF; color: white; font-weight: bold; padding: 5px; border: 1px solid #CBD5E1; text-align: left; }}
      td {{ padding: 5px; border: 1px solid #CBD5E1; }}
    </style>
    </head>
    <body>
      {html_content}
    </body>
    </html>
    """

    # Initialize FPDF
    print("Initializing PDF generation...")
    pdf = QualixPDF()
    pdf.alias_nb_pages()
    
    # ── Page 1: COVER PAGE ──
    pdf.add_page()
    pdf.set_y(40)
    # HDFC Bank Header
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(30, 64, 175)  # HDFC Blue
    pdf.cell(0, 10, 'HDFC BANK', border=0, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(20)
    
    # Big Title
    pdf.set_font('helvetica', 'B', 28)
    pdf.set_text_color(15, 23, 42)
    pdf.multi_cell(0, 15, 'QualiX User Manual', border=0, align='C')
    pdf.ln(5)
    
    # Subtitle
    pdf.set_font('helvetica', '', 12)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 10, 'Standard Operating Procedure (SOP) & Reference Guide', border=0, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    
    # Divider line
    pdf.set_draw_color(30, 64, 175)
    pdf.set_line_width(1)
    pdf.line(40, pdf.get_y(), 170, pdf.get_y())
    pdf.ln(25)
    
    # Metadata Block
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'Platform: Enterprise Data Quality & Validation Platform', border=0, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Version: 1.0 (Enterprise Edition)', border=0, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Date: July 2026', border=0, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, 'Classification: HDFC Bank Internal Use Only', border=0, new_x="LMARGIN", new_y="NEXT", align='C')
    
    # ── Page 2: CONTENT ──
    pdf.add_page()
    pdf.set_y(20)
    
    print("Writing HTML content to PDF...")
    pdf.write_html(styled_html)
    
    # Save PDF
    print(f"Saving PDF to: {pdf_path}")
    pdf.output(pdf_path)
    print("PDF generation completed successfully!")

if __name__ == '__main__':
    md_file = 'SOP_User_Manual.md'
    pdf_file = 'SOP_User_Manual.pdf'
    
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found in current directory.")
        sys.exit(1)
        
    try:
        convert_md_to_pdf(md_file, pdf_file)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
