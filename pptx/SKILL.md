---
name: pptx
description: >
  Use whenever a .pptx file is involved — creating slide decks, pitch decks,
  presentations, reading/extracting content from slides, editing or updating
  existing presentations, merging decks, adding animations, or working with
  speaker notes. Triggers: deck, slides, presentation, .pptx filename,
  "make me slides", "create a presentation".
user-invocable: true
requires:
  - type: python
    check: "python3 -c 'import pptx'"
    install-cmd: "pip install python-pptx pillow"
    packages: [python-pptx, pillow]
---

# PPTX

`python-pptx` is the standard library for reading and writing `.pptx` files.

## Read an existing presentation

```python
from pptx import Presentation

prs = Presentation("deck.pptx")

print(f"{len(prs.slides)} slides")

for i, slide in enumerate(prs.slides):
    print(f"\n--- Slide {i + 1} ---")
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                print(para.text)
```

Extract all text at once:
```python
def extract_text(path: str) -> str:
    prs = Presentation(path)
    lines = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                lines.extend(p.text for p in shape.text_frame.paragraphs if p.text)
    return "\n".join(lines)
```

## Create a presentation from scratch

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
slide_width = prs.slide_width
slide_height = prs.slide_height

# --- Title slide ---
blank_layout = prs.slide_layouts[6]  # blank
slide = prs.slides.add_slide(blank_layout)

# Title text box
txBox = slide.shapes.add_textbox(
    Inches(1), Inches(2.5), Inches(8), Inches(1.5)
)
tf = txBox.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "Presentation Title"
run.font.size = Pt(40)
run.font.bold = True
run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

prs.save("deck.pptx")
```

## Use built-in slide layouts

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()

# Layout 1 = Title and Content
layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(layout)

title = slide.shapes.title
title.text = "Slide Title"

body = slide.placeholders[1]
tf = body.text_frame
tf.text = "First bullet"
tf.add_paragraph().text = "Second bullet"
tf.add_paragraph().text = "Third bullet"

prs.save("deck.pptx")
```

Available layouts (index → name):
```python
for i, layout in enumerate(prs.slide_layouts):
    print(i, layout.name)
```

## Background color

```python
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from lxml import etree

def set_slide_background(slide, hex_color: str):
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(r, g, b)
```

## Images

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

slide.shapes.add_picture(
    "image.png",
    left=Inches(1),
    top=Inches(1.5),
    width=Inches(6),
    height=Inches(4)
)
prs.save("with_image.pptx")
```

## Tables

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

rows, cols = 4, 3
table = slide.shapes.add_table(
    rows, cols,
    left=Inches(1), top=Inches(1.5),
    width=Inches(8), height=Inches(3)
).table

# Headers
headers = ["Name", "Role", "Score"]
for col, text in enumerate(headers):
    cell = table.cell(0, col)
    cell.text = text
    cell.text_frame.paragraphs[0].runs[0].font.bold = True

# Data
data = [("Alice", "Eng", "95"), ("Bob", "Design", "88"), ("Carol", "PM", "91")]
for row_idx, (name, role, score) in enumerate(data, start=1):
    table.cell(row_idx, 0).text = name
    table.cell(row_idx, 1).text = role
    table.cell(row_idx, 2).text = score

prs.save("table.pptx")
```

## Speaker notes

```python
slide = prs.slides.add_slide(layout)
notes_slide = slide.notes_slide
notes_slide.notes_text_frame.text = "Speaker notes go here."
```

Read notes from an existing deck:
```python
for i, slide in enumerate(prs.slides):
    if slide.has_notes_slide:
        print(f"Slide {i+1}:", slide.notes_slide.notes_text_frame.text)
```

## Merge presentations

```python
from pptx import Presentation
from pptx.util import Inches
from copy import deepcopy
from lxml import etree

def merge_pptx(paths: list[str], output: str):
    base = Presentation(paths[0])
    for path in paths[1:]:
        src = Presentation(path)
        for slide in src.slides:
            slide_layout = base.slide_layouts[6]
            new_slide = base.slides.add_slide(slide_layout)
            for shape in slide.shapes:
                el = deepcopy(shape._element)
                new_slide.shapes._spTree.insert(2, el)
    base.save(output)

merge_pptx(["part1.pptx", "part2.pptx"], "merged.pptx")
```

## Design tips for the agent

When creating a deck programmatically:
- Limit text per slide: max 5-6 bullets, max 10 words per bullet
- Use high contrast: dark text on light background or vice versa
- Keep font sizes readable: title ≥ 28pt, body ≥ 18pt
- Consistent color palette across all slides (define 2-3 colors upfront)
- One key idea per slide

## Checklist before delivering

- [ ] Presentation opens without errors
- [ ] All slides present (count matches)
- [ ] No placeholder text ("Click to edit…")
- [ ] Images load correctly
- [ ] Speaker notes included if requested
- [ ] Font sizes readable (≥ 18pt for body)
