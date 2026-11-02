# Student Study & Assessment Tracker

AI-assisted revision of the function-based code supplied in chat. Review, understand and adapt it before using it for your assessment. No third-party packages are required.

## Run
1. Install Python 3.9 or newer.
2. Extract this ZIP into a folder you can write to.
3. Open a terminal in the extracted folder.
4. Run `python student_tracker.py` (or `python3 student_tracker.py`).

The menu offers: add, view, record marks, calculate grades and targets, show deadlines, delete, edit, and exit. Each successful change saves immediately. Edit asks for replacement details and keeps the recorded mark; type YES to confirm. Edit cancellation leaves the original record unchanged.

## Existing data and backups
Back up your original assessments.csv before trying the revised program. Place a copy beside student_tracker.py to load your existing records. The six CSV column headings are unchanged:
`unit,assessment,due_date,weight,total_marks,marks_obtained`
The CSV is stored beside the Python script, not in the terminal's current directory. If there is no CSV, the first successful change creates it. Invalid or unreadable data stops the application and blocks saving; repair or restore the file and restart. Never delete your only copy while troubleshooting.

Temporary-file replacement reduces partial-write risk; it is not a versioned backup system. Keep separate backups. Use one running instance at a time; concurrent edits are not supported. Files are plain text and not encrypted.

## Example calculation
A mark of 25/30 on an assessment worth 40% contributes `(25 / 30) * 40 = 33.33` percentage points to the unit.
To reach 50% overall, the remaining 60% would require approximately 27.78% on average.
The average on graded work is 83.33%; this differs from weighted points earned.

Target estimates assume a unit weighted to 100%. If assessments are missing, the calculation explicitly assumes that unrecorded weighting remains available. Separate hurdle requirements, late penalties and institution-specific rounding rules are not modelled. Consult official unit results for your final grade.

Deadlines show ungraded records sorted by due date, including past dates. Ungraded does not necessarily mean unsubmitted. Dates use your computer's local date and do not track submission time or time zones. Due dates must use YYYY-MM-DD.

## Tests
Run `python -m unittest -v` (or `python3 -m unittest -v`) from this folder.
Tests use temporary directories and do not modify your assessments.csv. The suite checks calculations, date and number validation, CSV errors, failed-save preservation, add/edit/mark/delete operations, deadline order and menu exit.

## Mapping to the eight planned issues
These numbers refer to our proposed issue list, not actual GitHub issue numbers.

| Planned issue | Implementation |
| --- | --- |
| 1. Syntax/startup | Correct Python formatting and runnable main entry point |
| 2. Upcoming deadlines | deadline_rows and upcoming_assessments methods |
| 3. OOP refactoring | AssessmentTracker class with instance data and methods |
| 4. Quality assurance | test_student_tracker.py automated test suite |
| 5. Edit assessment | edit_assessment and shared input validation |
| 6. CSV validation | validate_records and strict CSV loading |
| 7. Save/load protection | load-error blocking, temporary writes and memory updates after save |
| 8. README improvements | This file |

## Understanding the code
- `self` refers to the current tracker object.
- `self.assessments` holds the records currently accepted by the program.
- `proposed` is a separate list of changes awaiting a successful save.
- `validate_records` checks file contents and proposed changes.
- `os.replace` replaces the CSV only after writing a complete temporary file.
- `grade_summary` performs calculations separately from interactive input.
- The action dictionary connects menu numbers to methods.
- The lambda in deadline_rows selects the day count as the sorting key.

## Assessment and AI record keeping
This code, tests and documentation were generated with ChatGPT assistance. They are not evidence of independently authored work. Save the full relevant prompts and responses in ai-assistance-logs according to your unit's record-keeping specification; this README is not a substitute for those logs. Include this revision and the issue-drafting conversation in that record. No complete AI log is included in this package.

The package does not create GitHub issues, commits, a cover page or a video. Use your official repository. Do not invent a development history or label AI-generated changes human-only. Carry out the required initial human-only project-copy step yourself, then study, test and adapt improvements in manageable steps, using real issue numbers in commits and including corresponding AI records. You must be able to explain submitted changes.
