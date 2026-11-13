"""
validation.py
-------------
Input validation functions.

Every function either RETURNS a clean value or RAISES a ValueError
with a clear, user-friendly message. The GUI catches the ValueError
and shows the message in a pop-up, so the program never crashes.
"""

from datetime import datetime
from models import PRIORITIES, DATE_FORMAT

MAX_HOURS = 200        # an upper limit to reject impossible values


def validate_text(value, field_name, max_length=40):
    """Required text field: must not be empty or too long."""
    value = value.strip()
    if value == "":
        raise ValueError(f"{field_name} cannot be empty.")
    if len(value) > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters.")
    return value


def validate_hours(value, field_name, allow_zero=False):
    """Convert text to a float and check it is in a sensible range."""
    try:
        hours = float(value)
    except ValueError:
        raise ValueError(f"{field_name} must be a number (e.g. 2 or 1.5).")

    if hours < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    if hours == 0 and not allow_zero:
        raise ValueError(f"{field_name} must be greater than 0.")
    if hours > MAX_HOURS:
        raise ValueError(f"{field_name} cannot be more than {MAX_HOURS}.")
    return round(hours, 2)


def validate_date(value):
    """Date must be in YYYY-MM-DD format and be a real calendar date."""
    value = value.strip()
    try:
        datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        raise ValueError("Deadline must be a valid date in YYYY-MM-DD format.")
    return value


def validate_priority(value):
    """Priority must be one of the allowed values in the PRIORITIES tuple."""
    if value not in PRIORITIES:
        raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}.")
    return value


def validate_task_form(subject, topic, deadline, planned, done, priority):
    """Validate a whole form at once. Returns a dictionary of clean values."""
    clean = {
        "subject": validate_text(subject, "Subject"),
        "topic": validate_text(topic, "Topic"),
        "deadline": validate_date(deadline),
        "planned_hours": validate_hours(planned, "Planned hours"),
        "hours_done": validate_hours(done if done.strip() else "0",
                                     "Hours done", allow_zero=True),
        "priority": validate_priority(priority),
    }
    # Cross-field check
    if clean["hours_done"] > clean["planned_hours"]:
        raise ValueError("Hours done cannot be more than planned hours.")
    return clean
