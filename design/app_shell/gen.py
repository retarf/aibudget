#!/usr/bin/env python3
"""Generate a whole-app SVG mockup (Mantine v9 dark): the AppShell chrome —
a 56px header and a 240px left navbar — wrapping the Budget Detail page, which
sits on an elevated Mantine Paper over the darker #1a1a1a app canvas.

Imports the shared primitives and page builder so the page matches the
standalone budget_details.svg. Run: python design/app_shell/gen.py"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # design/ on the path

from _svglib import (
    BG, BORDER, DIM, ELEV, INDIGO, INDIGO_SUB, SOFT_SHADOW_DEFS, SURFACE, TEXT,
    Svg,
)
from page_budget_detail import draw_page, page_surface_height

HEADER_H = 56
NAVBAR_W = 240
NAV_PAD = 16
MAIN_PAD = 16          # AppShell padding="md"
PAPER_W = 940          # same page width as the standalone mockup

PAPER_X = NAVBAR_W + MAIN_PAD
PAPER_Y = HEADER_H + MAIN_PAD
PAPER_H = page_surface_height()

CANVAS_W = PAPER_X + PAPER_W + MAIN_PAD          # 1212
CANVAS_H = PAPER_Y + PAPER_H + MAIN_PAD          # 1086

NAV_ITEMS = [
    ("Dashboard", False),
    ("Budgets", True),       # active for a budget detail route
    ("Categories", False),
    ("Templates", False),
    ("Reports", False),
]

svg = Svg()
with svg.group("app-shell--dark"):
    # App canvas (darker than the body, so the chrome and paper read as raised)
    svg.rect(0, 0, CANVAS_W, CANVAS_H, BG)

    # Header
    with svg.group("header"):
        svg.rect(0, 0, CANVAS_W, HEADER_H, SURFACE)
        svg.line(0, HEADER_H, CANVAS_W, HEADER_H, BORDER, 1)
        svg.text(24, 36, "aibudget", 20, TEXT, 700)
        # Theme toggle (ActionIcon, default variant)
        tx = CANVAS_W - 24 - 34
        svg.rect(tx, 11, 34, 34, ELEV, rx=6, stroke=BORDER, sw=1)
        svg.text(tx + 17, 33, "☾", 16, TEXT, 400, "middle")

    # Navbar
    with svg.group("navbar"):
        svg.rect(0, HEADER_H, NAVBAR_W, CANVAS_H - HEADER_H, SURFACE)
        svg.line(NAVBAR_W, HEADER_H, NAVBAR_W, CANVAS_H, BORDER, 1)
        link_x = NAV_PAD
        link_w = NAVBAR_W - 2 * NAV_PAD
        for i, (label, active) in enumerate(NAV_ITEMS):
            ly = HEADER_H + NAV_PAD + i * 42
            if active:
                svg.rect(link_x, ly, link_w, 38, INDIGO, rx=6, opacity=0.15)
            svg.text(link_x + 14, ly + 25, label, 14,
                     INDIGO_SUB if active else TEXT, 500 if active else 400)

    # Main: the budget detail page on an elevated Paper
    with svg.group("main"):
        with svg.group("paper--budget-detail"):
            svg.rect(PAPER_X, PAPER_Y, PAPER_W, PAPER_H, SURFACE, rx=10,
                     stroke=BORDER, sw=1, filt="paper-shadow")
            draw_page(svg, PAPER_X, PAPER_Y, PAPER_W)

out = svg.render(CANVAS_W, CANVAS_H, defs=SOFT_SHADOW_DEFS)
with open(os.path.join(HERE, "app_shell.svg"), "w") as f:
    f.write(out)
print("Wrote", len(out), "bytes; canvas", CANVAS_W, "x", CANVAS_H)
