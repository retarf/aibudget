#!/usr/bin/env python3
"""Builders for the Budget Detail page content and its modals, drawn onto an
`Svg` from `_svglib`. Shared by the standalone page mockup
(`budget_details/gen.py`) and the whole-app shell mockup (`app_shell/gen.py`),
so the page stays identical across both.

Data reflects the live budget "test" (2026-06-01 → 2026-06-29)."""

from _svglib import (
    BORDER, DIM, ELEV, INDIGO_LINK, INDIGO_SUB, RED, SURFACE, TEXT, WHITE,
    char_w,
)

PAD = 32  # content padding inside the page surface


def page_surface_height():
    """Height of the page surface (top padding through content to bottom
    padding), independent of the surrounding chrome."""
    return 998


def draw_page(svg, px, py, pw):
    """Draw the budget-detail content onto `svg`. (px, py) is the top-left of
    the content *surface* (page card / paper) and `pw` its width; this routine
    draws only the content, not the surface rect. Returns the content bottom y."""
    cx = px + PAD                # content left
    cr = px + pw - PAD           # content right
    tw = pw - 2 * PAD            # full content / table width

    # Back link
    with svg.group("back-link"):
        svg.text(cx, py + 46, "← Back to budgets", 14, INDIGO_LINK, 400)

    # Title + Record button
    with svg.group("title-row"):
        svg.text(cx, py + 96, "test", 26, TEXT, 700)
        bw = int(len("Record transaction") * char_w(14) + 36)
        svg.button(cr - bw, py + 66, "Record transaction", "filled", "sm")

    # Date range
    with svg.group("date-range"):
        svg.text(cx, py + 132, "2026-06-01 → 2026-06-29", 14, DIM, 400)

    # Budget totals card (5 aggregate figures), under the name and period.
    with svg.group("budget-totals"):
        card_y = py + 150
        card_h = 88
        svg.rect(cx, card_y, tw, card_h, ELEV, rx=10, stroke=BORDER, sw=1)
        totals = [
            ("Planned income", "200.00"),
            ("Actual income", "1111.00"),
            ("Planned expense", "200.00"),
            ("Actual expense", "122.00"),
            ("Net", "989.00"),
        ]
        tx = cx + 24
        for lab, val in totals:
            svg.text(tx, card_y + 36, lab, 14, DIM, 400)
            svg.text(tx, card_y + 62, val, 16, TEXT, 500)
            tx += 165

    # Summary table: Planned vs actual by category
    summary_title_y = card_y + card_h + 28
    summary_table_y = summary_title_y + 16
    with svg.group("summary-table"):
        svg.text(cx, summary_title_y, "Planned vs actual by category", 13, DIM, 600)
        cols = [
            ("Category", 0, "left"),
            ("Planned", tw - 130, "right"),
            ("Actual", tw, "right"),
        ]
        rows = [
            ["test", "200.00", "1111.00"],
            ["computer", "0.00", "11.00"],
            ["tettd", "0.00", "111.00"],
            ["test", "100.00", "0.00"],
            ["boots", "100.00", "0.00"],
        ]
        row_kinds = ["income", "expense", "expense", "expense", "expense"]
        svg.table(cx, summary_table_y, tw, cols, rows, row_kinds=row_kinds)

    # Allocation panel
    with svg.group("allocation-panel"):
        ay = summary_table_y + 40 + 5 * 44 + 28
        svg.text(cx, ay, "Planned allocations", 18, TEXT, 700)
        addw = int(len("Add allocation") * char_w(13) + 24)
        svg.button(cr - addw, ay - 22, "Add allocation", "filled", "xs")
        appw = int(len("Apply template") * char_w(13) + 24)
        svg.button(cr - addw - appw - 10, ay - 22, "Apply template", "default", "xs")

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
            svg.text(rx_right - 12, ry + 14, "×", 18, RED, 400, "middle")
            svg.text(rx_right - 40, ry + 14, "✎", 15, INDIGO_SUB, 400, "middle")

        svg.table(cx, ay + 16, tw, acols, arows, action_cells=[alloc_actions] * 3)

    # Transactions table
    with svg.group("transactions-table"):
        ttop = ay + 16 + 40 + 3 * 44 + 36
        tcols = [
            ("Date", 0, "left"),
            ("Category", 200, "left"),
            ("Amount", tw - 150, "right"),
        ]
        trows = [
            ["2026-06-01", "test", "1111.00"],
            ["2026-06-03", "computer", "11.00"],
            ["2026-06-02", "tettd", "111.00"],
        ]
        ttypes = ["income", "expense", "expense"]

        def txn_actions(rx_right, ry):
            svg.button(rx_right - 60, ry - 4, "Delete", "subtle-red", "xs")
            svg.button(rx_right - 110, ry - 4, "Edit", "subtle", "xs")

        h = svg.table(cx, ttop, tw, tcols, trows,
                      action_cells=[txn_actions] * 3, row_kinds=ttypes)

    return ttop + h


def draw_modals(svg, mx, my, mw):
    """Draw the four budget-detail modals as stacked frames starting at (mx, my)
    with width mw. Returns the bottom y of the last frame."""
    mpad = 24
    mcx = mx + mpad
    mcw = mw - 2 * mpad

    def frame(gid, y, title, body_height):
        total_h = 56 + body_height + mpad
        svg.emit(f'<g id="{gid}">')
        svg.rect(mx, y, mw, total_h, ELEV, rx=10, stroke=BORDER, sw=1)
        svg.text(mcx, y + 36, title, 18, TEXT, 600)
        svg.line(mx, y + 52, mx + mw, y + 52, BORDER, 1)
        return y + 56, total_h

    # Record transaction
    ya = my
    by, ha = frame("modal--record-transaction", ya, "Record transaction", 300)
    cy = by + 12
    svg.segmented(mcx, cy, mcw, ["Income", "Expense"]); cy += 36 + 20
    cy += svg.input_field(mcx, cy, mcw, "Amount", "0", placeholder=True)
    cy += svg.input_field(mcx, cy, mcw, "Date", "mm/dd/yyyy", placeholder=True)
    cy += svg.input_field(mcx, cy, mcw, "Category", "Choose a kind first", disabled=True)
    svg.button(mx + mw - mpad - 70, by + 12 + 36 + 20 + 3*68 - 4, "Save", "filled", "sm")
    svg.emit('</g>')

    # Add allocation
    yb = ya + ha + 32
    by, hb = frame("modal--add-allocation", yb, "Add allocation", 260)
    cy = by + 12
    svg.segmented(mcx, cy, mcw, ["Income", "Expense"]); cy += 36 + 20
    cy += svg.input_field(mcx, cy, mcw, "Category", "Choose a kind first", disabled=True)
    cy += svg.input_field(mcx, cy, mcw, "Planned amount", "0", placeholder=True)
    svg.button(mx + mw - mpad - 64, cy - 4, "Add", "filled", "sm")
    svg.button(mx + mw - mpad - 64 - 90, cy - 4, "Cancel", "default", "sm")
    svg.emit('</g>')

    # Apply template
    yc = yb + hb + 32
    by, hc = frame("modal--apply-template", yc, "Apply template", 130)
    cy = by + 12
    cy += svg.input_field(mcx, cy, mcw, "Template", "Pick a template", placeholder=True)
    svg.button(mx + mw - mpad - 70, cy - 4, "Apply", "filled", "sm")
    svg.button(mx + mw - mpad - 70 - 90, cy - 4, "Cancel", "default", "sm")
    svg.emit('</g>')

    # Delete transaction
    yd = yc + hc + 32
    by, hd = frame("modal--delete-transaction", yd, "Delete transaction", 90)
    svg.text(mcx, by + 32, "Delete this transaction?", 14, TEXT, 400)
    svg.button(mx + mw - mpad - 72, by + 50, "Delete", "danger", "sm")
    svg.button(mx + mw - mpad - 72 - 90, by + 50, "Cancel", "default", "sm")
    svg.emit('</g>')

    return yd + hd
