---
name: competence50-course-builder
description: >-
  Scaffolds, manages, or validates the 5-module Competence 5.0 course structure
  with the 3 content lanes (Preparation, During Training, Between Trainings) and
  knowledge test access restrictions. Use when updating course content models or completion gating.
---

# Competence 5.0 Course Builder & Validator

This skill guides the creation, maintenance, and structural validation of Competence 5.0 courses conforming to the BRD specification.

## Core Rules

1. **Course Structure**:
   - Section 1: Module 1 (Foundations)
   - Section 2: Module 2 (Agile Transformation & Industry 5.0)
   - Section 3: Module 3 (Data-Driven Decision Making)
   - Section 4: Module 4 (Sustainable Process Innovation)
   - Section 5: Module 5 (Leadership & Scaling)
   - Section 6: Final Assessment & Knowledge Test

2. **Every Module (Sections 1–5) Must Include 3 Content Lanes**:
   - **Lane 1: Preparation (Pre-work)**: Self-paced reading/videos + estimated time badge.
   - **Lane 2: During Training**: Live slides, discussion prompts, interactive workshop tasks.
   - **Lane 3: Between Trainings**: Workplace reflection task, team implementation canvas.

3. **Knowledge Test Gating**:
   - Activity completion tracking (`enablecompletion = 1`) enabled on all modules.
   - Quiz access restriction must depend on completion of all 5 modules.
   - Passing threshold set to 70%.

## Automation Script

To programmatically provision or reset the course template:

```bash
docker compose exec web php public/local/esf_export/cli/setup_c50_course.php
```
