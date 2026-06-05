#!/usr/bin/env python3
"""Generate a high-fidelity, layered SVG mockup of the Budget Detail page
(Mantine v9 dark): the resting page on the left and its four modals as frames
on the right. Imports the shared primitives and page builders so the page
stays in sync with the whole-app mockup.

Run: python design/budget_details/gen.py"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # design/ on the path

from _svglib import BG, ELEV, SURFACE, Svg
from page_budget_detail import draw_modals, draw_page, page_surface_height

CANVAS_W = 1540
CANVAS_H = 1280

# Page surface (content only)
PX, PY, PW = 40, 40, 940
PH = page_surface_height()

svg = Svg()
with svg.group("budget-details--dark"):
    svg.rect(0, 0, CANVAS_W, CANVAS_H, BG)

    with svg.group("page--budget-detail"):
        svg.rect(PX, PY, PW, PH, SURFACE, rx=10, stroke=ELEV, sw=1)
        draw_page(svg, PX, PY, PW)

    # Modal frames stacked in a right-hand column.
    draw_modals(svg, PX + PW + 40, 40, 440)

out = svg.render(CANVAS_W, CANVAS_H)
with open(os.path.join(HERE, "budget_details.svg"), "w") as f:
    f.write(out)
print("Wrote", len(out), "bytes; canvas", CANVAS_W, "x", CANVAS_H)
