## ADDED Requirements

### Requirement: Content area is an elevated surface

The application shell SHALL render the routed content on a surface that is
visually distinct from the application background and has rounded corners. The
application background SHALL be darker than the content surface so the content
reads as a raised panel rather than sitting flush with the background.

#### Scenario: Content sits on a distinct, raised surface

- **WHEN** the application loads a routed page
- **THEN** the page content is shown on a surface whose background differs from
  the (darker) application background and whose corners are rounded

#### Scenario: Surface separation persists across sections

- **WHEN** the user navigates between sections
- **THEN** each section's content continues to render on the elevated,
  rounded surface within the shell
