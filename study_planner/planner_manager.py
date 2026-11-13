"""
planner_manager.py
------------------
Manager / application class. It keeps all StudyTask objects, performs
add / search / update / delete operations, and saves / loads the JSON file.
"""

import json
import os
from models import StudyTask


class RecordNotFoundError(Exception):
    """Raised when a task ID does not exist."""
    pass


class StudyPlanner:
    """Coordinates the list of tasks and the data file."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.tasks = []          # LIST of StudyTask objects
        self.task_ids = set()    # SET of IDs -> fast duplicate checking
        self.load_messages = []  # warnings produced while loading

    # ------------------------- File handling -------------------------
    def load_from_file(self):
        """Load tasks from JSON. Handles missing, empty and malformed files.
        Returns the number of tasks loaded."""
        self.tasks = []
        self.task_ids = set()
        self.load_messages = []

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except FileNotFoundError:
            self.load_messages.append("Data file not found. Starting with an empty planner.")
            return 0
        except OSError as error:
            self.load_messages.append(f"Could not read the data file: {error}")
            return 0

        if content.strip() == "":
            self.load_messages.append("Data file is empty. Starting with an empty planner.")
            return 0

        try:
            records = json.loads(content)
        except json.JSONDecodeError:
            self.load_messages.append("Data file is not valid JSON. Starting with an empty planner.")
            return 0

        if not isinstance(records, list):
            self.load_messages.append("Data file has the wrong format (expected a list).")
            return 0

        skipped = 0
        for record in records:
            try:
                task = StudyTask.from_dict(record)
                if task.task_id in self.task_ids:
                    raise ValueError("duplicate ID")
                self.tasks.append(task)
                self.task_ids.add(task.task_id)
            except (KeyError, ValueError, TypeError, AttributeError):
                skipped += 1          # skip only the bad record, keep the rest

        if skipped > 0:
            self.load_messages.append(f"{skipped} invalid record(s) were skipped.")
        return len(self.tasks)

    def save_to_file(self):
        """Save all tasks to the JSON file. Returns True on success."""
        folder = os.path.dirname(self.file_path)
        try:
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump([t.to_dict() for t in self.tasks], file, indent=4)
            return True
        except OSError:
            return False

    # ------------------------- CRUD operations -------------------------
    def generate_next_id(self):
        """Create the next free ID like T001, T002 ..."""
        number = 1
        while f"T{number:03d}" in self.task_ids:
            number += 1
        return f"T{number:03d}"

    def add_task(self, task):
        """Add a new task. Duplicate IDs are rejected using the set."""
        if task.task_id in self.task_ids:
            raise ValueError(f"Task ID {task.task_id} already exists.")
        self.tasks.append(task)
        self.task_ids.add(task.task_id)

    def find_task(self, task_id):
        """Return the task with this ID or raise RecordNotFoundError."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        raise RecordNotFoundError(f"No task found with ID {task_id}.")

    def update_task(self, task_id, new_values):
        """Update a task's fields using a dictionary of new values."""
        task = self.find_task(task_id)
        for field, value in new_values.items():
            setattr(task, field, value)
        return task

    def delete_task(self, task_id):
        """Delete a task by ID."""
        task = self.find_task(task_id)
        self.tasks.remove(task)
        self.task_ids.discard(task_id)
        return task

    def log_hours(self, task_id, hours):
        """Add study hours to a task."""
        task = self.find_task(task_id)
        task.add_study_hours(hours)
        return task

    # ------------------------- Searching / filtering -------------------------
    def search(self, keyword="", subject="All", status="All"):
        """Return tasks matching a keyword AND the chosen subject/status."""
        keyword = keyword.strip().lower()
        results = []
        for task in self.tasks:
            text = f"{task.task_id} {task.subject} {task.topic}".lower()
            if keyword and keyword not in text:
                continue
            if subject != "All" and task.subject != subject:
                continue
            if status != "All" and task.get_status() != status:
                continue
            results.append(task)
        return results

    def get_subjects(self):
        """Unique subject names (a SET removes duplicates), sorted."""
        return sorted({task.subject for task in self.tasks})
