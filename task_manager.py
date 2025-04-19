import tkinter as tk
from tkinter import messagebox
import json
import os

DATA_FILE = "tasks.json"

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Task Manager")
        self.tasks = []

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        self.task_entry = tk.Entry(self.frame, width=40)
        self.task_entry.grid(row=0, column=0, padx=5)
        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=0, column=1)

        self.task_frame = tk.Frame(self.frame)
        self.task_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.delete_button = tk.Button(self.frame, text="Delete Completed Tasks", command=self.delete_done)
        self.delete_button.grid(row=2, column=0, columnspan=2)

        self.load_tasks()

    def add_task(self):
        text = self.task_entry.get().strip()
        if text:
            var = tk.IntVar()
            cb = tk.Checkbutton(self.task_frame, text=text, variable=var)
            cb.pack(anchor='w')
            self.tasks.append((cb, var))
            self.task_entry.delete(0, tk.END)
            self.save_tasks()
        else:
            messagebox.showwarning("Warning", "Task cannot be empty!")

    def delete_done(self):
        new_tasks = []
        for cb, var in self.tasks:
            if var.get() == 0:
                new_tasks.append((cb, var))
            else:
                cb.destroy()
        self.tasks = new_tasks
        self.save_tasks()

    def save_tasks(self):
        data = []
        for cb, var in self.tasks:
            data.append({"text": cb.cget("text"), "done": var.get()})
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    var = tk.IntVar(value=item["done"])
                    cb = tk.Checkbutton(self.task_frame, text=item["text"], variable=var)
                    cb.pack(anchor='w')
                    self.tasks.append((cb, var))


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
