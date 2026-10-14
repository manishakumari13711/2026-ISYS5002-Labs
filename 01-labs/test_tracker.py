"""Basic tests using only Python built-in unittest."""
import unittest
from datetime import date
from tempfile import TemporaryDirectory
from pathlib import Path
from tracker import add_task, read_tasks, save_tasks, days_until, upcoming, summary


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.tasks = []
        add_task(self.tasks, 'ISYS5002', 'Programming project', '2026-11-10', 'High')

    def test_add(self):
        self.assertEqual(len(self.tasks), 1)
        self.assertEqual(self.tasks[0]['status'], 'Not started')

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            add_task(self.tasks, 'Unit', 'Quiz', '2026-02-30', 'Low')

    def test_invalid_priority(self):
        with self.assertRaises(ValueError):
            add_task(self.tasks, 'Unit', 'Quiz', '2026-12-10', 'Urgent')

    def test_save_and_load(self):
        with TemporaryDirectory() as temp:
            file = Path(temp) / 'tasks.csv'
            save_tasks(file, self.tasks)
            self.assertEqual(read_tasks(file), self.tasks)

    def test_days_until(self):
        self.assertEqual(days_until('2026-11-10', date(2026, 11, 8)), 2)

    def test_upcoming_excludes_completed(self):
        self.tasks[0]['status'] = 'Completed'
        self.assertEqual(upcoming(self.tasks), [])

    def test_summary(self):
        self.tasks[0]['status'] = 'Completed'
        self.tasks[0]['hours_spent'] = '2.5'
        self.assertEqual(summary(self.tasks), (1, 1, 2.5, 100.0))


if __name__ == '__main__':
    unittest.main()
