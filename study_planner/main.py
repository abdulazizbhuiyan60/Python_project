"""
main.py  -  MAIN FILE (run this one)
=====================================
Study Planner  |  CSC 4162 Programming in Python  |  Mid-Term Project

Run with:   python main.py
Requires:   Python 3.8+, NumPy (pip install numpy), Tkinter (comes with Python)
"""

import os
import tkinter as tk

from planner_manager import StudyPlanner
from gui import StudyPlannerApp

# Data file is stored next to this script, inside the "data" folder
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_FOLDER, "data", "study_tasks.json")


def main():
    planner = StudyPlanner(DATA_FILE)
    root = tk.Tk()
    StudyPlannerApp(root, planner)
    root.mainloop()


if __name__ == "__main__":
    main()
