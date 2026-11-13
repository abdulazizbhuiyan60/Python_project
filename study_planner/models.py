"""
models.py
---------
Data model class for the Study Planner.

A StudyTask represents ONE thing a student plans to study
(for example: "Python - OOP chapter, 6 hours, due 2026-11-25").
"""

from datetime import datetime, date

# ---------------- Fixed configuration values (TUPLES) ----------------
# Tuples are used because these values should never change while
# the program is running.
PRIORITIES = ("High", "Medium", "Low")
STATUSES = ("Not Started", "In Progress", "Completed", "Overdue")
DATE_FORMAT = "%Y-%m-%d"

# Maps each priority to a number so tasks can be sorted (DICTIONARY)
PRIORITY_RANK = {"High": 1, "Medium": 2, "Low": 3}


class StudyTask:
    """Represents a single study task / study goal."""

    def __init__(self, task_id, subject, topic, deadline,
                 planned_hours, hours_done=0.0, priority="Medium"):
        self.task_id = task_id              # str   e.g. "T001"
        self.subject = subject              # str   e.g. "Python"
        self.topic = topic                  # str   e.g. "OOP basics"
        self.deadline = deadline            # str   "YYYY-MM-DD"
        self.planned_hours = float(planned_hours)   # float
        self.hours_done = float(hours_done)         # float
        self.priority = priority            # one of PRIORITIES

    # ---------------------- Calculations ----------------------
    def remaining_hours(self):
        """Hours still left to study (never negative)."""
        return max(self.planned_hours - self.hours_done, 0.0)

    def progress_percent(self):
        """Percentage of planned hours already completed (0-100)."""
        if self.planned_hours <= 0:
            return 0.0
        percent = (self.hours_done / self.planned_hours) * 100
        return min(round(percent, 1), 100.0)

    def days_left(self, today=None):
        """Number of days from today until the deadline (negative = passed)."""
        if today is None:
            today = date.today()
        deadline_date = datetime.strptime(self.deadline, DATE_FORMAT).date()
        return (deadline_date - today).days

    def get_status(self, today=None):
        """Decide the status of the task using if / elif / else."""
        if self.hours_done >= self.planned_hours:
            return "Completed"
        elif self.days_left(today) < 0:
            return "Overdue"
        elif self.hours_done > 0:
            return "In Progress"
        else:
            return "Not Started"

    def daily_hours_needed(self, today=None):
        """How many hours per day are needed to finish on time."""
        if self.get_status(today) == "Completed":
            return 0.0
        days = self.days_left(today)
        if days <= 0:
            # Due today or already overdue: everything must be done now
            return round(self.remaining_hours(), 2)
        # +1 so that the deadline day itself counts as a study day
        return round(self.remaining_hours() / (days + 1), 2)

    # ---------------------- Updates ----------------------
    def add_study_hours(self, hours):
        """Log a study session. Raises ValueError for invalid hours."""
        if hours <= 0:
            raise ValueError("Study hours must be greater than 0.")
        self.hours_done = round(self.hours_done + hours, 2)

    # ---------------------- File conversion ----------------------
    def to_dict(self):
        """Convert the object into a dictionary so it can be saved as JSON."""
        return {
            "task_id": self.task_id,
            "subject": self.subject,
            "topic": self.topic,
            "deadline": self.deadline,
            "planned_hours": self.planned_hours,
            "hours_done": self.hours_done,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a StudyTask from a dictionary (loaded from JSON).
        Raises KeyError / ValueError if the record is malformed."""
        task = cls(
            task_id=str(data["task_id"]),
            subject=str(data["subject"]),
            topic=str(data["topic"]),
            deadline=str(data["deadline"]),
            planned_hours=float(data["planned_hours"]),
            hours_done=float(data.get("hours_done", 0)),
            priority=str(data.get("priority", "Medium")),
        )
        # Check the date is real, e.g. "2026-13-45" will raise ValueError
        datetime.strptime(task.deadline, DATE_FORMAT)
        if task.priority not in PRIORITIES:
            raise ValueError(f"Unknown priority: {task.priority}")
        return task

    def __str__(self):
        return (f"{self.task_id} | {self.subject} - {self.topic} | "
                f"{self.hours_done}/{self.planned_hours} h | "
                f"due {self.deadline} | {self.get_status()}")
