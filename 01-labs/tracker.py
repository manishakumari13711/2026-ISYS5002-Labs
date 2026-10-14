"""Functions for storing and reviewing student assessments."""
import csv
from datetime import date, datetime
from pathlib import Path

HEADERS = ["unit", "task", "due_date", "priority", "status", "hours_spent"]
STATUSES = ["Not started", "In progress", "Completed"]
PRIORITIES = ["Low", "Medium", "High"]


def read_tasks(filename):
    """Return assessment records, or an empty list for a new file."""
    path = Path(filename)
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def save_tasks(filename, tasks):
    """Write all tasks to a CSV file."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(tasks)


def check_date(value):
    """Accept only real dates in YYYY-MM-DD format."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def add_task(tasks, unit, task, due_date, priority):
    if not unit.strip() or not task.strip():
        raise ValueError("Unit and assessment name cannot be empty.")
    if check_date(due_date) is None:
        raise ValueError("Enter a valid date like 2026-11-10.")
    if priority not in PRIORITIES:
        raise ValueError("Priority must be Low, Medium or High.")
    tasks.append({"unit": unit.strip(), "task": task.strip(),
                  "due_date": due_date, "priority": priority,
                  "status": "Not started", "hours_spent": "0"})


def days_until(due_date, today=None):
    if today is None:
        today = date.today()
    return (check_date(due_date) - today).days


def upcoming(tasks, today=None):
    """Show unfinished tasks in due-date order."""
    pending = [task for task in tasks if task["status"] != "Completed"]
    return sorted(pending, key=lambda item: item["due_date"])


def summary(tasks):
    total = len(tasks)
    completed = sum(1 for item in tasks if item["status"] == "Completed")
    hours = sum(float(item["hours_spent"]) for item in tasks)
    percent = (completed / total * 100) if total else 0
    return total, completed, hours, percent
