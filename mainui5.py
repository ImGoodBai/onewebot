import tkinter as tk
import subprocess
import threading
import os

class AppManager:
    def __init__(self, root):
        self.root = root
        self.root.title("白话Agent-微信机器人一键运行包")
        self.root.geometry("900x600")  # 扩大窗口尺寸以容纳新的布局

        self.processes = []

        # 配置输入区
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(input_frame, text="输入coze api token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.key_entry = tk.Entry(input_frame, width=60)
        self.key_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(input_frame, text="coze bot_id:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.bot_id_entry = tk.Entry(input_frame, width=60)
        self.bot_id_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # 注意事项
        self.notice_text = tk.Text(input_frame, height=5, width=40, wrap=tk.WORD)
        self.notice_text.grid(row=0, column=2, rowspan=2, padx=10, pady=5)
        self.notice_text.insert(tk.END, "1 运行前确认botid、token已填写，微信版本已更换。2 请以学习目的使用，有封号风险。")
        self.notice_text.config(state=tk.DISABLED)

        self.run_button = tk.Button(root, text="运行", command=self.on_run)
        self.run_button.pack(pady=20)

        # 日志显示区
        log_frame = tk.Frame(root)
        log_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(log_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(log_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="机器人动态").pack(pady=5)
        self.text_area1 = tk.Text(left_frame, height=20, width=60)
        self.text_area1.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(right_frame, text="coze api状态").pack(pady=5)
        self.text_area2 = tk.Text(right_frame, height=20, width=60)
        self.text_area2.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 底部网址
        label = tk.Label(root, text="100agent.cn", fg="blue", cursor="hand2")
        label.pack(pady=10)
        label.bind("<Button-1>", lambda e: os.system("start http://100agent.cn"))


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
