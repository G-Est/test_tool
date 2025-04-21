import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime
import requests
import zipfile
import io
import shutil
import sys
import subprocess
from packaging import version

DATA_FILE = "tasks.json"
UPDATE_CHECK_URL = "https://api.github.com/repos/G-Est/test_tool/releases/latest"
CURRENT_VERSION = "1.0.0"  # 当前版本号，需要与GitHub发布的版本对应

class UpdateManager:
    @staticmethod
    def check_for_updates():
        try:
            response = requests.get(UPDATE_CHECK_URL)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release['tag_name']
            
            if version.parse(latest_version) > version.parse(CURRENT_VERSION):
                return latest_release
            return None
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None

    @staticmethod
    def download_and_apply_update(release_info):
        try:
            # 获取zipball下载URL
            zip_url = release_info['zipball_url']
            response = requests.get(zip_url)
            response.raise_for_status()
            
            # 解压更新文件
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                # 创建临时目录
                temp_dir = "temp_update"
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)
                
                # 解压到临时目录
                zip_ref.extractall(temp_dir)
                
                # 获取解压后的根目录（GitHub会创建一个包含版本号的子目录）
                extracted_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
                
                # 复制文件到当前目录（排除特定文件如数据文件）
                for item in os.listdir(extracted_dir):
                    s = os.path.join(extracted_dir, item)
                    d = os.path.join(".", item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        # 跳过数据文件和特定配置文件
                        if item not in [DATA_FILE, 'config.json']:
                            shutil.copy2(s, d)
                
                # 清理临时文件
                shutil.rmtree(temp_dir)
                
                return True
        except Exception as e:
            print(f"Error applying update: {e}")
            return False

    @staticmethod
    def restart_application():
        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        sys.exit()

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Daily Task Manager v{CURRENT_VERSION}")
        self.tasks = []

        # 添加菜单栏
        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Check for Updates", command=self.check_updates)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        root.config(menu=self.menu_bar)

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        # 输入字段 (保持不变)
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

        # 按钮 (保持不变)
        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=3, column=0, columnspan=2, sticky="w")

        self.delete_button = tk.Button(self.frame, text="Delete Completed", command=self.delete_done)
        self.delete_button.grid(row=3, column=2, columnspan=2, sticky="e")

        # 任务列表显示 (保持不变)
        self.task_frame = tk.Frame(self.frame)
        self.task_frame.grid(row=4, column=0, columnspan=6, pady=10)

        self.load_tasks()

    def check_updates(self):
        """检查更新并在有新版本时提示用户"""
        update_window = tk.Toplevel(self.root)
        update_window.title("Software Update")
        update_window.geometry("400x200")
        
        label = tk.Label(update_window, text="Checking for updates...")
        label.pack(pady=20)
        
        progress = ttk.Progressbar(update_window, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        def do_check():
            latest_release = UpdateManager.check_for_updates()
            
            if latest_release is None:
                label.config(text="You are using the latest version.")
            else:
                latest_version = latest_release['tag_name']
                label.config(text=f"New version {latest_version} is available!\n\nRelease notes:\n{latest_release.get('body', 'No description provided.')}")
                
                # 添加更新按钮
                update_btn = tk.Button(update_window, text="Update Now", 
                                     command=lambda: self.perform_update(latest_release, update_window))
                update_btn.pack(pady=10)
            
            progress.stop()
            progress.pack_forget()
        
        # 在后台线程中执行检查
        self.root.after(100, do_check)

    def perform_update(self, release_info, update_window):
        """执行更新过程"""
        for widget in update_window.winfo_children():
            widget.destroy()
        
        label = tk.Label(update_window, text="Downloading and applying update...")
        label.pack(pady=20)
        
        progress = ttk.Progressbar(update_window, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        def do_update():
            success = UpdateManager.download_and_apply_update(release_info)
            progress.stop()
            
            if success:
                label.config(text="Update successful! The application will now restart.")
                update_btn = tk.Button(update_window, text="Restart Now", 
                                     command=UpdateManager.restart_application)
                update_btn.pack(pady=10)
            else:
                label.config(text="Update failed. Please try again later.")
        
        self.root.after(100, do_update)

    # 以下方法保持不变...
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