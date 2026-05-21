## ADDED Requirements

### Requirement: Default theme from OS preference
On first visit, the application SHALL use the operating system's color-scheme
preference to choose between the light and dark theme.

#### Scenario: OS prefers dark
- **WHEN** a first-time user whose OS prefers a dark color scheme opens the app
- **THEN** the application is displayed in the dark theme

#### Scenario: OS prefers light
- **WHEN** a first-time user whose OS prefers a light color scheme opens the app
- **THEN** the application is displayed in the light theme

### Requirement: Theme toggle
The application SHALL provide a visible control that switches between the
light and dark themes.

#### Scenario: Toggling the theme
- **WHEN** the user activates the theme toggle
- **THEN** the application immediately switches to the other theme

### Requirement: Theme persistence
The application SHALL remember the user's chosen theme and reapply it on the
next visit.

#### Scenario: Chosen theme persists
- **WHEN** a user who has chosen a theme reloads or revisits the app
- **THEN** the application is displayed in the previously chosen theme
