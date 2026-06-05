## Context

These decisions were worked out in the `design/` SVG mockups (`app_shell.svg`
and `budget_details/budget_details.svg`), which are layered, Figma/Inkscape-
importable renderings of the app in Mantine v9 dark. The current frontend
renders routed pages as a bare `Stack` directly inside `AppShell.Main` (no
elevated surface), and the budget detail view shows a `Kind`/`Type` column to
distinguish income from expense. The specs in this change describe the target
behavior; this document records the technical rationale.

## Goals / Non-Goals

**Goals:**
- Give routed content a distinct, raised surface over a darker app background.
- Convey income vs expense on the budget detail view without a dedicated
  column, while guaranteeing the distinction does not rely on color alone.
- Group the budget's aggregate totals into one panel under the budget identity.

**Non-Goals:**
- No backend, API, NATS, or data-model changes.
- No prescription of exact colors, border widths, shadow values, radii, or
  spacing — those are implementation detail and live in the mockups/theme.
- Not changing which figures the summary endpoint returns (see
  `budget-summary-enhanced`).

## Decisions

- **Elevated content surface (Mantine `Paper`) on a darker app background.**
  Wrap routed content in a `Paper` (rounded, bordered, lightly elevated) and
  set the app background a step darker than the body so the content reads as a
  raised panel. _Alternative considered:_ leave content flush on the body
  background — rejected because the page did not read as a distinct surface,
  especially once the header/navbar share the body color.

- **Dual income/expense cue, drop the type/kind column.** Indicate direction
  with a color wash plus a redundant non-color marker (an up/down arrow on the
  row). _Alternatives considered:_ color only — rejected, fails for colorblind
  users and in grayscale (the budget detail view can legitimately show two rows
  with the same category name, one income and one expense, distinguishable only
  by this cue); keep the text column — rejected as redundant once the cue
  exists.

- **Group aggregate totals beneath the budget name and period.** Present the
  totals as a single panel directly under the budget identity rather than a
  loose row above the transactions list, giving the detail view a clearer
  top-down reading order.

## Risks / Trade-offs

- **Red/green is the most common colorblind confusion** → mitigated by the
  mandatory non-color cue, which the spec enforces.
- **Darker-than-stock app background may surprise a future reader** ("why isn't
  the body Mantine's default body color?") → recorded here and in the
  app-shell spec as an intentional choice so the contrast with the Paper is
  preserved.
- **Specs are intentionally style-agnostic** → the precise look is pinned only
  in the `design/` mockups and the Mantine theme, not in the spec; the two must
  be kept in rough sync by hand.
