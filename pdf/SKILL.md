---
name: pdf
description: >
  Use whenever the user mentions a PDF file or needs to work with one — reading,
  extracting text or tables, merging, splitting, rotating pages, adding watermarks,
  creating PDFs from scratch, filling forms, encrypting, decrypting, extracting
  images, or running OCR on scanned documents.
user-invocable: true
requires:
  - type: python
    check: "python3 -c 'import pypdf'"
    install-cmd: "pip install pypdf pymupdf pillow reportlab"
    packages: [pypdf, pymupdf, pillow, reportlab]
---

# PDF

## Decide your approach first

Before writing any code, identify what the user actually needs:

| Goal | Right library |
|---|---|
| Read text / extract content | `pypdf` (fast, no deps beyond pip) |
| High-fidelity text + layout | `pymupdf` (`import fitz`) |
| Create a new PDF from scratch | `reportlab` |
| Image extraction | `pymupdf` |
| OCR on scanned pages | `pytesseract` + `pillow` (ask user to install) |
| Merge / split / rotate / encrypt | `pypdf` |
| Fill an existing form | `pypdf` (AcroForm) |

Pick the simplest library that covers the task. Don't import multiple libraries for a job one can do.

## Reading and extracting

```python
from pypdf import PdfReader

reader = PdfReader("file.pdf")
print(f"{len(reader.pages)} pages")

# All text
full_text = "\n".join(page.extract_text() or "" for page in reader.pages)

# Single page (0-indexed)
page_text = reader.pages[2].extract_text()
```

For better layout fidelity (tables, multi-column):
```python
import fitz  # pymupdf

doc = fitz.open("file.pdf")
for page in doc:
    text = page.get_text("text")   # plain text
    blocks = page.get_text("dict") # structured blocks with coordinates
```

## Merge and split

```python
from pypdf import PdfWriter, PdfReader

# Merge multiple PDFs
writer = PdfWriter()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    writer.append(path)
with open("merged.pdf", "wb") as f:
    writer.write(f)

# Extract a page range (pages 3-7, 0-indexed)
writer = PdfWriter()
reader = PdfReader("source.pdf")
for i in range(2, 7):
    writer.add_page(reader.pages[i])
with open("extract.pdf", "wb") as f:
    writer.write(f)
```

## Rotate, watermark, encrypt

```python
from pypdf import PdfWriter, PdfReader

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.rotate(90)          # 90, 180, or 270
    writer.add_page(page)

# Encrypt
writer.encrypt("password")

with open("output.pdf", "wb") as f:
    writer.write(f)
```

Overlay watermark (stamp an existing watermark PDF onto each page):
```python
from pypdf import PdfWriter, PdfReader

stamp = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(stamp)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as f:
    writer.write(f)
```

## Create a PDF from scratch

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

c = canvas.Canvas("output.pdf", pagesize=A4)
width, height = A4

c.setFont("Helvetica-Bold", 16)
c.drawString(72, height - 72, "Title")

c.setFont("Helvetica", 12)
c.drawString(72, height - 110, "Body text goes here.")

c.showPage()   # new page
c.save()
```

For richer layouts (tables, styles, multi-page flow), use `reportlab.platypus`:
```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("output.pdf", pagesize=A4)
styles = getSampleStyleSheet()
story = [
    Paragraph("My Report", styles["Title"]),
    Paragraph("Introduction paragraph.", styles["Normal"]),
]
doc.build(story)
```

## Fill a PDF form (AcroForm)

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()
writer.append(reader)

# List available fields first
fields = reader.get_fields()
print(fields.keys())

# Fill fields
writer.update_page_form_field_values(
    writer.pages[0],
    {"field_name": "value", "other_field": "other_value"}
)

with open("filled.pdf", "wb") as f:
    writer.write(f)
```

## Extract images

```python
import fitz

doc = fitz.open("file.pdf")
for page_num, page in enumerate(doc):
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base_image = doc.extract_image(xref)
        img_bytes = base_image["image"]
        ext = base_image["ext"]
        with open(f"page{page_num}_img{img_index}.{ext}", "wb") as f:
            f.write(img_bytes)
```

## OCR on scanned PDFs

Requires Tesseract to be installed on the system (`apt install tesseract-ocr` or `brew install tesseract`).

```python
import fitz
import pytesseract
from PIL import Image
import io

doc = fitz.open("scanned.pdf")
text_pages = []

for page in doc:
    # Render page to image at 300 DPI
    mat = fitz.Matrix(300/72, 300/72)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text_pages.append(pytesseract.image_to_string(img))

full_text = "\n\n".join(text_pages)
```

Ask the user if Tesseract is installed before running this — it is a system-level dependency.

## Error handling patterns

Always verify the file exists and is a valid PDF before processing:

```python
import os
from pypdf import PdfReader
from pypdf.errors import PdfReadError

def safe_read(path: str) -> PdfReader | None:
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        return None
    try:
        return PdfReader(path)
    except PdfReadError as e:
        print(f"Could not read PDF: {e}")
        return None
```

For encrypted PDFs, try decrypting first:
```python
reader = PdfReader("protected.pdf")
if reader.is_encrypted:
    reader.decrypt("password")
```

## Checklist before delivering

- [ ] Output file opens without errors
- [ ] Page count matches expectations
- [ ] Text extraction is readable (not garbage characters)
- [ ] For forms: all fields are filled and visible
- [ ] File size is reasonable (flag if > 50 MB unexpectedly)
