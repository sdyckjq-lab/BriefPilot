# Brief Schema

## Markdown Brief Sections

Every Markdown brief must contain:

1. Project overview
2. Brief diagnosis
3. Target audience
4. Business goal
5. Design goal
6. Core message
7. Required structure
8. Visual direction
9. Strategy options
10. Brand context
11. DESIGN.md reference
12. Asset list
13. Interaction requirements
14. Constraints
15. Forbidden directions
16. Success criteria
17. Open questions
18. Assumptions

## JSON Brief Shape

Use this shape:

```json
{
  "meta": {
    "version": "0.1",
    "created_by": "BriefPilot",
    "target_tools": []
  },
  "project": {
    "name": "",
    "summary": "",
    "task_type": "",
    "stage": ""
  },
  "diagnosis": {
    "raw_request": "",
    "initial_score": 0,
    "level": "",
    "main_gaps": [],
    "recommended_mode": "",
    "risk": []
  },
  "audience": {
    "primary_user": "",
    "secondary_user": "",
    "context_of_use": "",
    "pain_points": [],
    "jobs_to_be_done": []
  },
  "goals": {
    "business_goal": "",
    "design_goal": "",
    "conversion_goal": "",
    "primary_cta": "",
    "secondary_cta": ""
  },
  "message": {
    "core_claim": "",
    "supporting_points": [],
    "proof_points": [],
    "content_warnings": []
  },
  "structure": {
    "sections": [],
    "screens": [],
    "flows": [],
    "section_details": [],
    "interaction_states": [],
    "interaction_contract": [],
    "responsive_accessibility": []
  },
  "visual": {
    "strategy_name": "",
    "tone_keywords": [],
    "references": [],
    "differentiators": [],
    "avoid": []
  },
  "strategy_options": [],
  "brand": {
    "brand_name": "",
    "logo": "",
    "colors": [],
    "typography": [],
    "voice": "",
    "existing_assets": []
  },
  "design_system": {
    "design_md_path": "",
    "reference_direction": {
      "id": "",
      "name": "",
      "source_boundary": ""
    },
    "token_summary": [],
    "assumptions": []
  },
  "constraints": {
    "platform": "",
    "responsive": true,
    "tech_stack": [],
    "accessibility": [],
    "deadline": ""
  },
  "quality_bar": {
    "must_have": [],
    "must_avoid": [],
    "review_criteria": []
  },
  "assumptions": [],
  "open_questions": []
}
```
