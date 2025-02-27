import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

# 检查 ffmpeg 是否安装
def check_ffmpeg():
    try:
        # 尝试运行 ffmpeg -version 命令，如果能够正常返回，则表示已安装
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

# 转换函数
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

    if not check_ffmpeg():
        messagebox.showerror("错误", "您的电脑上没有安装 FFmpeg，请先安装 FFmpeg。")
        return

    # 如果没有选择目标路径，则默认使用与源文件相同的路径和文件名
    if not output_file:
        output_dir = os.path.dirname(input_file)
        output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.' + output_format)
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, output_file)

    # 使用 FFmpeg 执行转换命令
    try:
        command = f'ffmpeg -i "{input_file}" -c:v libx264 -c:a aac "{output_file}"'
        subprocess.run(command, shell=True, check=True)
        messagebox.showinfo("成功", f"文件转换成功！保存为：{output_file}")
    except subprocess.CalledProcessError:
        messagebox.showerror("错误", "转换过程中出现问题，请检查输入和输出文件路径。")

# 选择文件函数
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

# 选择保存路径函数
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

# 转换按钮
convert_button = tk.Button(root, text="开始转换", command=convert_video)
convert_button.grid(row=3, column=0, columnspan=3, pady=20)

root.mainloop()
