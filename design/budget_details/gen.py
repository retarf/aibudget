#!/usr/bin/env python3
"""Generate a high-fidelity, layered SVG mockup of the Budget Detail page
(Mantine v9 dark) for import into Figma. Each logical block is a named <g>
so it becomes an editable, movable layer."""

import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))

# --- Mantine v9 dark tokens ---------------------------------------------------
BG = "#1a1a1a"          # canvas behind frames
SURFACE = "#242424"     # page / modal body (color-body, dark[7])
ELEV = "#2e2e2e"        # inputs, segmented track, default button (dark[6])
BORDER = "#424242"      # dividers / input borders (dark[4])
TEXT = "#C9C9C9"        # default text (dark[0])
DIM = "#828282"         # dimmed text (dark[2])
INDIGO = "#4c6ef5"      # filled primary button (indigo[6])
INDIGO_LINK = "#748ffc" # anchor (indigo[4])
INDIGO_SUB = "#91a7ff"  # subtle primary text (indigo[3])
RED = "#ff8787"         # subtle red text (red[4])
RED_FILL = "#fa5252"    # filled red (red[6])
WHITE = "#ffffff"
FONT = "Inter, -apple-system, 'Segoe UI', Roboto, sans-serif"

out = []
def emit(s): out.append(s)

def g_open(gid):  emit(f'<g id="{escape(gid)}">')
def g_close():    emit('</g>')

def rect(x, y, w, h, fill, rx=0, stroke=None, sw=1, opacity=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'
    if stroke: s += f' stroke="{stroke}" stroke-width="{sw}"'
    if opacity is not None: s += f' opacity="{opacity}"'
    emit(s + '/>')

def line(x1, y1, x2, y2, stroke, sw=1):
    emit(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"/>')

def text(x, y, s, size=14, fill=TEXT, weight=400, anchor="start"):
    emit(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
         f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')

def char_w(size): return size * 0.56

def button(x, y, label, kind="filled", size="sm"):
    """kind: filled | default | subtle | subtle-red. Returns width."""
    h = 36 if size == "sm" else 28
    fs = 14 if size == "sm" else 13
    pad = 18 if size == "sm" else 12
    w = int(len(label) * char_w(fs) + pad * 2)
    if kind == "filled":
        rect(x, y, w, h, INDIGO, rx=6)
        text(x + w/2, y + h/2 + fs*0.35, label, fs, WHITE, 600, "middle")
    elif kind == "default":
        rect(x, y, w, h, ELEV, rx=6, stroke=BORDER, sw=1)
        text(x + w/2, y + h/2 + fs*0.35, label, fs, TEXT, 500, "middle")
    elif kind == "subtle":
        text(x + w/2, y + h/2 + fs*0.35, label, fs, INDIGO_SUB, 500, "middle")
    elif kind == "subtle-red":
        text(x + w/2, y + h/2 + fs*0.35, label, fs, RED, 500, "middle")
    return w

def input_field(x, y, w, label, value, placeholder=False, disabled=False):
    """Returns total height consumed (label + box)."""
    text(x, y, label, 13, TEXT, 500)
    by = y + 8
    bg = "#262626" if disabled else ELEV
    rect(x, by, w, 36, bg, rx=6, stroke=BORDER, sw=1)
    vfill = DIM if (placeholder or disabled) else TEXT
    text(x + 12, by + 23, value, 14, vfill)
    return 8 + 36 + 24  # label gap + box + stack gap

def segmented(x, y, w, opts, active=None):
    h = 36
    rect(x, y, w, h, ELEV, rx=8)
    seg_w = w / len(opts)
    for i, opt in enumerate(opts):
        sx = x + i*seg_w
        is_active = (opt == active)
        if is_active:
            rect(sx+3, y+3, seg_w-6, h-6, "#424242", rx=6)
        text(sx + seg_w/2, y + h/2 + 5, opt, 14,
             TEXT if is_active else DIM, 500 if is_active else 400, "middle")
    return h

def table(x, y, cols, rows, action_cells=None, label=None):
    """cols: list of (header, x_offset, align). rows: list of list[str].
    action_cells: optional list (per row) of callables(rx_right, ry)->None.
    Returns height consumed."""
    cy = y
    if label:
        # aria-label is invisible on real page; skip drawing, keep as layer name only
        pass
    header_h = 40
    # header
    for (htext, hx, align) in cols:
        anchor = "end" if align == "right" else "start"
        tx = x + hx
        text(tx, cy + 24, htext, 13, DIM, 600, anchor)
    cy += header_h
    line(x, cy, x + TABLE_W, cy, BORDER, 1)
    row_h = 44
    for ri, row in enumerate(rows):
        for (col, (htext, hx, align)) in zip(row, cols):
            anchor = "end" if align == "right" else "start"
            tx = x + hx
            text(tx, cy + 28, col, 14, TEXT, 400, anchor)
        if action_cells and ri < len(action_cells) and action_cells[ri]:
            action_cells[ri](x + TABLE_W, cy + 22)
        cy += row_h
        line(x, cy, x + TABLE_W, cy, BORDER, 1)
    return cy - y

# =============================================================================
# Canvas
# =============================================================================
CANVAS_W = 1540
CANVAS_H = 1280
emit(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
     f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="{FONT}">')
g_open("budget-details--dark")
rect(0, 0, CANVAS_W, CANVAS_H, BG)

# -----------------------------------------------------------------------------
# PAGE FRAME (content only)
# -----------------------------------------------------------------------------
PX, PY, PW, PH = 40, 40, 940, 1000
PAD = 32
CX = PX + PAD                 # content left
CR = PX + PW - PAD            # content right
TABLE_W = PW - 2*PAD          # full content width tables

g_open("page--budget-detail")
rect(PX, PY, PW, PH, SURFACE, rx=10, stroke=ELEV, sw=1)

# Back link
g_open("back-link")
text(CX, PY + 46, "← Back to budgets", 14, INDIGO_LINK, 400)
g_close()

# Title + Record button (Group space-between)
g_open("title-row")
text(CX, PY + 96, "test", 26, TEXT, 700)
bw = int(len("Record transaction") * char_w(14) + 36)
button(CR - bw, PY + 66, "Record transaction", "filled", "sm")
g_close()

# Date range
g_open("date-range")
text(CX, PY + 132, "2026-06-01 → 2026-06-29", 14, DIM, 400)
g_close()

# Budget totals: the 5 aggregate figures, grouped into a visible card placed
# directly under the budget name and period.
g_open("budget-totals")
CARD_Y = PY + 150
CARD_H = 88
rect(CX, CARD_Y, TABLE_W, CARD_H, ELEV, rx=10, stroke=BORDER, sw=1)
totals = [
    ("Planned income", "200.00"),
    ("Actual income", "1111.00"),
    ("Planned expense", "200.00"),
    ("Actual expense", "122.00"),
    ("Net", "989.00"),
]
tx = CX + 24
for lab, val in totals:
    text(tx, CARD_Y + 36, lab, 14, DIM, 400)
    text(tx, CARD_Y + 62, val, 16, TEXT, 500)
    tx += 165
g_close()

# Summary table: Planned vs actual by category
SUMMARY_TITLE_Y = CARD_Y + CARD_H + 28
SUMMARY_TABLE_Y = SUMMARY_TITLE_Y + 16
g_open("summary-table")
text(CX, SUMMARY_TITLE_Y, "Planned vs actual by category", 13, DIM, 600)
cols = [
    ("Category", 0, "left"),
    ("Kind", 240, "left"),
    ("Planned", TABLE_W - 130, "right"),
    ("Actual", TABLE_W, "right"),
]
rows = [
    ["test", "income", "200.00", "1111.00"],
    ["computer", "expense", "0.00", "11.00"],
    ["tettd", "expense", "0.00", "111.00"],
    ["test", "expense", "100.00", "0.00"],
    ["boots", "expense", "100.00", "0.00"],
]
table(CX, SUMMARY_TABLE_Y, cols, rows)
g_close()

# Allocation panel
g_open("allocation-panel")
ay = SUMMARY_TABLE_Y + 40 + 5*44 + 28
text(CX, ay, "Planned allocations", 18, TEXT, 700)
# buttons right-aligned: Apply template (default) + Add allocation (filled)
addw = int(len("Add allocation") * char_w(13) + 24)
button(CR - addw, ay - 22, "Add allocation", "filled", "xs")
appw = int(len("Apply template") * char_w(13) + 24)
button(CR - addw - appw - 10, ay - 22, "Apply template", "default", "xs")

acols = [
    ("Category", 0, "left"),
    ("Planned amount", 300, "left"),
]
arows = [
    ["test", "100.00"],
    ["test", "200.00"],
    ["boots", "100.00"],
]
def alloc_actions(rx_right, ry):
    # ✎ edit and × delete icon buttons, right aligned
    text(rx_right - 12, ry + 14, "×", 18, RED, 400, "middle")
    text(rx_right - 40, ry + 14, "✎", 15, INDIGO_SUB, 400, "middle")
table(CX, ay + 16, acols, arows, action_cells=[alloc_actions]*3)
g_close()

# Transactions table
g_open("transactions-table")
ttop = ay + 16 + 40 + 3*44 + 36
tcols = [
    ("Date", 0, "left"),
    ("Type", 150, "left"),
    ("Category", 300, "left"),
    ("Amount", TABLE_W - 150, "right"),
]
trows = [
    ["2026-06-01", "income", "test", "1111.00"],
    ["2026-06-03", "expense", "computer", "11.00"],
    ["2026-06-02", "expense", "tettd", "111.00"],
]
def txn_actions(rx_right, ry):
    button(rx_right - 60, ry - 4, "Delete", "subtle-red", "xs")
    button(rx_right - 110, ry - 4, "Edit", "subtle", "xs")
table(CX, ttop, tcols, trows, action_cells=[txn_actions]*3)
g_close()

g_close()  # page

# -----------------------------------------------------------------------------
# MODAL FRAMES (right column)
# -----------------------------------------------------------------------------
MX = PX + PW + 40
MW = 440
MPAD = 24
MCX = MX + MPAD
MCW = MW - 2*MPAD

def modal_frame(gid, y, title, body_height):
    total_h = 56 + body_height + MPAD
    g_open(gid)
    rect(MX, y, MW, total_h, ELEV, rx=10, stroke=BORDER, sw=1)
    text(MCX, y + 36, title, 18, TEXT, 600)
    line(MX, y + 52, MX + MW, y + 52, BORDER, 1)
    return y + 56, total_h

# Modal A: Record transaction
ya = 40
by, ha = modal_frame("modal--record-transaction", ya, "Record transaction", 300)
cy = by + 12
segmented(MCX, cy, MCW, ["Income", "Expense"]); cy += 36 + 20
cy += input_field(MCX, cy, MCW, "Amount", "0", placeholder=True)
cy += input_field(MCX, cy, MCW, "Date", "mm/dd/yyyy", placeholder=True)
cy += input_field(MCX, cy, MCW, "Category", "Choose a kind first", disabled=True)
button(MX + MW - MPAD - 70, by + 12 + 36 + 20 + 3*68 - 4, "Save", "filled", "sm")
g_close()

# Modal B: Add allocation
yb = ya + ha + 32
by, hb = modal_frame("modal--add-allocation", yb, "Add allocation", 260)
cy = by + 12
segmented(MCX, cy, MCW, ["Income", "Expense"]); cy += 36 + 20
cy += input_field(MCX, cy, MCW, "Category", "Choose a kind first", disabled=True)
cy += input_field(MCX, cy, MCW, "Planned amount", "0", placeholder=True)
# Cancel + Add (right)
addw = button(MX + MW - MPAD - 64, cy - 4, "Add", "filled", "sm")
button(MX + MW - MPAD - 64 - 90, cy - 4, "Cancel", "default", "sm")
g_close()

# Modal C: Apply template
yc = yb + hb + 32
by, hc = modal_frame("modal--apply-template", yc, "Apply template", 130)
cy = by + 12
cy += input_field(MCX, cy, MCW, "Template", "Pick a template", placeholder=True)
button(MX + MW - MPAD - 70, cy - 4, "Apply", "filled", "sm")
button(MX + MW - MPAD - 70 - 90, cy - 4, "Cancel", "default", "sm")
g_close()

# Modal D: Delete transaction
yd = yc + hc + 32
by, hd = modal_frame("modal--delete-transaction", yd, "Delete transaction", 90)
text(MCX, by + 32, "Delete this transaction?", 14, TEXT, 400)
delw = button(MX + MW - MPAD - 72, by + 50, "Delete", "filled", "sm")
# recolor delete as red: overpaint
# (simpler: draw a red filled button manually)
out.pop()  # remove last text of Delete label
out.pop()  # remove rect of delete button
rect(MX + MW - MPAD - 72, by + 50, 72, 36, RED_FILL, rx=6)
text(MX + MW - MPAD - 72 + 36, by + 50 + 23, "Delete", 14, WHITE, 600, "middle")
button(MX + MW - MPAD - 72 - 90, by + 50, "Cancel", "default", "sm")
g_close()

g_close()  # budget-details--dark
emit('</svg>')

svg = "\n".join(out)
with open(os.path.join(HERE, "budget_details.svg"), "w") as f:
    f.write(svg + "\n")
print("Wrote", len(svg), "bytes; canvas", CANVAS_W, "x", CANVAS_H)
