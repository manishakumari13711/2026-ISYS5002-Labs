import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

from student_tracker import AssessmentTracker, FIELDS, number, valid_date, validate_records


def record(**changes):
    row = dict(unit='ISYS5002', assessment='Project', due_date='2026-11-04',
               weight='40', total_marks='30', marks_obtained='')
    row.update(changes)
    return row


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'assessments.csv'
        self.tracker = AssessmentTracker(self.path)
        self.output = io.StringIO()
        self.capture = redirect_stdout(self.output)
        self.capture.__enter__()
        self.addCleanup(self.capture.__exit__, None, None, None)

    def write_csv(self, rows):
        with self.path.open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def test_missing_file_is_empty(self):
        self.assertEqual(self.tracker.assessments, [])
        self.assertIsNone(self.tracker.load_error)

    def test_save_and_reload(self):
        self.assertTrue(self.tracker.save_assessments([record()]))
        self.assertEqual(AssessmentTracker(self.path).assessments, [record()])

    def test_weighted_grade(self):
        self.tracker.save_assessments([record(marks_obtained='25')])
        _, earned, graded = self.tracker.grade_summary(' isys5002 ')
        self.assertAlmostEqual(earned, 33.3333333333)
        self.assertEqual(graded, 40)

    def test_zero_mark_is_graded(self):
        self.tracker.save_assessments([record(marks_obtained='0')])
        self.assertEqual(self.tracker.grade_summary('ISYS5002')[2], 40)
        self.assertEqual(self.tracker.deadline_rows(), [])

    def test_invalid_numbers(self):
        for value in ['nan', 'inf', '-inf', 'abc', '-1', '101']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                number(value, 0, 100)

    def test_dates(self):
        self.assertEqual(valid_date('2028-02-29'), date(2028, 2, 29))
        for value in ['2026-02-29', '2026-1-01', '04/11/2026']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                valid_date(value)

    def test_invalid_records(self):
        for changes in [dict(unit=' '), dict(assessment=''), dict(total_marks='0'),
                        dict(weight='nan'), dict(marks_obtained='31'),
                        dict(due_date='not a date'), dict(total_marks=None)]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_records([record(**changes)])

    def test_weight_limit(self):
        with self.assertRaises(ValueError):
            validate_records([record(weight='60'), record(unit='isys5002', weight='41')])
        validate_records([record(weight='60'), record(weight='40')])

    def test_bad_headers_block_save(self):
        self.path.write_text('wrong,headings\nx,y\n', encoding='utf-8')
        old = self.path.read_bytes()
        tracker = AssessmentTracker(self.path)
        self.assertIsNotNone(tracker.load_error)
        self.assertFalse(tracker.save_assessments([record()]))
        self.assertEqual(self.path.read_bytes(), old)

    def test_bad_row_blocks_load(self):
        self.write_csv([record(total_marks='0')])
        tracker = AssessmentTracker(self.path)
        self.assertIsNotNone(tracker.load_error)
        self.assertEqual(tracker.assessments, [])

    def test_failed_save_preserves_memory_and_disk(self):
        self.tracker.save_assessments([record()])
        original = self.path.read_bytes()
        with patch('student_tracker.os.replace', side_effect=PermissionError('Read only')):
            self.assertFalse(self.tracker.save_assessments([record(assessment='Changed')]))
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(self.tracker.assessments, [record()])
        self.assertEqual(list(self.path.parent.glob('.tracker-*')), [])

    def test_deadline_order_and_graded_exclusion(self):
        self.tracker.save_assessments([
            record(due_date='2026-11-05', weight='20'),
            record(due_date='2026-11-03', weight='20'),
            record(due_date='2026-11-04', weight='20'),
            record(due_date='2026-11-02', weight='20', marks_obtained='0')])
        self.assertEqual([days for days, _ in self.tracker.deadline_rows(date(2026, 11, 4))], [-1, 0, 1])

    def test_add_via_prompts(self):
        with patch('builtins.input', side_effect=['ISYS5002', 'Project', '2026-11-04', '40', '30']):
            self.tracker.add_assessment()
        self.assertEqual(self.tracker.assessments, [record(weight='40.0', total_marks='30.0')])

    def test_edit_excludes_old_weight(self):
        self.tracker.save_assessments([record(weight='100')])
        with patch('builtins.input', side_effect=['1', 'ISYS5002', 'Updated', '2026-11-05', '100', '30', 'YES']):
            self.tracker.edit_assessment()
        self.assertEqual(self.tracker.assessments[0]['assessment'], 'Updated')
        self.assertEqual(float(self.tracker.assessments[0]['weight']), 100)

    def test_edit_rejects_total_below_recorded_mark(self):
        self.tracker.save_assessments([record(marks_obtained='25')])
        with patch('builtins.input', side_effect=['1', 'ISYS5002', 'Updated', '2026-11-04', '40', '20', '30', 'YES']):
            self.tracker.edit_assessment()
        self.assertEqual(float(self.tracker.assessments[0]['total_marks']), 30)
        self.assertIn('Enter a finite number', self.output.getvalue())

    def test_cancel_edit(self):
        self.tracker.save_assessments([record()])
        with patch('builtins.input', side_effect=['1', 'ISYS5002', 'Updated', '2026-11-04', '40', '30', 'NO']):
            self.tracker.edit_assessment()
        self.assertEqual(self.tracker.assessments, [record()])

    def test_record_mark_and_delete(self):
        self.tracker.save_assessments([record()])
        with patch('builtins.input', side_effect=['1', '25']):
            self.tracker.record_mark()
        self.assertEqual(self.tracker.assessments[0]['marks_obtained'], '25.0')
        with patch('builtins.input', side_effect=['1', 'YES']):
            self.tracker.delete_assessment()
        self.assertEqual(AssessmentTracker(self.path).assessments, [])

    def test_target_calculation(self):
        self.tracker.save_assessments([record(marks_obtained='25')])
        with patch('builtins.input', side_effect=['ISYS5002', '50']):
            self.tracker.calculate_grades()
        self.assertIn('27.78%', self.output.getvalue())
        self.assertIn('Not all unit weighting', self.output.getvalue())

    def test_full_weight_graded(self):
        self.tracker.save_assessments([record(weight='100', marks_obtained='15')])
        with patch('builtins.input', side_effect=['ISYS5002']):
            self.tracker.calculate_grades()
        self.assertIn('50.00%', self.output.getvalue())

    def test_menu_exit(self):
        with patch('builtins.input', side_effect=['8']):
            self.tracker.run()
        self.assertIn('Goodbye!', self.output.getvalue())


if __name__ == '__main__':
    unittest.main(verbosity=2)
