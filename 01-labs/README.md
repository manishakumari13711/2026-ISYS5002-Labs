# AI Assistance Records — ISYS5002 Project

**Project:** Student Study & Assessment Tracker  
**Student:** Manisha Kumari  
**Student ID:** 23834101  
**AI tool:** ChatGPT (OpenAI)

## Declaration

I used ChatGPT to help plan and develop my Student Study & Assessment Tracker, understand Python programming concepts, review and debug code, and prepare project documentation. I am responsible for reviewing, understanding, testing, and submitting my work. AI assistance is also declared on my assignment cover page.

## Assistance summary

This is a **summary** of known interactions, not a verbatim transcript. Dates reflect conversations available in our project history. Attach the original conversations separately where required by the assignment's AI recordkeeping specification.

| Date | Area | What I asked ChatGPT to help with | What assistance was provided | What I should verify or do myself |
|---|---|---|---|---|
| 2026-10-07 | Project idea | Develop a Student Study & Assessment Tracker | Proposed an assessment tracker with units, deadlines, marks, grade calculations and targets | Explain why this idea is useful to me |
| 2026-10-07 to 2026-10-11 | Python development | Build the program step by step and combine features into a complete program | Helped with menu-based Python design, CSV storage, input validation and calculations | Understand and test every function |
| 2026-10-11 to 2026-10-13 | Code explanation | Explain the assessment tracker code in simple English | Explained functions and Python concepts used by the program | Practise explaining the code independently |
| 2026-10-13 | Code review | Review the shared complete program | Identified a syntax error where `def upcoming_assessments(...)` appeared on the same line as a `print(...)` statement | Correct the line break and run the program |
| 2026-10-13 | Documentation | Create a simple project idea explanation and assignment documentation | Helped draft the project rationale, features, usage and documentation | Edit wording to match my actual experience and tests |
| 2026-10-13 | AI recordkeeping | Prepare an AI assistance record for GitHub | Created this summary and a transcript collection template | Add complete authentic chat exports and relevant commit references |

## Program functions discussed

- `load_assessments()` — reads saved assessment records from `assessments.csv`.
- `save_assessments()` — writes assessment records to the CSV file.
- `get_number()` — validates decimal number input within a range.
- `get_integer()` — validates whole-number menu and selection input.
- `get_date()` — checks that a due date follows `YYYY-MM-DD` and is valid.
- `add_assessment()` — creates an assessment and limits total unit weighting to 100%.
- `view_assessments()` — displays recorded assessments.
- `record_mark()` — saves a mark for a selected assessment.
- `calculate_grades()` — calculates weighted points, graded average and target-grade requirements.
- `upcoming_assessments()` — lists ungraded assessments due today or later.
- `delete_assessment()` — deletes an assessment after confirmation.
- `main()` — runs the seven-option menu until exit.

## Important accuracy notes

1. This file does **not** reproduce every message or exact prompt from the original conversations.
2. Do **not** present reconstructed summaries as full transcripts.
3. If the assignment requires prompt/response logs, save or export the original conversations and add them to this folder, without changing their content.
4. If the assignment requires AI-related Git commit references, add the real commit IDs from your repository; do not invent them.
5. The program code pasted on 2026-10-13 contained a syntax error joining the end of `calculate_grades()` and the start of `upcoming_assessments()`. Check that the submitted file has been corrected and tested.

## Suggested folder contents

```text
02-project/
  README.md
  <your Python source file>
  ai-assistance-logs/
    README.md
    AI_ASSISTANCE_SUMMARY.md
    TRANSCRIPT_CHECKLIST.md
    <original chat exports, as required>
```

**Note:** Check the assignment's official recordkeeping specification for exact required filenames, formatting and commit practices. This package is a starting point, not a substitute for the original records.
