"""Student Study & Assessment Tracker. AI-assisted revision; see README.md."""
import csv
import math
import os
import tempfile
from datetime import date, datetime
from pathlib import Path

FIELDS = ['unit', 'assessment', 'due_date', 'weight', 'total_marks', 'marks_obtained']
DATA_FILE = Path(__file__).with_name('assessments.csv')


def valid_date(value):
    parsed = datetime.strptime(value, '%Y-%m-%d').date()
    if parsed.isoformat() != value:
        raise ValueError('Use YYYY-MM-DD, including leading zeros.')
    return parsed


def number(value, minimum, maximum):
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ValueError(f'Enter a finite number from {minimum} to {maximum}.')
    return result


def validate_records(records):
    """Validate the complete proposed file before accepting any changes."""
    totals = {}
    for row_number, row in enumerate(records, start=2):
        try:
            if set(row) != set(FIELDS) or any(row[key] is None for key in FIELDS):
                raise ValueError('Missing or extra CSV fields.')
            if not row['unit'].strip() or not row['assessment'].strip():
                raise ValueError('Unit and assessment cannot be blank.')
            valid_date(row['due_date'])
            weight = number(row['weight'], 0.01, 100)
            total = number(row['total_marks'], 0.01, 1000000)
            if row['marks_obtained'] != '':
                number(row['marks_obtained'], 0, total)
            unit = row['unit'].strip().casefold()
            totals[unit] = totals.get(unit, 0) + weight
            if totals[unit] > 100 + 0.000000001:
                raise ValueError('Unit weighting exceeds 100%.')
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError(f'CSV row {row_number}: {error}') from error


def get_number(prompt, minimum, maximum):
    while True:
        try:
            return number(input(prompt).strip(), minimum, maximum)
        except ValueError as error:
            print(error)


def get_integer(prompt, minimum, maximum):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if minimum <= value <= maximum:
                return value
        except ValueError:
            pass
        print(f'Enter a whole number from {minimum} to {maximum}.')


def get_date():
    while True:
        value = input('Due date (YYYY-MM-DD): ').strip()
        try:
            valid_date(value)
            return value
        except ValueError:
            print('Enter a real date using YYYY-MM-DD.')


class AssessmentTracker:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = Path(data_file)
        self.assessments = []
        self.load_error = None
        self.load_assessments()

    def load_assessments(self):
        self.load_error = None
        try:
            with self.data_file.open('r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file, strict=True)
                if reader.fieldnames != FIELDS:
                    raise ValueError('CSV headings do not match the tracker.')
                records = list(reader)
            validate_records(records)
            self.assessments = records
        except FileNotFoundError:
            # A broken symbolic link is not a genuinely new data file.
            if self.data_file.is_symlink():
                self.load_error = 'Data file is a broken symbolic link.'
            else:
                self.assessments = []
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            self.load_error = str(error)
        if self.load_error:
            print('Could not load assessments:', self.load_error)
            print('Saving is blocked. Repair or restore the CSV, then restart.')

    def save_assessments(self, proposed):
        """Write a temporary file first; update memory only after replacement."""
        if self.load_error:
            print('Saving blocked because the data file could not be loaded.')
            return False
        temporary = None
        try:
            validate_records(proposed)
            with tempfile.NamedTemporaryFile(mode='w', newline='', encoding='utf-8',
                                             dir=self.data_file.parent, delete=False,
                                             prefix='.tracker-', suffix='.tmp') as file:
                temporary = file.name
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(proposed)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.data_file)
            self.assessments = [row.copy() for row in proposed]
            return True
        except (OSError, ValueError, TypeError, csv.Error) as error:
            print('Could not save assessments:', error)
            return False
        finally:
            if temporary and os.path.exists(temporary):
                try:
                    os.unlink(temporary)
                except OSError:
                    pass

    def view_assessments(self):
        if not self.assessments:
            print('No assessments recorded.')
        for index, row in enumerate(self.assessments, start=1):
            mark = row['marks_obtained']
            result = 'Not graded' if mark == '' else f"{mark}/{row['total_marks']}"
            print(f"{index}. {row['unit']} | {row['assessment']} | Due: {row['due_date']} | "
                  f"Weight: {row['weight']}% | Mark: {result}")

    def choose_assessment(self):
        if not self.assessments:
            print('Add an assessment first.')
            return None
        self.view_assessments()
        return get_integer('Assessment number: ', 1, len(self.assessments)) - 1

    def read_assessment(self, exclude_index=None):
        unit = input('Unit code/name: ').strip()
        name = input('Assessment name: ').strip()
        if not unit or not name:
            print('Unit and assessment names cannot be blank.')
            return None
        used = sum(float(row['weight']) for i, row in enumerate(self.assessments)
                   if i != exclude_index and row['unit'].strip().casefold() == unit.casefold())
        available = 100 - used
        if available < 0.01:
            print('This unit has no available assessment weighting.')
            return None
        due = get_date()
        weight = get_number('Assessment weight (%): ', 0.01, available)
        minimum_total = 0.01
        mark = ''
        if exclude_index is not None:
            mark = self.assessments[exclude_index]['marks_obtained']
            if mark != '':
                minimum_total = max(minimum_total, float(mark))
        total = get_number('Total possible marks: ', minimum_total, 1000000)
        return dict(unit=unit, assessment=name, due_date=due, weight=str(weight),
                    total_marks=str(total), marks_obtained=mark)

    def add_assessment(self):
        row = self.read_assessment()
        if row and self.save_assessments(self.assessments + [row]):
            print('Assessment saved.')

    def edit_assessment(self):
        index = self.choose_assessment()
        if index is None:
            return
        print('Enter replacement details. The existing recorded mark is kept.')
        row = self.read_assessment(exclude_index=index)
        if row is None:
            return
        if input('Type YES to save these changes: ').strip() != 'YES':
            print('Edit cancelled.')
            return
        proposed = [item.copy() for item in self.assessments]
        proposed[index] = row
        if self.save_assessments(proposed):
            print('Assessment updated.')

    def record_mark(self):
        index = self.choose_assessment()
        if index is None:
            return
        total = float(self.assessments[index]['total_marks'])
        mark = get_number('Marks obtained: ', 0, total)
        proposed = [row.copy() for row in self.assessments]
        proposed[index]['marks_obtained'] = str(mark)
        if self.save_assessments(proposed):
            print('Mark saved.')

    def grade_summary(self, unit):
        matching = [row for row in self.assessments
                    if row['unit'].strip().casefold() == unit.strip().casefold()]
        earned = 0.0
        graded_weight = 0.0
        for row in matching:
            if row['marks_obtained'] != '':
                weight = float(row['weight'])
                earned += float(row['marks_obtained']) / float(row['total_marks']) * weight
                graded_weight += weight
        return matching, earned, graded_weight

    def calculate_grades(self):
        unit = input('Enter unit code/name: ').strip()
        matching, earned, graded_weight = self.grade_summary(unit)
        if not matching:
            print('No assessments for that unit.')
            return
        for row in matching:
            if row['marks_obtained'] != '':
                points = float(row['marks_obtained']) / float(row['total_marks']) * float(row['weight'])
                print(f"{row['assessment']}: {points:.2f} percentage points")
        print(f'Weighted points earned: {earned:.2f} / 100')
        print(f'Graded weighting: {graded_weight:.2f}%')
        if graded_weight:
            print(f'Average on graded work: {earned / graded_weight * 100:.2f}%')
        else:
            print('No marks have been entered yet.')
        remaining = 100 - graded_weight
        if remaining <= 0.000000001:
            print(f'All weighting graded; final calculated result: {earned:.2f}%')
            return
        target = get_number('Target final grade (%): ', 0, 100)
        required = (target - earned) / remaining * 100
        if required > 100 + 0.000000001:
            print('Target is not achievable with the remaining weighting.')
        elif required <= 0:
            print('Target already secured based on recorded results.')
        else:
            print(f'Average needed on remaining {remaining:.2f}% weighting: {required:.2f}%')
        if sum(float(row['weight']) for row in matching) < 100 - 0.000000001:
            print('Not all unit weighting is recorded; target assumes a 100%-weighted unit.')
        print('This estimate does not account for separate hurdle requirements.')

    def deadline_rows(self, today=None):
        today = today if today is not None else date.today()
        rows = []
        for row in self.assessments:
            if row['marks_obtained'] == '':
                days = (valid_date(row['due_date']) - today).days
                rows.append((days, row))
        return sorted(rows, key=lambda item: item[0])

    def upcoming_assessments(self):
        rows = self.deadline_rows()
        if not rows:
            print('No ungraded assessments to display.')
        for days, row in rows:
            if days < 0:
                status = f'Overdue by {abs(days)} day(s)'
            elif days == 0:
                status = 'Due today'
            else:
                status = f'Due in {days} day(s)'
            print(f"{row['unit']} | {row['assessment']} | {row['due_date']} | {status}")
        if rows:
            print('Ungraded does not necessarily mean unsubmitted; check your submission records.')

    def delete_assessment(self):
        index = self.choose_assessment()
        if index is None:
            return
        if input('Type YES to confirm deletion: ').strip() != 'YES':
            print('Deletion cancelled.')
            return
        proposed = [row.copy() for row in self.assessments]
        removed = proposed.pop(index)
        if self.save_assessments(proposed):
            print('Deleted:', removed['assessment'])

    def run(self):
        if self.load_error:
            return
        while True:
            print('\n--- STUDENT STUDY & ASSESSMENT TRACKER ---')
            print('1. Add assessment\n2. View assessments\n3. Record a mark')
            print('4. Calculate grades and target\n5. Upcoming deadlines')
            print('6. Delete assessment\n7. Edit assessment\n8. Exit')
            choice = get_integer('Choose 1-8: ', 1, 8)
            if choice == 8:
                print('Goodbye!')
                return
            actions = {1: self.add_assessment, 2: self.view_assessments,
                       3: self.record_mark, 4: self.calculate_grades,
                       5: self.upcoming_assessments, 6: self.delete_assessment,
                       7: self.edit_assessment}
            actions[choice]()


def main():
    try:
        AssessmentTracker().run()
    except (KeyboardInterrupt, EOFError):
        print('\nInput cancelled. Previously saved assessments are kept.')


if __name__ == '__main__':
    main()
