"""
gui.py
------
Tkinter graphical interface for the Study Planner.

Layout:
    left  -> form to enter / edit a task
    right -> search bar + table of tasks
    below -> action buttons and a status bar
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from models import StudyTask, PRIORITIES, STATUSES
from planner_manager import StudyPlanner, RecordNotFoundError
from validation import validate_task_form, validate_hours
from analysis import overall_statistics, subject_summary, todays_plan

# Table columns: (internal name, heading, width)  -> TUPLE of TUPLES
COLUMNS = (
    ("id", "ID", 45),
    ("subject", "Subject", 105),
    ("topic", "Topic", 165),
    ("deadline", "Deadline", 85),
    ("days", "Days Left", 65),
    ("hours", "Done / Plan (h)", 95),
    ("progress", "Progress", 65),
    ("priority", "Priority", 65),
    ("status", "Status", 85),
)

# Row colour for each status -> DICTIONARY
STATUS_COLOURS = {
    "Completed": "#d9f2d9",
    "In Progress": "#fff4cc",
    "Not Started": "#ffffff",
    "Overdue": "#f8d0d0",
}


class StudyPlannerApp:
    """The main window of the application."""

    def __init__(self, root, planner):
        self.root = root
        self.planner = planner
        self.selected_id = None       # ID of the row currently selected
        self.unsaved_changes = False

        self.root.title("Study Planner - CSC 4162 Mid-Term Project")
        self.root.geometry("1250x600")
        self.root.minsize(1000, 520)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.build_form()
        self.build_table()
        self.build_buttons()
        self.build_status_bar()

        self.load_data(show_message=False)

    # =================================================================
    #                         BUILD THE INTERFACE
    # =================================================================
    def build_form(self):
        form = ttk.LabelFrame(self.root, text=" Task Details ", padding=10)
        form.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        self.id_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.topic_var = tk.StringVar()
        self.deadline_var = tk.StringVar()
        self.planned_var = tk.StringVar()
        self.done_var = tk.StringVar(value="0")
        self.priority_var = tk.StringVar(value=PRIORITIES[1])

        ttk.Label(form, text="Task ID:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(form, textvariable=self.id_var, foreground="#1f4e8c",
                  font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w")

        # Each form field: (label text, variable)
        fields = (
            ("Subject:", self.subject_var),
            ("Topic:", self.topic_var),
            ("Deadline (YYYY-MM-DD):", self.deadline_var),
            ("Planned hours:", self.planned_var),
            ("Hours done:", self.done_var),
        )
        for row, (label, variable) in enumerate(fields, start=1):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=variable, width=24).grid(row=row, column=1, pady=4)

        ttk.Label(form, text="Priority:").grid(row=6, column=0, sticky="w", pady=4)
        ttk.Combobox(form, textvariable=self.priority_var, values=PRIORITIES,
                     state="readonly", width=21).grid(row=6, column=1, pady=4)

        # Form buttons
        ttk.Button(form, text="Add Task", command=self.add_task)\
            .grid(row=7, column=0, columnspan=2, sticky="ew", pady=(12, 3))
        ttk.Button(form, text="Update Selected", command=self.update_task)\
            .grid(row=8, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(form, text="Delete Selected", command=self.delete_task)\
            .grid(row=9, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(form, text="Clear Form", command=self.clear_form)\
            .grid(row=10, column=0, columnspan=2, sticky="ew", pady=3)

    def build_table(self):
        right = ttk.Frame(self.root)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # ---- search / filter bar ----
        bar = ttk.Frame(right)
        bar.pack(fill="x", pady=(0, 6))
        self.search_var = tk.StringVar()
        self.subject_filter = tk.StringVar(value="All")
        self.status_filter = tk.StringVar(value="All")

        ttk.Label(bar, text="Search:").pack(side="left")
        search_entry = ttk.Entry(bar, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=4)
        search_entry.bind("<Return>", lambda event: self.refresh_table())

        ttk.Label(bar, text="Subject:").pack(side="left", padx=(8, 0))
        self.subject_box = ttk.Combobox(bar, textvariable=self.subject_filter,
                                        state="readonly", width=14)
        self.subject_box.pack(side="left", padx=4)

        ttk.Label(bar, text="Status:").pack(side="left", padx=(8, 0))
        ttk.Combobox(bar, textvariable=self.status_filter, values=("All",) + STATUSES,
                     state="readonly", width=12).pack(side="left", padx=4)

        ttk.Button(bar, text="Search", command=self.refresh_table).pack(side="left", padx=4)
        ttk.Button(bar, text="Show All", command=self.show_all).pack(side="left")

        # ---- table ----
        table_frame = ttk.Frame(right)
        table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_frame, columns=[c[0] for c in COLUMNS],
                                  show="headings", selectmode="browse")
        for name, heading, width in COLUMNS:
            self.table.heading(name, text=heading)
            self.table.column(name, width=width, anchor="center")
        self.table.column("topic", anchor="w")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for status, colour in STATUS_COLOURS.items():
            self.table.tag_configure(status, background=colour)
        self.table.bind("<<TreeviewSelect>>", self.on_row_selected)

    def build_buttons(self):
        bar = ttk.Frame(self.root, padding=(10, 0))
        bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        # (button text, function) pairs
        buttons = (
            ("Log Study Hours", self.log_hours),
            ("Progress Summary", self.show_summary),
            ("Today's Study Plan", self.show_todays_plan),
            ("Save", self.save_data),
            ("Reload from File", self.reload_data),
        )
        for text, command in buttons:
            ttk.Button(bar, text=text, command=command).pack(side="left", padx=4, pady=6)

    def build_status_bar(self):
        self.status_text = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status_text, relief="sunken",
                  anchor="w", padding=4).grid(row=2, column=0, columnspan=2, sticky="ew")

    # =================================================================
    #                          HELPER METHODS
    # =================================================================
    def set_status(self, message):
        marker = "  (unsaved changes)" if self.unsaved_changes else ""
        self.status_text.set(f"{message}{marker}   |   Total tasks: {len(self.planner.tasks)}")

    def refresh_table(self):
        """Redraw the table using the current search and filter values."""
        for row in self.table.get_children():
            self.table.delete(row)

        results = self.planner.search(self.search_var.get(),
                                      self.subject_filter.get(),
                                      self.status_filter.get())
        for task in results:
            status = task.get_status()
            days = task.days_left()
            self.table.insert("", "end", iid=task.task_id, tags=(status,), values=(
                task.task_id, task.subject, task.topic, task.deadline,
                days if status != "Completed" else "-",
                f"{task.hours_done:g} / {task.planned_hours:g}",
                f"{task.progress_percent():g}%",
                task.priority, status,
            ))
        self.subject_box["values"] = ("All",) + tuple(self.planner.get_subjects())
        self.set_status(f"Showing {len(results)} task(s)")

    def show_all(self):
        self.search_var.set("")
        self.subject_filter.set("All")
        self.status_filter.set("All")
        self.refresh_table()

    def clear_form(self):
        self.selected_id = None
        self.table.selection_remove(self.table.selection())
        self.id_var.set(self.planner.generate_next_id() + " (new)")
        for variable in (self.subject_var, self.topic_var, self.deadline_var, self.planned_var):
            variable.set("")
        self.done_var.set("0")
        self.priority_var.set(PRIORITIES[1])

    def read_form(self):
        """Read and validate the form. Returns a dict or None on error."""
        try:
            return validate_task_form(self.subject_var.get(), self.topic_var.get(),
                                      self.deadline_var.get(), self.planned_var.get(),
                                      self.done_var.get(), self.priority_var.get())
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return None

    def changed(self, message):
        self.unsaved_changes = True
        self.refresh_table()
        self.set_status(message)

    def get_selected_or_warn(self):
        if self.selected_id is None:
            messagebox.showwarning("No task selected", "Please select a task in the table first.")
        return self.selected_id

    # =================================================================
    #                          EVENT HANDLERS
    # =================================================================
    def on_row_selected(self, event=None):
        selection = self.table.selection()
        if not selection:
            return
        try:
            task = self.planner.find_task(selection[0])
        except RecordNotFoundError:
            return
        self.selected_id = task.task_id
        self.id_var.set(task.task_id)
        self.subject_var.set(task.subject)
        self.topic_var.set(task.topic)
        self.deadline_var.set(task.deadline)
        self.planned_var.set(f"{task.planned_hours:g}")
        self.done_var.set(f"{task.hours_done:g}")
        self.priority_var.set(task.priority)

    def add_task(self):
        values = self.read_form()
        if values is None:
            return
        task_id = self.planner.generate_next_id()
        try:
            self.planner.add_task(StudyTask(task_id, **values))
        except ValueError as error:
            messagebox.showerror("Cannot add task", str(error))
            return
        self.changed(f"Task {task_id} added")
        self.clear_form()

    def update_task(self):
        task_id = self.get_selected_or_warn()
        if task_id is None:
            return
        values = self.read_form()
        if values is None:
            return
        try:
            self.planner.update_task(task_id, values)
        except RecordNotFoundError as error:
            messagebox.showerror("Not found", str(error))
            return
        self.changed(f"Task {task_id} updated")

    def delete_task(self):
        task_id = self.get_selected_or_warn()
        if task_id is None:
            return
        if not messagebox.askyesno("Confirm delete", f"Delete task {task_id}?"):
            return
        try:
            self.planner.delete_task(task_id)
        except RecordNotFoundError as error:
            messagebox.showerror("Not found", str(error))
            return
        self.changed(f"Task {task_id} deleted")
        self.clear_form()

    def log_hours(self):
        task_id = self.get_selected_or_warn()
        if task_id is None:
            return
        # Keep asking until the input is valid or the user presses Cancel
        while True:
            text = simpledialog.askstring("Log study hours",
                                          f"How many hours did you study for {task_id}?",
                                          parent=self.root)
            if text is None:          # Cancel pressed
                return
            try:
                hours = validate_hours(text, "Study hours")
                task = self.planner.log_hours(task_id, hours)
                break
            except ValueError as error:
                messagebox.showerror("Invalid input", str(error))
            except RecordNotFoundError as error:
                messagebox.showerror("Not found", str(error))
                return

        self.changed(f"Logged {hours:g} h for {task_id}")
        self.on_row_selected()
        if task.get_status() == "Completed":
            messagebox.showinfo("Well done!", f"Task {task_id} is now completed.")

    # =================================================================
    #                        ANALYSIS WINDOWS
    # =================================================================
    def open_text_window(self, title, text):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("600x600")
        box = tk.Text(window, wrap="word", font=("Consolas", 10), padx=10, pady=10)
        box.insert("1.0", text)
        box.configure(state="disabled")
        box.pack(fill="both", expand=True)
        ttk.Button(window, text="Close", command=window.destroy).pack(pady=6)

    def show_summary(self):
        stats = overall_statistics(self.planner.tasks)
        if stats is None:
            messagebox.showinfo("Summary", "There are no tasks to summarise yet.")
            return

        lines = [
            "OVERALL PROGRESS (calculated with NumPy)",
            "=" * 46,
            f"Total tasks            : {stats['task_count']}",
            f"Total planned hours    : {stats['total_planned']}",
            f"Total hours studied    : {stats['total_done']}",
            f"Hours remaining        : {stats['total_remaining']}",
            f"Overall completion     : {stats['overall_percent']}%",
            f"Tasks completed        : {stats['completed']} ({stats['completion_rate']}%)",
            "",
            "Progress per task:",
            f"  Average  : {stats['avg_progress']}%",
            f"  Median   : {stats['median_progress']}%",
            f"  Std. dev : {stats['std_progress']}",
            "",
            f"Planned hours per task : min {stats['min_planned']}, "
            f"max {stats['max_planned']}, avg {stats['avg_planned']}",
            "",
            "TASKS BY STATUS",
            "-" * 46,
        ]
        for status in STATUSES:
            lines.append(f"  {status:<12}: {stats['status_counts'].get(status, 0)}")

        lines += ["", "PROGRESS BY SUBJECT", "-" * 46,
                  f"  {'Subject':<14}{'Tasks':>6}{'Done':>8}{'Plan':>8}{'%':>8}"]
        for subject, info in sorted(subject_summary(self.planner.tasks).items()):
            lines.append(f"  {subject:<14}{info['tasks']:>6}{info['done']:>8g}"
                         f"{info['planned']:>8g}{info['percent']:>7}%")

        # A simple message based on overall progress (if / elif / else)
        percent = stats["overall_percent"]
        if percent >= 75:
            advice = "Excellent! You are almost there."
        elif percent >= 40:
            advice = "Good progress. Keep a steady routine."
        else:
            advice = "You are just getting started - focus on high-priority tasks."
        overdue = stats["status_counts"].get("Overdue", 0)
        if overdue > 0:
            advice += f"\nWarning: {overdue} task(s) are overdue. Update their deadlines or finish them."
        lines += ["", "ADVICE", "-" * 46, advice]

        self.open_text_window("Progress Summary", "\n".join(lines))

    def show_todays_plan(self):
        limit_text = simpledialog.askstring("Today's plan",
                                            "How many hours can you study today?",
                                            initialvalue="6", parent=self.root)
        if limit_text is None:
            return
        try:
            limit = validate_hours(limit_text, "Daily study hours")
            if limit > 16:
                raise ValueError("Please enter a realistic daily limit (16 hours or less).")
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return

        plan, total = todays_plan(self.planner.tasks, limit)
        if not plan:
            messagebox.showinfo("Today's plan", "All tasks are completed. Enjoy your free time!")
            return

        lines = [f"SUGGESTED STUDY PLAN FOR TODAY (limit {limit:g} h)", "=" * 50,
                 "Sorted by nearest deadline, then priority.", ""]
        for number, (task, hours) in enumerate(plan, start=1):
            days = task.days_left()
            when = "OVERDUE" if days < 0 else ("due today" if days == 0 else f"{days} day(s) left")
            lines.append(f"{number}. [{task.priority}] {task.subject} - {task.topic}")
            lines.append(f"     Study {hours:g} h   ({task.remaining_hours():g} h left, {when})")
        lines += ["", f"Total suggested today: {total:g} h"]
        self.open_text_window("Today's Study Plan", "\n".join(lines))

    # =================================================================
    #                          SAVE / LOAD
    # =================================================================
    def load_data(self, show_message=True):
        count = self.planner.load_from_file()
        self.unsaved_changes = False
        self.show_all()
        self.clear_form()
        for warning in self.planner.load_messages:
            messagebox.showwarning("Loading data", warning)
        self.set_status(f"Loaded {count} task(s) from {self.planner.file_path}")
        if show_message:
            messagebox.showinfo("Reloaded", f"Loaded {count} task(s) from the file.")

    def save_data(self):
        if self.planner.save_to_file():
            self.unsaved_changes = False
            self.set_status(f"Saved {len(self.planner.tasks)} task(s) to {self.planner.file_path}")
            messagebox.showinfo("Saved", "All tasks were saved successfully.")
            return True
        messagebox.showerror("Save failed", "Could not write the data file. Check folder permissions.")
        return False

    def reload_data(self):
        if self.unsaved_changes and not messagebox.askyesno(
                "Unsaved changes", "You have unsaved changes. Reload and lose them?"):
            return
        self.load_data(show_message=True)

    def on_close(self):
        if self.unsaved_changes:
            answer = messagebox.askyesnocancel("Exit", "Save changes before closing?")
            if answer is None:                 # Cancel
                return
            if answer and not self.save_data():
                return
        self.root.destroy()
