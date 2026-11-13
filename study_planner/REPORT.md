# Project Report – Study Planner

**Course:** CSC 4162 Programming in Python · Fall 2026–27 · Mid-Term Project

---

## 1. Project Title and Group Information

**Title:** Study Planner – A Study Task and Progress Tracker for Students

| Name | Student ID | Contribution |
|---|---|---|
| _[Member 1]_ | _[ID]_ | _e.g. models.py, validation.py_ |
| _[Member 2]_ | _[ID]_ | _e.g. planner_manager.py (file handling)_ |
| _[Member 3]_ | _[ID]_ | _e.g. gui.py, analysis.py, report_ |

---

## 2. Problem Statement, Objectives and Intended Users

**Problem.** Many university students prepare for several courses at the same time and lose
track of what they still need to study and how close each deadline is. Without a plan they
leave work until the last minute and often miss topics.

**Objectives.**
- Let students record study tasks with subject, topic, deadline, planned hours and priority.
- Let them log the hours they actually study.
- Automatically show each task's progress and status (Not Started / In Progress / Completed / Overdue).
- Calculate overall and per-subject statistics.
- Suggest a realistic study plan for today based on deadlines and priorities.
- Keep all data in a file so nothing is lost when the program closes.

**Intended users.** University and college students (and teachers who want to suggest a
revision plan). The app stores only study information, with no personal or sensitive data.

**Application type.** Hybrid application: Tkinter GUI + JSON file records + NumPy calculations.

---

## 3. Feature List and Workflow / Design

| # | Feature | Where |
|---|---|---|
| 1 | Add task (auto-generated unique ID) | `gui.add_task` → `StudyPlanner.add_task` |
| 2 | View all tasks in a colour-coded table | `gui.refresh_table` |
| 3 | Search by keyword + filter by subject/status | `StudyPlanner.search` |
| 4 | Update selected task | `StudyPlanner.update_task` |
| 5 | Delete selected task (confirmation) | `StudyPlanner.delete_task` |
| 6 | Log study hours | `StudyTask.add_study_hours` |
| 7 | Progress summary with statistics | `analysis.overall_statistics`, `analysis.subject_summary` |
| 8 | Today's study plan | `analysis.todays_plan` |
| 9 | Save / Reload / Save-on-exit prompt | `StudyPlanner.save_to_file`, `load_from_file` |

**Workflow.**

```
Start (main.py)
   │
   ▼
Load data/study_tasks.json ──(missing / empty / bad file)──► warning, empty planner
   │
   ▼
Main window: form + table + buttons
   │
   ├─ Add / Update ─► validate form ─(invalid)─► error message, stay on form
   │                         │ (valid)
   │                         ▼
   │                  update list + set ─► refresh table
   ├─ Delete / Log hours ─► find task ─(not found)─► error message
   ├─ Search / Filter ─► show matching rows
   ├─ Summary / Today's plan ─► NumPy calculations ─► result window
   ├─ Save ─► write JSON
   └─ Close ─► "Save changes?" ─► exit
```

**Program structure (matches section 7 of the requirements).**

| Component | File / Class |
|---|---|
| Data model class | `models.py` → `StudyTask` |
| Manager/application class | `planner_manager.py` → `StudyPlanner` |
| Input and validation functions | `validation.py` |
| Calculation functions | `analysis.py` (+ methods in `StudyTask`) |
| File functions | `StudyPlanner.load_from_file`, `StudyPlanner.save_to_file` |
| Interface functions | `gui.py` → `StudyPlannerApp` |

---

## 4. Python Concepts Used

| Concept | Example in the code |
|---|---|
| **Variables & data types** | `task_id` (str), `planned_hours` (float), `unsaved_changes` (bool), `task_count` (int), `deadline` (str converted to `date`) |
| **Operators** | `remaining = planned - done`, `percent = done / planned * 100`, comparisons `hours < 0`, `days_left < 0`, `total >= daily_limit`, membership `task_id in self.task_ids` |
| **Conditionals** | `StudyTask.get_status()` uses `if / elif / else` to decide the status; advice message in the summary; validation checks |
| **Loops** | `for` loops over tasks in `search`, `load_from_file`, `subject_summary`; `while` loop in `generate_next_id`; `while True` loop in `log_hours` that keeps asking until input is valid |
| **Functions** | 10+ functions/methods, each with one job: `validate_hours`, `validate_date`, `overall_statistics`, `todays_plan`, `find_task`, `save_to_file`, … |

---

## 5. Data Structures

| Structure | Where | Why |
|---|---|---|
| **List** | `StudyPlanner.tasks` holds all `StudyTask` objects; `todays_plan` returns a list of tasks | Ordered collection of records that can grow and shrink |
| **Tuple** | `PRIORITIES = ("High", "Medium", "Low")`, `STATUSES`, `COLUMNS` in `gui.py`, `(task, hours)` pairs in today's plan | Fixed values that must not change |
| **Set** | `StudyPlanner.task_ids` stores every ID; `get_subjects()` uses a set to get unique subject names | Fast duplicate-ID checking and removing duplicate subjects |
| **Dictionary** | `StudyTask.to_dict()` (one record = key/value pairs for JSON); `PRIORITY_RANK` maps priority → number; `STATUS_COLOURS` maps status → colour; statistics and subject summaries are returned as dictionaries | Map keys to related information |

---

## 6. Object-Oriented Design

**`StudyTask`** (`models.py`) – the data model.

| Attributes | Methods |
|---|---|
| `task_id`, `subject`, `topic`, `deadline`, `planned_hours`, `hours_done`, `priority` | `remaining_hours()`, `progress_percent()`, `days_left()`, `get_status()`, `daily_hours_needed()`, `add_study_hours(hours)`, `to_dict()`, `from_dict(data)` (class method), `__str__()` |

**`StudyPlanner`** (`planner_manager.py`) – the manager class.

| Attributes | Methods |
|---|---|
| `file_path`, `tasks` (list), `task_ids` (set), `load_messages` (list) | `load_from_file()`, `save_to_file()`, `generate_next_id()`, `add_task()`, `find_task()`, `update_task()`, `delete_task()`, `log_hours()`, `search()`, `get_subjects()` |

**`RecordNotFoundError`** – a custom exception class (inherits from `Exception`) raised when a task ID does not exist.

**`StudyPlannerApp`** (`gui.py`) – the interface class. It builds the window and calls `StudyPlanner`
methods; it contains no file or calculation logic itself.

---

## 7. File Handling and Exception Handling

**File handling.** Records are stored in `data/study_tasks.json` as a list of dictionaries.
The file is loaded automatically at start-up; the user can **Save** at any time or **Reload from File**.
When closing with unsaved changes the program asks whether to save. The folder is created
automatically if it does not exist.

**Exception handling (section 9 of the requirements).**

| Case | How it is handled |
|---|---|
| Invalid action | Update/Delete/Log hours with no row selected → warning message, program continues |
| Non-numeric input | `float()` inside `try/except ValueError` in `validate_hours` → clear message; the Log Hours dialog asks again |
| Out-of-range value | Negative hours, 0 planned hours, > 200 hours, hours done > planned hours, invalid date like `2026-13-40`, daily limit > 16 h → rejected |
| Empty required field | `validate_text` rejects empty subject/topic |
| Duplicate identifier | `task_ids` set checked in `add_task` and while loading the file |
| Record not found | `find_task` raises `RecordNotFoundError`; the GUI catches it and shows a message |
| Missing file | `FileNotFoundError` caught → empty planner + warning |
| Empty file | Detected → empty planner + warning |
| Malformed JSON | `json.JSONDecodeError` caught → empty planner + warning |
| Bad individual records | `KeyError/ValueError/TypeError` caught per record → only that record is skipped, the rest load |
| Cannot write file | `OSError` caught in `save_to_file` → error message instead of crash |

---

## 8. Library / Module Use and Justification

**Tkinter** – provides the whole interface: `Entry` fields and a `Combobox` for input, `Treeview`
table with colour-coded rows, buttons, pop-up `messagebox` errors/confirmations, `simpledialog`
input, and `Toplevel` result windows.

**NumPy** – used in `analysis.py` for the analysis features. Planned hours, studied hours and
progress values are turned into NumPy arrays and NumPy calculates `sum`, `mean`, `median`,
`std`, `min`, `max` and `minimum` (to cap extra hours). These results appear in the
Progress Summary window. The core logic (validation, status rules, search, CRUD, today's plan
selection) is written in plain Python, so the libraries do not hide the required programming.

**Standard library:** `json` (save/load), `os` (file paths, create folder), `datetime` (deadlines, days left).

---

## 9. Screenshots and Sample Input/Output

_Insert your own screenshots here:_

1. Main window with the 12 sample tasks loaded
2. Error message for an invalid input (e.g. empty subject or `-3` hours)
3. Task added / updated / deleted
4. Log Study Hours dialog and the "Well done!" message when a task is completed
5. Search/filter result (e.g. Subject = Python)
6. Progress Summary window
7. Today's Study Plan window
8. The `study_tasks.json` file open in a text editor after saving
9. Program restarted – data is still there

**Sample output (Progress Summary, with sample data on 14 Nov 2026):**

```
Total tasks            : 12
Total planned hours    : 61.0
Total hours studied    : 22.5
Hours remaining        : 38.5
Overall completion     : 36.9%
Tasks completed        : 2 (16.7%)
Progress per task:  Average 40.4%  Median 40.9%  Std. dev 33.8
```

---

## 10. Limitations, Societal Benefit and Future Improvements

**Limitations.**
- Single user, data stored locally in one JSON file.
- Dates must be typed in YYYY-MM-DD format (no calendar picker).
- No reminders/notifications.
- Today's plan uses a simple rule (deadline, then priority) and spreads hours evenly over the remaining days.

**Societal benefit.** Helps students organise their study time, notice overdue topics early and
spread their work over the days before a deadline, which can reduce last-minute stress and
improve learning. It is free, works offline and stores no personal data.

**Future improvements (final-term ideas).**
- Study session history (date + hours) and a weekly chart of study time (Matplotlib).
- Export a report to CSV.
- Calendar date picker and reminder pop-ups.
- Multiple student profiles and a teacher view.
- Smarter planning using past study speed for each subject.
