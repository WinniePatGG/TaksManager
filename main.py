import customtkinter as ctk
import json
import os
from datetime import datetime
from tkinter import messagebox

TASKS_FILE = "tasks.json"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

STATUS_COLORS = {
    "Open": "gray",
    "In Progress": "orange",
    "Done": "green"
}

PRIORITY_COLORS = {
    "Low": "#7FDBFF",
    "Medium": "#FFDC00",
    "High": "#FF4136"
}

class TaskManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cool Task Manager")
        self.geometry("800x650")
        self.resizable(False, False)

        self.tasks = self.load_tasks()
        self.filter_status = None

        # Current Time
        self.time_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.time_label.pack(pady=5)
        self.update_time()

        # Entry for new tasks
        entry_frame = ctk.CTkFrame(self)
        entry_frame.pack(pady=5, padx=10, fill="x")

        self.task_entry = ctk.CTkEntry(entry_frame, placeholder_text="Enter a new task", height=40, corner_radius=10)
        self.task_entry.pack(side="left", padx=5, fill="x", expand=True)

        self.priority_dropdown = ctk.CTkComboBox(entry_frame, values=["Low", "Medium", "High"], width=100,
                                                 fg_color="white", text_color="black", dropdown_text_color="black", dropdown_fg_color="white")
        self.priority_dropdown.set("Medium")
        self.priority_dropdown.pack(side="left", padx=5)

        self.add_button = ctk.CTkButton(entry_frame, text="Add Task", command=self.add_task, height=40, corner_radius=10)
        self.add_button.pack(side="left", padx=5)

        # Filter Dropdown
        filter_frame = ctk.CTkFrame(self, corner_radius=10)
        filter_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(filter_frame, text="Filter by Status:").pack(side="left", padx=5)
        self.filter_dropdown = ctk.CTkComboBox(filter_frame, values=["All", "Open", "In Progress", "Done"],
                                               command=self.on_filter_change, width=150,
                                               fg_color="white", text_color="black", dropdown_text_color="black", dropdown_fg_color="white")
        self.filter_dropdown.set("All")
        self.filter_dropdown.pack(side="left", padx=5)

        # Task Counters
        self.counter_label = ctk.CTkLabel(self, text="")
        self.counter_label.pack(pady=5)

        # Progress Label
        self.progress_label = ctk.CTkLabel(self, text="Progress: 0%")
        self.progress_label.pack(pady=5)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate")
        self.progress_bar.pack(pady=5, padx=10, fill="x")

        # Task List
        self.task_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.task_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.display_tasks()

    def update_time(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=f"Current Time: {now}")
        self.after(1000, self.update_time)

    def add_task(self):
        task_text = self.task_entry.get().strip()
        priority = self.priority_dropdown.get()
        if task_text:
            task = {"text": task_text, "status": "Open", "priority": priority}
            self.tasks.append(task)
            self.task_entry.delete(0, "end")
            self.save_tasks()
            self.display_tasks()
        else:
            messagebox.showwarning("Warning", "Please enter a task!")

    def on_filter_change(self, value):
        self.filter_status = None if value == "All" else value
        self.display_tasks()

    def update_status(self, index, new_status):
        self.tasks[index]["status"] = new_status
        self.save_tasks()
        self.display_tasks()

    def delete_task(self, index):
        del self.tasks[index]
        self.save_tasks()
        self.display_tasks()

    def edit_task(self, index):
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Task")
        edit_window.geometry("300x150")
        edit_entry = ctk.CTkEntry(edit_window, placeholder_text="Edit task text")
        edit_entry.insert(0, self.tasks[index]["text"])
        edit_entry.pack(pady=10, padx=10)

        def save_edit():
            new_text = edit_entry.get().strip()
            if new_text:
                self.tasks[index]["text"] = new_text
                self.save_tasks()
                self.display_tasks()
                edit_window.destroy()

        save_button = ctk.CTkButton(edit_window, text="Save", command=save_edit, corner_radius=10)
        save_button.pack(pady=5)

    def display_tasks(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        total = len(self.tasks)
        done = len([t for t in self.tasks if t["status"] == "Done"])

        # Update counters and progress
        self.counter_label.configure(text=f"Tasks: {total} | Done: {done} | Open: {total - done}")
        if total > 0:
            progress = done / total
            self.progress_bar.set(progress)
            percent = int(progress * 100)
        else:
            self.progress_bar.set(0)
            percent = 0
        self.progress_label.configure(text=f"Progress: {percent}%")

        for index, task in enumerate(self.tasks):
            if self.filter_status and task["status"] != self.filter_status:
                continue

            frame = ctk.CTkFrame(self.task_frame, corner_radius=10)
            frame.pack(fill="x", pady=5, padx=5)

            bg_color = STATUS_COLORS[task["status"]]
            priority_color = PRIORITY_COLORS.get(task.get("priority", "Medium"), "gray")

            label = ctk.CTkLabel(frame, text=f"{task['text']} (Priority: {task.get('priority', 'Medium')})",
                                 fg_color=bg_color, corner_radius=10, width=400, anchor="w")
            label.pack(side="left", padx=5, pady=5, fill="x", expand=True)

            priority_label = ctk.CTkLabel(frame, text=task.get("priority", "Medium"), fg_color=priority_color, corner_radius=5, width=60)
            priority_label.pack(side="right", padx=2)

            status_dropdown = ctk.CTkComboBox(frame, values=["Open", "In Progress", "Done"], width=120,
                                              command=lambda new_status, i=index: self.update_status(i, new_status),
                                              fg_color="white", text_color="black", dropdown_text_color="black", dropdown_fg_color="white")
            status_dropdown.set(task["status"])
            status_dropdown.pack(side="right", padx=5)

            edit_button = ctk.CTkButton(frame, text="Edit", width=60, corner_radius=10, command=lambda i=index: self.edit_task(i))
            edit_button.pack(side="right", padx=2)

            delete_button = ctk.CTkButton(frame, text="Delete", width=70, corner_radius=10, fg_color="red", command=lambda i=index: self.delete_task(i))
            delete_button.pack(side="right", padx=2)

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r") as f:
                    content = f.read().strip()
                    if not content:
                        return []
                    return json.loads(content)
            except (json.JSONDecodeError, IOError):
                print("Warning: Failed to load tasks. File might be corrupted.")
                return []
        return []

    def save_tasks(self):
        with open(TASKS_FILE, "w") as f:
            json.dump(self.tasks, f, indent=4)

if __name__ == "__main__":
    app = TaskManager()
    app.mainloop()
