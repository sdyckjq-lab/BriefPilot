# DESIGN.md Review

Mode: briefpilot_fallback

Blocking: false

Reference direction: ai_product_landing_page

Source SHA-256: 20b652a0287808bf8acf32aafeea73d2a536d2990b4922031971e6aedb78387e

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
- warning [reference_direction_drift] drift_checks.product_proof: Landing direction should mention product surface proof, screenshot, mock, or demo. Fix: Add guidance that matches the selected reference direction, or choose a better direction.
- info [optional_official_check] official_tool: Google official DESIGN.md lint was not run; fallback checks were used. Fix: For stricter checks, provide a safe absolute --official-command path or run the official tool manually.
