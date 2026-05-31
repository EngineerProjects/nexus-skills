---
name: xlsx
description: >
  Use whenever a spreadsheet is the primary input or output — .xlsx, .xlsm,
  .csv, .tsv files. Triggers: open/read/edit/create spreadsheet, fix messy
  tabular data, add columns, charts, formulas, pivot tables, conditional
  formatting. Not for Word documents, HTML reports, or Google Sheets API work.
user-invocable: true
requires:
  - type: python
    check: "python3 -c 'import openpyxl'"
    install-cmd: "pip install openpyxl"
    packages: [openpyxl]
---

# XLSX

`openpyxl` reads and writes `.xlsx` / `.xlsm` files.
For `.csv` / `.tsv`, use the standard library `csv` module or `pandas` if already available.

## Read a spreadsheet

```python
from openpyxl import load_workbook

wb = load_workbook("data.xlsx")
ws = wb.active   # or wb["Sheet1"]

print(f"Dimensions: {ws.dimensions}")
print(f"Rows: {ws.max_row}, Columns: {ws.max_column}")

# Iterate rows
for row in ws.iter_rows(values_only=True):
    print(row)

# Read a specific cell
value = ws["B3"].value
value = ws.cell(row=3, column=2).value
```

Read with headers as dict:
```python
rows = ws.iter_rows(min_row=1, values_only=True)
headers = next(rows)
data = [dict(zip(headers, row)) for row in rows]
```

## Create a spreadsheet from scratch

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Report"

# Headers
headers = ["Name", "Q1", "Q2", "Q3", "Q4", "Total"]
ws.append(headers)

# Style the header row
header_fill = PatternFill("solid", fgColor="1F497D")
header_font = Font(bold=True, color="FFFFFF")
for cell in ws[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

# Data rows
data = [
    ("Alice", 12000, 15000, 13500, 18000),
    ("Bob",   9800,  10200, 11000, 12500),
]
for name, q1, q2, q3, q4 in data:
    ws.append([name, q1, q2, q3, q4, f"=SUM(B{ws.max_row}:E{ws.max_row})"])

# Auto column width
for col in ws.columns:
    max_len = max(len(str(cell.value or "")) for cell in col)
    ws.column_dimensions[get_column_letter(col[0].column)].width = max_len + 4

wb.save("report.xlsx")
```

## Edit an existing spreadsheet

Always work on a copy:
```python
import shutil
shutil.copy("data.xlsx", "data.xlsx.bak")

wb = load_workbook("data.xlsx")
ws = wb.active

# Find and update a cell
for row in ws.iter_rows():
    for cell in row:
        if cell.value == "OLD":
            cell.value = "NEW"

wb.save("data.xlsx")
```

## Formulas

```python
ws["F2"] = "=SUM(B2:E2)"
ws["G2"] = "=AVERAGE(B2:E2)"
ws["H2"] = "=IF(F2>50000,\"High\",\"Normal\")"

# VLOOKUP example
ws["I2"] = '=VLOOKUP(A2,Sheet2!$A:$B,2,FALSE)'
```

**Important:** `openpyxl` writes the formula string. The value is computed when the file is opened in Excel/LibreOffice. To get the computed value programmatically, use `data_only=True` when reading (requires the file to have been saved by Excel first):
```python
wb = load_workbook("data.xlsx", data_only=True)
```

## Conditional formatting

```python
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule, CellIsRule
from openpyxl.styles import PatternFill

# Color scale: green → yellow → red
rule = ColorScaleRule(
    start_type="min", start_color="00FF00",
    mid_type="percentile", mid_value=50, mid_color="FFFF00",
    end_type="max", end_color="FF0000"
)
ws.conditional_formatting.add("B2:B100", rule)

# Highlight cells above threshold
red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
rule2 = CellIsRule(operator="greaterThan", formula=["10000"], fill=red_fill)
ws.conditional_formatting.add("C2:C100", rule2)

wb.save("formatted.xlsx")
```

## Charts

```python
from openpyxl.chart import BarChart, Reference

chart = BarChart()
chart.type = "col"
chart.title = "Quarterly Revenue"
chart.y_axis.title = "Revenue (€)"
chart.x_axis.title = "Employee"

data_ref = Reference(ws, min_col=2, max_col=5, min_row=1, max_row=ws.max_row)
cats = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats)
chart.shape = 4
chart.width = 20
chart.height = 12

ws.add_chart(chart, "A10")
wb.save("with_chart.xlsx")
```

## Multiple sheets

```python
wb = Workbook()

# Create sheets
ws1 = wb.active
ws1.title = "Summary"

ws2 = wb.create_sheet("Raw Data")
ws3 = wb.create_sheet("Pivot", index=1)  # insert at position 1

# Copy data between sheets
for row in ws2.iter_rows(values_only=True):
    ws1.append(row)

# Delete a sheet
del wb["Temp"]

wb.save("multi.xlsx")
```

## CSV / TSV import

```python
import csv
from openpyxl import Workbook

wb = Workbook()
ws = wb.active

with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        ws.append(row)

wb.save("from_csv.xlsx")
```

## Freeze panes and filters

```python
# Freeze row 1 (header always visible)
ws.freeze_panes = "A2"

# Auto-filter on header row
ws.auto_filter.ref = ws.dimensions
```

## Checklist before delivering

- [ ] File opens without errors
- [ ] All sheets present with correct names
- [ ] Formulas show expected values (no #REF!, #DIV/0!, #VALUE! errors)
- [ ] Charts visible and labelled
- [ ] Column widths sized to content
- [ ] Backup of original made before in-place edits
