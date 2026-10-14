"""Student Study & Assessment Tracker - start here with: python main.py"""
from pathlib import Path
from datetime import date
from tracker import (read_tasks, save_tasks, add_task, upcoming,
                     days_until, summary, STATUSES, PRIORITIES)

DATA_FILE = Path(__file__).parent / "data" / "my_assessments.csv"


def choose_task(tasks):
    if not tasks:
        print("No assessments saved yet.")
        return None
    for number, item in enumerate(tasks, 1):
        print(f"{number}. {item['unit']} - {item['task']} ({item['status']})")
    answer = input("Enter assessment number: ").strip()
    if not answer.isdigit() or not 1 <= int(answer) <= len(tasks):
        print("Please enter a number from the list.")
        return None
    return tasks[int(answer) - 1]


def show_tasks(tasks):
    if not tasks:
        print("No assessments found. Add your first assessment!")
        return
    print("\nYOUR ASSESSMENTS")
    for number, item in enumerate(tasks, 1):
        remaining = days_until(item['due_date'])
        if item['status'] == 'Completed':
            message = 'Done'
        elif remaining < 0:
            message = f'{abs(remaining)} day(s) overdue'
        elif remaining == 0:
            message = 'Due today'
        else:
            message = f'{remaining} day(s) left'
        print(f"{number}. {item['unit']} | {item['task']} | "
              f"Due: {item['due_date']} | {item['priority']} | "
              f"{item['status']} | {message}")


def run():
    tasks = read_tasks(DATA_FILE)
    while True:
        print("\n===== STUDENT STUDY & ASSESSMENT TRACKER =====")
        print("1. Add assessment")
        print("2. View all assessments")
        print("3. View upcoming deadlines")
        print("4. Update progress")
        print("5. Record study hours")
        print("6. View study summary")
        print("7. Delete an assessment")
        print("8. Save and exit")
        choice = input("Choose 1-8: ").strip()
        if choice == '1':
            unit = input('Unit name/code: ')
            name = input('Assessment name: ')
            deadline = input('Due date (YYYY-MM-DD): ').strip()
            print('Priority options: ' + ', '.join(PRIORITIES))
            priority = input('Priority: ').strip().title()
            try:
                add_task(tasks, unit, name, deadline, priority)
                save_tasks(DATA_FILE, tasks)
                print('Assessment added and saved!')
            except ValueError as error:
                print(error)
        elif choice == '2':
            show_tasks(tasks)
        elif choice == '3':
            show_tasks(upcoming(tasks))
        elif choice == '4':
            selected = choose_task(tasks)
            if selected is not None:
                print('Status options: ' + ', '.join(STATUSES))
                status = input('New status: ').strip().title()
                if status in STATUSES:
                    selected['status'] = status
                    save_tasks(DATA_FILE, tasks)
                    print('Progress updated!')
                else:
                    print('Status not recognised.')
        elif choice == '5':
            selected = choose_task(tasks)
            if selected is not None:
                try:
                    hours = float(input('Additional hours studied: '))
                    if not 0 < hours <= 24:
                        print('Enter hours greater than 0 and no more than 24.')
                        continue
                    selected['hours_spent'] = str(round(float(selected['hours_spent']) + hours, 2))
                    save_tasks(DATA_FILE, tasks)
                    print('Study time recorded!')
                except ValueError:
                    print('Please enter a number such as 1.5.')
        elif choice == '6':
            total, completed, hours, percent = summary(tasks)
            print(f'Total assessments: {total}')
            print(f'Completed: {completed}')
            print(f'Study hours recorded: {hours:.1f}')
            print(f'Completion rate: {percent:.1f}%')
            due_soon = [item for item in upcoming(tasks)
                        if 0 <= days_until(item['due_date']) <= 7]
            print(f'Unfinished assessments due within 7 days: {len(due_soon)}')
        elif choice == '7':
            selected = choose_task(tasks)
            if selected is not None:
                confirm = input('Type YES to delete: ').strip()
                if confirm == 'YES':
                    tasks.remove(selected)
                    save_tasks(DATA_FILE, tasks)
                    print('Assessment deleted.')
                else:
                    print('Deletion cancelled.')
        elif choice == '8':
            save_tasks(DATA_FILE, tasks)
            print('Goodbye! Your data is saved.')
            break
        else:
            print('Please choose a number between 1 and 8.')


if __name__ == '__main__':
    run()
