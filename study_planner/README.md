# Study Planner – CSC 4162 Mid-Term Project

A Tkinter desktop app that helps students plan study tasks, log study hours,
track progress and get a suggested daily study plan. Data is saved in a JSON file
and statistics are calculated with NumPy.

## How to run

```bash
pip install numpy
python main.py          # main file
```

Tkinter is included with standard Python on Windows and macOS.
On Linux you may need: `sudo apt install python3-tk`

## Files

| File | Purpose |
|---|---|
| `main.py` | **Main file** – starts the program |
| `models.py` | `StudyTask` data model class + fixed tuples (priorities, statuses) |
| `planner_manager.py` | `StudyPlanner` manager class – add/search/update/delete, save/load JSON |
| `validation.py` | Input and validation functions |
| `analysis.py` | Calculation functions using NumPy (totals, average, median, std dev, daily plan) |
| `gui.py` | Tkinter interface (`StudyPlannerApp` class) |
| `data/study_tasks.json` | 12 sample records |

## Features

1. Add a study task (ID is generated automatically: T001, T002 …)
2. View all tasks in a colour-coded table (green = completed, yellow = in progress, red = overdue)
3. Search by keyword, filter by subject and status
4. Update a selected task
5. Delete a selected task (with confirmation)
6. Log study hours for a task
7. Progress summary (NumPy statistics + per-subject summary + advice)
8. Today's study plan (what to study today, given the hours you have)
9. Save to / reload from `data/study_tasks.json`; asks to save on exit

## Quick demo script (for the viva)

1. Run `python main.py` → 12 sample tasks load.
2. Add a task with an empty subject → error message. Enter `-3` hours → error. Fix and add.
3. Select T003 → **Log Study Hours** → type `abc` (error), then `2` (accepted).
4. **Progress Summary** and **Today's Study Plan**.
5. **Save**, close the program, run it again → the changes are still there.
6. Rename `data/study_tasks.json` and start the program → it opens with an empty planner instead of crashing.
