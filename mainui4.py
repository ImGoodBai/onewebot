import tkinter as tk
import subprocess
import threading
import os

class AppManager:
    def __init__(self, root):
        self.root = root
        self.root.title("配置设置")
        self.root.geometry("800x400")  # 扩大窗口尺寸以容纳两个text组件

        self.processes = []

        tk.Label(root, text="输入coze api token:").pack(pady=10)
        self.key_entry = tk.Entry(root, width=40)
        self.key_entry.pack(pady=10)

        tk.Label(root, text="coze bot_id:").pack(pady=10)
        self.bot_id_entry = tk.Entry(root, width=40)
        self.bot_id_entry.pack(pady=10)

        self.run_button = tk.Button(root, text="运行", command=self.on_run)
        self.run_button.pack(pady=20)

        self.text_area1 = tk.Text(root, height=15, width=50)
        self.text_area1.pack(side=tk.LEFT, padx=10, pady=10)

        self.text_area2 = tk.Text(root, height=15, width=50)
        self.text_area2.pack(side=tk.LEFT, padx=10, pady=10)

        self.load_config()

    def load_config(self):
        env_path = "./coze2openai/.env"
        key = ""
        bot_id = ""
        if os.path.exists(env_path):
            with open(env_path, 'r') as file:
                for line in file:
                    if line.startswith("KEY="):
                        key = line.strip().split('=')[1]
                    elif line.startswith("BOT_ID="):
                        bot_id = line.strip().split('=')[1]

        self.key_entry.insert(0, key)
        self.bot_id_entry.insert(0, bot_id)

    def update_env_file(self, key, value):
        env_path = "./coze2openai/.env"
        lines = []
        key_found = False
        with open(env_path, 'r') as file:
            lines = file.readlines()

        with open(env_path, 'w') as file:
            for line in lines:
                if line.startswith(f"{key}="):
                    file.write(f"{key}={value}\n")
                    key_found = True
                else:
                    file.write(line)
            if not key_found:
                file.write(f"{key}={value}\n")

    def save_config(self):
        key = self.key_entry.get()
        bot_id = self.bot_id_entry.get()
        self.update_env_file('BOT_ID', bot_id)
        self.update_env_file('KEY', key)

    def on_run(self):
        if self.run_button['text'] == "运行":
            self.save_config()
            self.start_apps()
            self.run_button.config(text="停止", command=self.on_stop)
        else:
            self.on_stop()

    def start_apps(self):
        self.text_area1.insert(tk.END, "Starting main.py...\n")
        self.text_area1.see(tk.END)
        self.text_area2.insert(tk.END, "Starting main2.py...\n")
        self.text_area2.see(tk.END)
        
        threading.Thread(target=self.run_app, args=("python.exe .\\main.py -c 2", self.text_area1)).start()
        threading.Thread(target=self.run_app, args=("python.exe .\\coze2openai\\main2.py", self.text_area2)).start()

    def run_app(self, command, text_area):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.processes.append(process)
        self.redirect_output(process, text_area)

    def redirect_output(self, process, text_area):
        def read_output(pipe):
            while True:
                output = pipe.readline()
                if process.poll() is not None:
                    break
                if output:
                    text_area.insert(tk.END, output.decode('gbk', errors='ignore'))
                    text_area.see(tk.END)

        threading.Thread(target=read_output, args=(process.stdout,)).start()
        threading.Thread(target=read_output, args=(process.stderr,)).start()

    def on_stop(self):
        for process in self.processes:
            process.terminate()
        self.processes.clear()
        self.text_area1.insert(tk.END, "Applications stopped.\n")
        self.text_area1.see(tk.END)
        self.text_area2.insert(tk.END, "Applications stopped.\n")
        self.text_area2.see(tk.END)
        self.run_button.config(text="运行", command=self.on_run)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppManager(root)
    root.mainloop()
