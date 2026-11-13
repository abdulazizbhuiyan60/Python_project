"""
analysis.py
-----------
Calculation functions that use NumPy for numerical summaries.

NumPy is used for a real purpose here: the hours and progress values of
all tasks are put into arrays and NumPy computes totals, averages,
median, standard deviation, minimum and maximum.
"""

import numpy as np


def overall_statistics(tasks):
    """Return a dictionary of statistics for a list of StudyTask objects."""
    if len(tasks) == 0:
        return None

    planned = np.array([t.planned_hours for t in tasks])
    done = np.array([t.hours_done for t in tasks])
    progress = np.array([t.progress_percent() for t in tasks])

    total_planned = float(np.sum(planned))
    total_done = float(np.sum(np.minimum(done, planned)))   # don't count extra hours

    statuses = [t.get_status() for t in tasks]
    completed = statuses.count("Completed")

    return {
        "task_count": len(tasks),
        "total_planned": round(total_planned, 2),
        "total_done": round(total_done, 2),
        "total_remaining": round(total_planned - total_done, 2),
        "overall_percent": round(total_done / total_planned * 100, 1) if total_planned else 0.0,
        "avg_progress": round(float(np.mean(progress)), 1),
        "median_progress": round(float(np.median(progress)), 1),
        "std_progress": round(float(np.std(progress)), 1),
        "max_planned": round(float(np.max(planned)), 2),
        "min_planned": round(float(np.min(planned)), 2),
        "avg_planned": round(float(np.mean(planned)), 2),
        "completed": completed,
        "completion_rate": round(completed / len(tasks) * 100, 1),
        "status_counts": {s: statuses.count(s) for s in set(statuses)},
    }


def subject_summary(tasks):
    """Group tasks by subject and calculate hours + progress per subject.
    Returns a dictionary: {subject: {"tasks", "planned", "done", "percent"}}"""
    summary = {}
    for task in tasks:
        if task.subject not in summary:
            summary[task.subject] = {"tasks": 0, "planned": [], "done": []}
        summary[task.subject]["tasks"] += 1
        summary[task.subject]["planned"].append(task.planned_hours)
        summary[task.subject]["done"].append(min(task.hours_done, task.planned_hours))

    # Use NumPy to turn the collected lists into totals
    for subject, info in summary.items():
        planned_total = float(np.sum(np.array(info["planned"])))
        done_total = float(np.sum(np.array(info["done"])))
        info["planned"] = round(planned_total, 2)
        info["done"] = round(done_total, 2)
        info["percent"] = round(done_total / planned_total * 100, 1) if planned_total else 0.0
    return summary


def todays_plan(tasks, daily_limit=6.0):
    """Suggest what to study today.

    Unfinished tasks are sorted by deadline, then priority. Each task gets
    the hours it needs per day, until the daily study limit is reached.
    Returns (list of (task, hours) tuples, total hours).
    """
    from models import PRIORITY_RANK

    pending = [t for t in tasks if t.get_status() != "Completed"]
    pending.sort(key=lambda t: (t.deadline, PRIORITY_RANK[t.priority]))

    plan = []
    total = 0.0
    for task in pending:
        if total >= daily_limit:
            break
        hours = max(task.daily_hours_needed(), 0.5)        # at least a 30-minute session
        hours = min(hours, task.remaining_hours(), daily_limit - total)  # never over the limit
        hours = round(hours, 2)
        plan.append((task, hours))
        total += hours
    return plan, round(total, 2)
