#!/usr/bin/env python3
"""Shared SVG drawing primitives and Mantine v9 dark tokens for the design
mockups. An `Svg` instance accumulates markup; the gen scripts compose scenes
from these primitives and the page builders in `page_budget_detail.py`.

Each logical block is wrapped in a named <g> so the SVG imports into Figma /
Inkscape as editable, movable layers."""

from contextlib import contextmanager
from html import escape

# --- Mantine v9 dark tokens ---------------------------------------------------
BG = "#1a1a1a"          # app canvas behind the chrome/paper (darker than body)
SURFACE = "#242424"     # paper / body / modal body (color-body, dark[7])
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
# income/expense row encoding: subtle full-row tint + colored arrow cue
INCOME_TINT = "#40c057"   # green[6]; applied at low opacity as a row wash
EXPENSE_TINT = "#fa5252"  # red[6]; applied at low opacity as a row wash
INCOME_ARROW = "#69db7c"  # green[4]; ↑ cue
EXPENSE_ARROW = "#ff8787"  # red[4]; ↓ cue
ROW_TINT_OPACITY = 0.14
FONT = "Inter, -apple-system, 'Segoe UI', Roboto, sans-serif"


def char_w(size):
    """Rough advance width per character at a given font size."""
    return size * 0.56


class Svg:
    """A minimal SVG document builder."""

    def __init__(self):
        self.parts = []

    def emit(self, s):
        self.parts.append(s)

    @contextmanager
    def group(self, gid):
        self.emit(f'<g id="{escape(gid)}">')
        yield
        self.emit('</g>')

    def rect(self, x, y, w, h, fill, rx=0, stroke=None, sw=1, opacity=None,
             filt=None):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{sw}"'
        if opacity is not None:
            s += f' opacity="{opacity}"'
        if filt:
            s += f' filter="url(#{filt})"'
        self.emit(s + '/>')

    def line(self, x1, y1, x2, y2, stroke, sw=1):
        self.emit(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                  f'stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=14, fill=TEXT, weight=400, anchor="start"):
        self.emit(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
                  f'font-weight="{weight}" fill="{fill}" '
                  f'text-anchor="{anchor}">{escape(s)}</text>')

    def button(self, x, y, label, kind="filled", size="sm"):
        """kind: filled | default | subtle | subtle-red | danger. Returns width."""
        h = 36 if size == "sm" else 28
        fs = 14 if size == "sm" else 13
        pad = 18 if size == "sm" else 12
        w = int(len(label) * char_w(fs) + pad * 2)
        if kind == "filled":
            self.rect(x, y, w, h, INDIGO, rx=6)
            self.text(x + w/2, y + h/2 + fs*0.35, label, fs, WHITE, 600, "middle")
        elif kind == "danger":
            self.rect(x, y, w, h, RED_FILL, rx=6)
            self.text(x + w/2, y + h/2 + fs*0.35, label, fs, WHITE, 600, "middle")
        elif kind == "default":
            self.rect(x, y, w, h, ELEV, rx=6, stroke=BORDER, sw=1)
            self.text(x + w/2, y + h/2 + fs*0.35, label, fs, TEXT, 500, "middle")
        elif kind == "subtle":
            self.text(x + w/2, y + h/2 + fs*0.35, label, fs, INDIGO_SUB, 500, "middle")
        elif kind == "subtle-red":
            self.text(x + w/2, y + h/2 + fs*0.35, label, fs, RED, 500, "middle")
        return w

    def input_field(self, x, y, w, label, value, placeholder=False, disabled=False):
        """Labelled input box. Returns total height consumed (label + box + gap)."""
        self.text(x, y, label, 13, TEXT, 500)
        by = y + 8
        bg = "#262626" if disabled else ELEV
        self.rect(x, by, w, 36, bg, rx=6, stroke=BORDER, sw=1)
        vfill = DIM if (placeholder or disabled) else TEXT
        self.text(x + 12, by + 23, value, 14, vfill)
        return 8 + 36 + 24

    def segmented(self, x, y, w, opts, active=None):
        h = 36
        self.rect(x, y, w, h, ELEV, rx=8)
        seg_w = w / len(opts)
        for i, opt in enumerate(opts):
            sx = x + i*seg_w
            is_active = (opt == active)
            if is_active:
                self.rect(sx+3, y+3, seg_w-6, h-6, BORDER, rx=6)
            self.text(sx + seg_w/2, y + h/2 + 5, opt, 14,
                      TEXT if is_active else DIM, 500 if is_active else 400, "middle")
        return h

    def table(self, x, y, width, cols, rows, action_cells=None, row_kinds=None):
        """cols: list of (header, x_offset, align). rows: list of list[str].
        width: full table width (for dividers and right-aligned columns).
        action_cells: optional list (per row) of callables(rx_right, ry)->None.
        row_kinds: optional list (per row) of "income"/"expense"/None. When set,
            the row gets a subtle green/red full-width tint and a colored ↑/↓
            cue prefixing the first cell.
        Returns height consumed."""
        cy = y
        header_h = 40
        arrow_indent = 22
        indent = arrow_indent if row_kinds else 0
        for (htext, hx, align) in cols:
            anchor = "end" if align == "right" else "start"
            tx = x + hx + (indent if hx == 0 and align != "right" else 0)
            self.text(tx, cy + 24, htext, 13, DIM, 600, anchor)
        cy += header_h
        self.line(x, cy, x + width, cy, BORDER, 1)
        row_h = 44
        for ri, row in enumerate(rows):
            kind = row_kinds[ri] if row_kinds and ri < len(row_kinds) else None
            if kind:
                tint = INCOME_TINT if kind == "income" else EXPENSE_TINT
                self.rect(x, cy, width, row_h, tint, opacity=ROW_TINT_OPACITY)
                arrow = "↑" if kind == "income" else "↓"
                acolor = INCOME_ARROW if kind == "income" else EXPENSE_ARROW
                self.text(x, cy + 28, arrow, 15, acolor, 700)
            for (col, (htext, hx, align)) in zip(row, cols):
                anchor = "end" if align == "right" else "start"
                tx = x + hx + (indent if hx == 0 and align != "right" else 0)
                self.text(tx, cy + 28, col, 14, TEXT, 400, anchor)
            if action_cells and ri < len(action_cells) and action_cells[ri]:
                action_cells[ri](x + width, cy + 22)
            cy += row_h
            self.line(x, cy, x + width, cy, BORDER, 1)
        return cy - y

    def render(self, width, height, defs=""):
        """Wrap accumulated parts in an <svg> document and return the string."""
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
                f'height="{height}" viewBox="0 0 {width} {height}" '
                f'font-family="{FONT}">')
        body = "\n".join(self.parts)
        return f"{head}\n{defs}{body}\n</svg>\n"


# A soft drop shadow for elevated surfaces (Mantine Paper shadow="sm"-ish).
SOFT_SHADOW_DEFS = (
    '<defs><filter id="paper-shadow" x="-20%" y="-20%" width="140%" height="140%">'
    '<feDropShadow dx="0" dy="6" stdDeviation="14" flood-color="#000000" '
    'flood-opacity="0.45"/></filter></defs>\n'
)
