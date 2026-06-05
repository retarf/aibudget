# app-shell Specification

## Purpose
TBD - created by archiving change frontend-ui. Update Purpose after archive.
## Requirements
### Requirement: Application shell layout
The application SHALL render a shell consisting of a persistent navigation
menu on the left side and a content area to its right.

#### Scenario: Shell is displayed
- **WHEN** the application loads
- **THEN** a navigation menu is shown on the left and the routed content is shown in the content area

### Requirement: Navigation menu
The navigation menu SHALL list the application's sections, and selecting an
item SHALL navigate to that section without a full page reload.

#### Scenario: Navigating to a section
- **WHEN** the user selects a navigation menu item
- **THEN** the content area displays that section and the browser URL updates

#### Scenario: Active section is indicated
- **WHEN** a section is displayed
- **THEN** its navigation menu item is visually marked as active

### Requirement: Unknown route handling
The application SHALL show a "not found" view when the user navigates to a
route that matches no section, with the shell still in place.

#### Scenario: Unknown route
- **WHEN** the user navigates to a URL that matches no section
- **THEN** a "not found" view is shown within the shell

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

