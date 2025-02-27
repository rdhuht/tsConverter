import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import os
import sys
import threading
import queue

# 检查 ffmpeg 是否可用
def check_ffmpeg():
    ffmpeg_path = os.path.join(os.getcwd(), 'src', 'ffmpeg')  # ffmpeg 相对路径
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    else:
        return None

# 更新进度条的函数
def update_progress(progress_value):
    progress_bar['value'] = progress_value
    root.update_idletasks()

# 转换视频文件的线程函数
def convert_video_thread(input_file, output_file, ffmpeg_path, output_format, progress_queue):
    try:
        # 使用 FFmpeg 执行转换命令并获取输出进度
        command = [ffmpeg_path, "-i", input_file, "-c:v", "libx264", "-c:a", "aac", "-progress", "pipe:1", output_file]
        
        # 启动子进程
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # 处理进度信息
        while process.poll() is None:
            line = process.stdout.readline()
            if 'frame=' in line:  # 获取进度行
                # 从进度信息中提取已处理的帧数
                frame_info = line.strip().split('=')[-1].strip()
                if frame_info.isdigit():
                    frame_count = int(frame_info)
                    progress_queue.put(min(frame_count, 100))
        
        # 等待 FFmpeg 完成转换
        process.communicate()

        # 转换结束后返回
        progress_queue.put("done")
    except subprocess.CalledProcessError:
        progress_queue.put("error")

# 转换视频文件并显示进度
def convert_video():
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    output_format = format_var.get()

    if not input_file:
        messagebox.showerror("错误", "请选择要转换的 TS 文件！")
        return

    if output_format == "请选择格式":
        messagebox.showerror("错误", "请选择转换后的格式！")
        return

    ffmpeg_path = check_ffmpeg()
    if not ffmpeg_path:
        messagebox.showerror("错误", "无法找到 FFmpeg 可执行文件，请确保 'src/ffmpeg' 存在。")
        return

    # 如果没有选择目标路径，则默认使用与源文件相同的路径和文件名
    if not output_file:
        output_dir = os.path.dirname(input_file)
        output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.' + output_format)
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, output_file)

    # 更新进度条
    progress_bar['value'] = 0
    root.update_idletasks()

    # 创建队列用于线程间通信
    progress_queue = queue.Queue()

    # 启动视频转换线程
    thread = threading.Thread(target=convert_video_thread, args=(input_file, output_file, ffmpeg_path, output_format, progress_queue))
    thread.daemon = True  # 主程序退出时自动退出该线程
    thread.start()

    # 线程循环监听进度信息
    def check_progress():
        try:
            while True:
                progress = progress_queue.get_nowait()
                if isinstance(progress, int):
                    update_progress(progress)  # 更新进度条
                elif progress == "done":
                    messagebox.showinfo("成功", f"文件转换成功！保存为：{output_file}")
                    if messagebox.askyesno("打开文件夹", "转换完成！是否打开文件夹？"):
                        open_folder(os.path.dirname(output_file))
                    return
                elif progress == "error":
                    messagebox.showerror("错误", "转换过程中出现问题，请检查输入和输出文件路径。")
                    return
        except queue.Empty:
            root.after(100, check_progress)  # 等待 100ms 后继续检查进度

    # 开始检查进度
    check_progress()

# 打开转换后的文件夹
def open_folder(folder_path):
    if sys.platform == "win32":  # Windows
        os.startfile(folder_path)
    elif sys.platform == "darwin":  # macOS
        subprocess.run(["open", folder_path])
    else:  # Linux
        subprocess.run(["xdg-open", folder_path])

# 选择 TS 文件
def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("TS 文件", "*.ts")])
    if file_path:
        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, file_path)
        
        # 设置默认保存路径为与输入文件相同的目录
        default_output_path = os.path.dirname(file_path)
        default_output_file = os.path.splitext(os.path.basename(file_path))[0] + '.' + format_var.get()
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, os.path.join(default_output_path, default_output_file))

# 选择保存路径
def select_output_file():
    input_file = input_file_entry.get()
    if input_file:
        default_output_file = os.path.splitext(os.path.basename(input_file))[0] + '.' + format_var.get()
        default_output_path = os.path.dirname(input_file)
    else:
        default_output_file = 'output.mp4'
        default_output_path = os.getcwd()

    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 文件", "*.mp4"), ("AVI 文件", "*.avi"), ("MKV 文件", "*.mkv"), ("所有文件", "*.*")], initialdir=default_output_path, initialfile=default_output_file)
    if file_path:
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, file_path)

# 当选择格式后更新目标路径的扩展名
def update_output_extension(*args):
    input_file = input_file_entry.get()
    output_format = format_var.get()

    if input_file and output_format != "请选择格式":
        output_file = os.path.splitext(input_file)[0] + '.' + output_format
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, output_file)

# 主程序
root = tk.Tk()
root.title("TS 视频转换器")

# 输入文件选择
input_file_label = tk.Label(root, text="选择 TS 文件：")
input_file_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

input_file_entry = tk.Entry(root, width=40)
input_file_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

input_file_button = tk.Button(root, text="浏览", command=select_input_file)
input_file_button.grid(row=0, column=2, padx=10, pady=5)

# 输出文件选择
output_file_label = tk.Label(root, text="保存为：")
output_file_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

output_file_entry = tk.Entry(root, width=40)
output_file_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

output_file_button = tk.Button(root, text="浏览", command=select_output_file)
output_file_button.grid(row=1, column=2, padx=10, pady=5)

# 输出格式选择
format_label = tk.Label(root, text="选择格式：")
format_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

formats = ["请选择格式", "mp4", "avi", "mkv", "flv", "mov", "wmv"]
format_var = tk.StringVar(value="mp4")  # 默认选择 mp4

format_menu = tk.OptionMenu(root, format_var, *formats)
format_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# 绑定格式选择变化
format_var.trace("w", update_output_extension)

# 进度条
progress_label = tk.Label(root, text="转换进度：")
progress_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")

progress_bar = ttk.Progressbar(root, length=300, mode="determinate", maximum=100)
progress_bar.grid(row=3, column=1, padx=10, pady=10, sticky="w")

# 转换按钮
convert_button = tk.Button(root, text="开始转换", command=convert_video)
convert_button.grid(row=4, column=0, columnspan=3, pady=20)

root.mainloop()
