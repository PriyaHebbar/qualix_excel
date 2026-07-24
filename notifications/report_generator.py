import os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from django.conf import settings
from django.utils import timezone

def generate_excel_report(run):
    """
    Generates an Excel validation report for the given ValidationRun.
    Returns the absolute file path where the report is saved.
    """
    mapping = run.mapping
    results = run.results.select_related('column_mapping').all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Validation Report"

    col_headers = [
        'Validation Rule Name',
        'Source Value',
        'Target Value',
        'Status',
        'Error Message (if failed)'
    ]

    ws.append(col_headers)

    # Style header row
    header_fill = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid") # Deep Blue
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for r in results:
        status_val = "PASSED" if r.is_match else "FAILED"
        err_msg = r.difference if not r.is_match else ""
        
        rule_name = f"{r.column_mapping.source_column} - {r.operation.replace('_', ' ').title()}"
        
        ws.append([
            rule_name,
            str(r.source_value) if r.source_value is not None else "None",
            str(r.target_value) if r.target_value is not None else "None",
            status_val,
            err_msg
        ])

    # Formatting columns
    for row in range(2, ws.max_row + 1):
        for col in range(1, 6):
            cell = ws.cell(row=row, column=col)
            if col in [1, 5]:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            if col == 4:
                if cell.value == "PASSED":
                    cell.font = Font(name="Calibri", size=11, bold=True, color="15803D") # Green
                else:
                    cell.font = Font(name="Calibri", size=11, bold=True, color="B91C1C") # Red

    # Adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 15)

    # Add Report Narrative sheet
    add_report_narrative_sheet(wb, run)

    # Prepare save directory
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # Use run's created_at, with timezone.now() fallback if not saved/None
    val_date = run.created_at.strftime('%Y%m%d_%H%M%S') if run.created_at else timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"validation_report_{run.id}_{val_date}.xlsx"
    filepath = os.path.join(reports_dir, filename)
    wb.save(filepath)

    return filepath


def add_report_narrative_sheet(wb, run):
    """
    Adds a 'Report Narrative' sheet to the given Excel workbook `wb`
    populated with metadata about the `run`.
    """
    from openpyxl.styles import Font, Alignment, PatternFill
    from django.utils.timezone import localtime

    ws = wb.create_sheet(title="Report Narrative")
    
    # 1. Enable grid lines
    ws.views.sheetView[0].showGridLines = True

    # 2. Set Column Widths
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 30

    # 3. Row 1: Merged Title Block (A1:C1)
    ws.merge_cells('A1:C1')
    ws.row_dimensions[1].height = 40
    
    title_fill = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid") # Deep Blue
    title_font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    
    for col in ['A', 'B', 'C']:
        cell = ws[f'{col}1']
        cell.fill = title_fill
        
    ws['A1'] = "Validation Report Narrative"
    ws['A1'].font = title_font
    ws['A1'].alignment = Alignment(horizontal="center", vertical="center")

    # Row 2 is blank (default height, no content)

    # 4. Report Summary Heading
    ws['A3'] = "Report Summary"
    ws['A3'].font = Font(name="Calibri", size=11, bold=True, color="1E40AF")

    # Row 4: Run ID
    ws['A4'] = "Run ID"
    ws['A4'].font = Font(name="Calibri", size=11, bold=True)
    ws['B4'] = f"Run #{run.id}"
    ws['B4'].font = Font(name="Calibri", size=11)
    ws['B4'].alignment = Alignment(horizontal="left", vertical="center")

    # Row 5: Triggered By
    ws['A5'] = "Triggered By"
    ws['A5'].font = Font(name="Calibri", size=11, bold=True)
    ws['B5'] = run.triggered_by.username if run.triggered_by else "System"
    ws['B5'].font = Font(name="Calibri", size=11)
    ws['B5'].alignment = Alignment(horizontal="left", vertical="center")

    # Row 6: Execution Date
    ws['A6'] = "Execution Date"
    ws['A6'].font = Font(name="Calibri", size=11, bold=True)
    ws['B6'] = localtime(run.created_at).strftime('%Y-%m-%d %H:%M:%S') if run.created_at else "N/A"
    ws['B6'].font = Font(name="Calibri", size=11)
    ws['B6'].alignment = Alignment(horizontal="left", vertical="center")

    # Row 7: Overall Status (light colored status bar for A7:C7)
    status_str = run.status.upper() if run.status else "PENDING"
    
    # Resolve colors based on status
    if status_str == 'COMPLETED':
        status_text_color = "15803D" # Dark Green
        status_bg_color = "DCFCE7"   # Light Green
    elif status_str == 'FAILED':
        status_text_color = "B91C1C" # Dark Red
        status_bg_color = "FEE2E2"   # Light Red
    elif status_str in ('RUNNING', 'PENDING'):
        status_text_color = "854D0E" # Dark Yellow/Amber
        status_bg_color = "FEF08A"   # Light Yellow
    else:
        status_text_color = "374151" # Dark Gray
        status_bg_color = "F3F4F6"   # Light Gray

    status_fill = PatternFill(start_color=status_bg_color, end_color=status_bg_color, fill_type="solid")
    
    ws['A7'] = "Overall Status"
    ws['A7'].font = Font(name="Calibri", size=11, bold=True)
    ws['B7'] = status_str
    ws['B7'].font = Font(name="Calibri", size=11, bold=True, color=status_text_color)
    
    for col in ['A', 'B', 'C']:
        ws[f'{col}7'].fill = status_fill
        ws[f'{col}7'].alignment = Alignment(horizontal="left" if col != 'C' else "center", vertical="center")

    # Row 8 is blank

    # 5. Dataset Configuration Heading
    ws['A9'] = "Dataset Configuration"
    ws['A9'].font = Font(name="Calibri", size=11, bold=True, color="1E40AF")

    # Row 10: Table Headers
    ws['A10'] = "Metadata Property"
    ws['B10'] = "Source System"
    ws['C10'] = "Target System"
    
    header_fill = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    
    for col in ['A', 'B', 'C']:
        cell = ws[f'{col}10']
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    mapping = run.mapping

    # Helper for label styling in A11:A15
    bold_label_font = Font(name="Calibri", size=11, bold=True)
    normal_val_font = Font(name="Calibri", size=11)
    left_align = Alignment(horizontal="left", vertical="center")

    # Row 11: Connection Type
    ws['A11'] = "Connection Type"
    ws['A11'].font = bold_label_font
    ws['B11'] = mapping.source_connection.get_connection_type_display() if mapping.source_connection else "N/A"
    ws['B11'].font = normal_val_font
    ws['B11'].alignment = left_align
    ws['C11'] = mapping.target_connection.get_connection_type_display() if mapping.target_connection else "N/A"
    ws['C11'].font = normal_val_font
    ws['C11'].alignment = left_align

    # Row 12: Table Name
    ws['A12'] = "Table Name"
    ws['A12'].font = bold_label_font
    ws['B12'] = mapping.source_table.upper() if mapping.source_table else "N/A"
    ws['B12'].font = normal_val_font
    ws['B12'].alignment = left_align
    ws['C12'] = mapping.target_table.upper() if mapping.target_table else "N/A"
    ws['C12'].font = normal_val_font
    ws['C12'].alignment = left_align

    # Row 13: Schema
    ws['A13'] = "Schema"
    ws['A13'].font = bold_label_font
    ws['B13'] = mapping.source_schema if mapping.source_schema else "N/A"
    ws['B13'].font = normal_val_font
    ws['B13'].alignment = left_align
    ws['C13'] = mapping.target_schema if mapping.target_schema else "N/A"
    ws['C13'].font = normal_val_font
    ws['C13'].alignment = left_align

    # Helper to format date filter description cleanly using actual dates
    def format_date_filter(start_val, end_val):
        start_val = str(start_val).strip() if start_val else ""
        end_val = str(end_val).strip() if end_val else ""
        if not start_val and not end_val:
            return "No Date Filter"
        if start_val and end_val:
            if start_val == end_val:
                return start_val
            return f"{start_val} to {end_val}"
        return start_val or end_val

    # Row 14: Date Column & Row 15: Date Range Filter
    ws['A14'] = "Date Column"
    ws['A14'].font = bold_label_font
    
    ws['A15'] = "Date Range Filter"
    ws['A15'].font = bold_label_font

    # Resolve Source dates & columns
    src_start = run.source_date_filter_start or run.date_filter_start or mapping.source_date_filter_start or mapping.date_filter_start
    src_end = run.source_date_filter_end or run.date_filter_end or mapping.source_date_filter_end or mapping.date_filter_end
    src_filter_desc = format_date_filter(src_start, src_end)

    src_date_col = "None"
    if src_filter_desc != "No Date Filter":
        if mapping.source_date_column:
            src_date_col = mapping.source_date_column
        elif mapping.date_filter_column:
            src_date_col = mapping.date_filter_column

    # Resolve Target dates & columns
    tgt_start = run.target_date_filter_start or run.date_filter_start or mapping.target_date_filter_start or mapping.date_filter_start
    tgt_end = run.target_date_filter_end or run.date_filter_end or mapping.target_date_filter_end or mapping.date_filter_end
    tgt_filter_desc = format_date_filter(tgt_start, tgt_end)

    tgt_date_col = "None"
    if tgt_filter_desc != "No Date Filter":
        if mapping.target_date_column:
            tgt_date_col = mapping.target_date_column
        elif mapping.date_filter_column:
            tgt_date_col = mapping.date_filter_column

    ws['B14'] = src_date_col
    ws['B14'].font = normal_val_font
    ws['B14'].alignment = left_align
    ws['C14'] = tgt_date_col
    ws['C14'].font = normal_val_font
    ws['C14'].alignment = left_align

    ws['B15'] = src_filter_desc
    ws['B15'].font = normal_val_font
    ws['B15'].alignment = left_align
    ws['C15'] = tgt_filter_desc
    ws['C15'].font = normal_val_font
    ws['C15'].alignment = left_align
