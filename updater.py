import os
import requests
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk

# ▼ GitHubの設定を変えてね ▼
GITHUB_API = "https://api.github.com/repos/G-Est/test_tool/releases/latest"
TOOL_NAME = "task_manager.exe"
TEMP_FILE = "tool_updater.exe"

class UpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Updating...")
        self.root.geometry("400x180")
        self.root.resizable(False, False)

        self.label = tk.Label(root, text="Checking for updates...", font=("Arial", 11))
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(root, length=350, mode='determinate')
        self.progress.pack(pady=10)

        self.ok_btn = tk.Button(root, text="OK", state="disabled", command=root.quit)
        self.retry_btn = tk.Button(root, text="Retry", state="disabled", command=self.retry)

        self.ok_btn.pack(side="right", padx=10, pady=10)
        self.retry_btn.pack(side="right", pady=10)

        self.root.after(100, self.start_update)

    def start_update(self):
        try:
            download_url = self.get_github_asset_url()
            self.label.config(text="Downloading latest version...")
            self.download_file(download_url, TEMP_FILE)
            self.replace_file()
            self.label.config(text="Update completed successfully!")
            self.ok_btn.config(state="normal")
            self.launch_tool()
        except Exception as e:
            self.label.config(text=f"Error: {e}")
            self.retry_btn.config(state="normal")

    def get_github_asset_url(self):
        response = requests.get(GITHUB_API)
        if response.status_code != 200:
            raise Exception("Failed to get release info")
        release_info = response.json()

        for asset in release_info.get("assets", []):
            if asset["name"] == TOOL_NAME:
                return asset["browser_download_url"]
        raise Exception(f"{TOOL_NAME} not found in release")

    def download_file(self, url, filename):
        response = requests.get(url, stream=True)
        total_length = int(response.headers.get('content-length', 0))

        with open(filename, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress_percent = int(100 * downloaded / total_length)
                    self.progress['value'] = progress_percent
                    self.root.update()

    def replace_file(self):
        if os.path.exists(TOOL_NAME):
            os.remove(TOOL_NAME)
        shutil.move(TEMP_FILE, TOOL_NAME)

    def launch_tool(self):
        subprocess.Popen([TOOL_NAME], shell=True)

    def retry(self):
        self.retry_btn.config(state="disabled")
        self.label.config(text="Retrying...")
        self.progress["value"] = 0
        self.root.after(500, self.start_update)

def main():
    root = tk.Tk()
    app = UpdaterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
