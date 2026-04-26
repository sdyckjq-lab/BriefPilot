# DESIGN.md Review

Mode: briefpilot_fallback

Blocking: false

Reference direction: enterprise_data_workspace

Source SHA-256: 91ec3856e75d78446680917497eef94bb5f9ff7e11436ec9d3de68a1447d2207

Severity counts:

- blocking: 0
- warning: 2
- info: 1

Next action: continue

Official tool:

- available: false
- command: 
- merged: false

## Findings

- warning [missing_accessibility_guidance] Markdown body: Accessibility guidance does not mention touch. Fix: Add explicit accessibility guidance.
- warning [reference_direction_drift] drift_checks.data_density: Workspace direction should define scan density, panels, rows, or metadata hierarchy. Fix: Add guidance that matches the selected reference direction, or choose a better direction.
- info [optional_official_check] official_tool: Google official DESIGN.md lint was not run; fallback checks were used. Fix: For stricter checks, provide a safe absolute --official-command path or run the official tool manually.
