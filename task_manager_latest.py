import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

DATA_FILE = "tasks.json"

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Task Manager")
        self.tasks = []

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        # Input fields
        tk.Label(self.frame, text="Task:").grid(row=0, column=0, sticky="w")
        self.task_entry = tk.Entry(self.frame, width=40)
        self.task_entry.grid(row=0, column=1, columnspan=3, padx=5)

        tk.Label(self.frame, text="Deadline (YYYY-MM-DD):").grid(row=1, column=0, sticky="w")
        self.deadline_entry = tk.Entry(self.frame, width=20)
        self.deadline_entry.grid(row=1, column=1)

        tk.Label(self.frame, text="Priority:").grid(row=1, column=2, sticky="e")
        self.priority = tk.StringVar(value="Medium")
        tk.Radiobutton(self.frame, text="High", variable=self.priority, value="High").grid(row=1, column=3, sticky="w")
        tk.Radiobutton(self.frame, text="Medium", variable=self.priority, value="Medium").grid(row=1, column=4, sticky="w")
        tk.Radiobutton(self.frame, text="Low", variable=self.priority, value="Low").grid(row=1, column=5, sticky="w")

        tk.Label(self.frame, text="Subtasks (comma-separated):").grid(row=2, column=0, sticky="w")
        self.subtasks_entry = tk.Entry(self.frame, width=40)
        self.subtasks_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=(0, 10))

        # Buttons
        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=3, column=0, columnspan=2, sticky="w")

        self.delete_button = tk.Button(self.frame, text="Delete Completed", command=self.delete_done)
        self.delete_button.grid(row=3, column=2, columnspan=2, sticky="e")

        # Task list display
        self.task_frame = tk.Frame(self.frame)
        self.task_frame.grid(row=4, column=0, columnspan=6, pady=10)

        self.load_tasks()

    def add_task(self):
        text = self.task_entry.get().strip()
        deadline = self.deadline_entry.get().strip()
        priority = self.priority.get()
        subtasks = [s.strip() for s in self.subtasks_entry.get().split(",") if s.strip()]

        if not text:
            messagebox.showwarning("Warning", "Task cannot be empty!")
            return

        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Deadline format should be YYYY-MM-DD.")
                return

        var = tk.IntVar()
        info = f"{text} | Due: {deadline or 'N/A'} | Priority: {priority}"
        if subtasks:
            info += f" | Subtasks: {', '.join(subtasks)}"
        cb = tk.Checkbutton(self.task_frame, text=info, variable=var, anchor="w", justify="left", wraplength=400)
        cb.pack(anchor='w')
        self.tasks.append((cb, var, {
            "text": text,
            "deadline": deadline,
            "priority": priority,
            "subtasks": subtasks,
            "done": 0
        }))
        self.clear_inputs()
        self.save_tasks()

    def clear_inputs(self):
        self.task_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.subtasks_entry.delete(0, tk.END)
        self.priority.set("Medium")

    def delete_done(self):
        new_tasks = []
        for cb, var, data in self.tasks:
            if var.get() == 0:
                new_tasks.append((cb, var, data))
            else:
                cb.destroy()
        self.tasks = new_tasks
        self.save_tasks()

    def save_tasks(self):
        data = []
        for cb, var, item in self.tasks:
            item["done"] = var.get()
            data.append(item)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    var = tk.IntVar(value=item.get("done", 0))
                    info = f"{item['text']} | Due: {item.get('deadline') or 'N/A'} | Priority: {item.get('priority', 'Medium')}"
                    subtasks = item.get("subtasks", [])
                    if subtasks:
                        info += f" | Subtasks: {', '.join(subtasks)}"
                    cb = tk.Checkbutton(self.task_frame, text=info, variable=var, anchor="w", justify="left", wraplength=400)
                    cb.pack(anchor='w')
                    self.tasks.append((cb, var, item))

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
