---
version: alpha
name: "{{brand_name}}"
description: "{{brand_description}}"
colors:
  background: "{{background_color}}"
  surface: "{{surface_color}}"
  text: "{{text_color}}"
  muted_text: "{{muted_text_color}}"
  border: "{{border_color}}"
  primary_action: "{{primary_action_color}}"
  success: "{{success_color}}"
  warning: "{{warning_color}}"
  danger: "{{danger_color}}"
  info: "{{info_color}}"
typography:
  display:
    fontFamily: "{{display_font}}"
    fontSize: 48px
    fontWeight: 650
    lineHeight: 1.1
  title:
    fontFamily: "{{title_font}}"
    fontSize: 32px
    fontWeight: 650
    lineHeight: 1.2
  heading:
    fontFamily: "{{heading_font}}"
    fontSize: 24px
    fontWeight: 650
    lineHeight: 1.25
  body:
    fontFamily: "{{body_font}}"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  caption:
    fontFamily: "{{body_font}}"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "{{body_font}}"
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.3
rounded:
  sm: 4px
  md: 8px
  lg: 12px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
components:
  button_primary:
    backgroundColor: "{colors.primary_action}"
    textColor: "#FFFFFF"
    borderColor: "{colors.primary_action}"
    rounded: "{rounded.md}"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    borderColor: "{colors.border}"
    rounded: "{rounded.lg}"
---

# {{brand_name}} DESIGN.md

## Overview

{{overview}}

## Visual Theme

{{visual_theme}}

## Colors

{{colors_guidance}}

## Typography

{{typography_guidance}}

## Layout

{{layout_guidance}}

## Elevation & Depth

{{elevation_guidance}}

## Shapes

{{shapes_guidance}}

## Components

{{components_guidance}}

Required states: default, hover, pressed, disabled, focus, error, loading, success, empty, and unavailable where relevant.

## Responsive Behavior

{{responsive_guidance}}

## Motion & Feedback

{{motion_guidance}}

## Content Voice

{{content_voice}}

## Do's and Don'ts

{{dos_and_donts}}

## Reference Direction

Reference direction: `{{reference_direction_id}}` - {{reference_direction_name}}.

Use the direction as a mechanism reference only. Do not copy third-party brand assets, logos, proprietary fonts, screenshots, full color systems, or complete `DESIGN.md` files.

## Agent Guidance

{{agent_guidance}}
