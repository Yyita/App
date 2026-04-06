import tkinter as tk
from tkinter import ttk
import pyperclip
import secrets
import string
from math import log2
import requests
from hashlib import sha1


TITLE = "密码生成器"
LENGTH_FLOOR = 2
LENGTH_CAP = 99


class Default:
    LENGTH = 17
    CUSTOM_CHARS = "!@#$"
    LOWERCASE_VALUE = 1
    UPPERCASE_VALUE = 1
    DIGITS_VALUE = 1
    CUSTOM_VALUE = 1
    AUTO_VALUE = 1


class Text:
    LENGTH = "长度"
    CHARSET = "字符集"
    LOWERCASE = "小写字母"
    UPPERCASE = "大写字母"
    DIGITS = "数字"
    CUSTOM = "自定义"
    GENERATE = "生成"
    COPY = "复制"
    SAFETY_ASSESSMENT = "安全性评估"
    ASSESSMENT = "评估"
    AUTO = "自动"
    READONLY = "readonly"
    NORMAL = "normal"


class Template:
    ENTROPY = "密码熵： {} bits"
    BREACH_COUNT = "在已知被泄露密码中有 {} 个与此相同"


class Colors:
    LIGHT_GREEN = "#80FF80"
    LIGHT_YELLOW = "#FFFF80"
    LIGHT_BLUE = "#80FFFF"


class Fonts:
    TITLE = ("TkDefaultFont", 11)
    TEXT = ("TkDefaultFont", 10)
    ENTRY = ("Fira code", 11)


session = requests.Session()

def number_of_password_breaches(password: str):
    password_sha1 = sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = password_sha1[:5], password_sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = session.get(url, timeout=5)
    for line in response.iter_lines():
        if line[:35].decode() == suffix: 
            return int(line[36:].decode())
    return 0

def copy_password() -> None:
    pyperclip.copy(password_entry.get())

def get_unique() -> list[str]:
    unique = []
    if lowercase_var.get():
        unique.extend(string.ascii_lowercase)
    if uppercase_var.get():
        unique.extend(string.ascii_uppercase)
    if digits_var.get():
        unique.extend(string.digits)
    if custom_var.get():
        unique.extend(custom_entry.get())
    return list(set(unique))

def assessment():
    length = int(length_spinbox.get())
    unique_size = len(get_unique())
    entropy = length * log2(unique_size)
    password_entropy_label.config(text=Template.ENTROPY.format(f"{entropy:.2f}"))

    try:
        breaches_count = number_of_password_breaches(password_entry.get())
    except Exception:
        breaches_count = "?"
    number_of_breaches_label.config(text=Template.BREACH_COUNT.format(breaches_count))

def generate_password() -> None:
    unique = get_unique()
    if not unique:
        return

    length = int(length_spinbox.get())
    password = ''.join(secrets.choice(unique) for _ in range(length))
    password_entry.config(state=Text.NORMAL)
    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)
    password_entry.config(state=Text.READONLY)

    if not auto_var.get():
        password_entropy_label.config(text=Template.ENTROPY.format("?"))
        number_of_breaches_label.config(text=Template.BREACH_COUNT.format("?"))
    else:
        assessment()


root = tk.Tk()
root.title(TITLE)
root.resizable(False, False)

frame = tk.Frame(root)

frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
frame.grid_columnconfigure((0,), weight=1)

config_area = tk.Frame(frame)
password_area = tk.Frame(frame)
control_area = tk.Frame(frame)
assessment_area = tk.Frame(frame)

config_area.grid(row=0, column=0, sticky="we", pady=(0, 2))
password_area.grid(row=1, column=0, pady=2)
control_area.grid(row=2, column=0, sticky="we", pady=2)
assessment_area.grid(row=3, column=0, sticky="we", pady=(2, 0))

config_area.grid_rowconfigure((0, 1), weight=1)
config_area.grid_columnconfigure((0, 1), weight=1)
password_area.grid_rowconfigure((0, 1), weight=1)
password_area.grid_columnconfigure((0,), weight=1)
control_area.grid_rowconfigure((0, 1), weight=1)
control_area.grid_columnconfigure((0, 1), weight=1)
assessment_area.grid_rowconfigure((0, 1), weight=1)
assessment_area.grid_columnconfigure((0,), weight=1)

length_text_label = tk.Label(config_area, text=Text.LENGTH, font=Fonts.TITLE)
length_spinbox = ttk.Spinbox(config_area, from_=LENGTH_FLOOR, to=LENGTH_CAP, width=4, state=Text.READONLY, justify=tk.CENTER)
length_spinbox.set(Default.LENGTH)
charset_text_label = tk.Label(config_area, text=Text.CHARSET, font=Fonts.TITLE)
option_frame = tk.Frame(config_area)

option_frame.grid_rowconfigure((0, 1), weight=1)
option_frame.grid_columnconfigure((0, 1, 2), weight=1)

length_text_label.grid(row=0, column=0, padx=(0, 10), pady=5)
length_spinbox.grid(row=0, column=1, sticky="w", pady=5)
charset_text_label.grid(row=1, column=0, padx=(0, 10), pady=(0, 15))
option_frame.grid(row=1, column=1, sticky="w", pady=5)

lowercase_var = tk.IntVar(value=Default.LOWERCASE_VALUE) 
uppercase_var = tk.IntVar(value=Default.UPPERCASE_VALUE)
digits_var = tk.IntVar(value=Default.DIGITS_VALUE)
custom_var = tk.IntVar(value=Default.CUSTOM_VALUE)

custom_entry = ttk.Entry(option_frame, width=13, font=Fonts.ENTRY)
custom_entry.insert(0, Default.CUSTOM_CHARS)
custom_entry_x_scrollbar = ttk.Scrollbar(option_frame, orient=tk.HORIZONTAL, command=custom_entry.xview)
custom_entry.config(xscrollcommand=custom_entry_x_scrollbar.set)
lowercase_checkbutton = ttk.Checkbutton(option_frame, text=Text.LOWERCASE, variable=lowercase_var)
uppercase_checkbutton = ttk.Checkbutton(option_frame, text=Text.UPPERCASE, variable=uppercase_var)
digits_checkbutton = ttk.Checkbutton(option_frame, text=Text.DIGITS, variable=digits_var)
custom_checkbutton = ttk.Checkbutton(option_frame, text=Text.CUSTOM, variable=custom_var)

lowercase_checkbutton.grid(row=0, column=0, padx=(0, 5))
uppercase_checkbutton.grid(row=0, column=1, padx=5)
digits_checkbutton.grid(row=0, column=2, padx=(5, 0))
custom_checkbutton.grid(row=1, column=0, sticky="w")
custom_entry.grid(row=1, column=1, columnspan=2, sticky="nswe", padx=(5, 0))
custom_entry_x_scrollbar.grid(row=2, column=1, columnspan=2, sticky="we", padx=(5, 0))

password_entry = ttk.Entry(password_area, state=Text.READONLY, width=17, font=Fonts.ENTRY)
password_entry_x_scrollbar = ttk.Scrollbar(password_area, orient=tk.HORIZONTAL, command=password_entry.xview)
password_entry.config(xscrollcommand=password_entry_x_scrollbar.set)

password_entry.grid(row=0, column=0, sticky="nswe")
password_entry_x_scrollbar.grid(row=1, column=0, sticky="we")

generate_button = tk.Button(control_area, command=generate_password, text=Text.GENERATE, bg=Colors.LIGHT_GREEN, bd=1, font=Fonts.TITLE, width=5)
copy_button = tk.Button(control_area, command=copy_password, text=Text.COPY, bg=Colors.LIGHT_YELLOW, bd=1, font=Fonts.TITLE, width=5)
assessment_button = tk.Button(control_area, command=assessment, text=Text.ASSESSMENT, bg=Colors.LIGHT_BLUE, bd=1, font=Fonts.TITLE, width=5)
auto_var = tk.IntVar(value=Default.AUTO_VALUE)
auto_checkbutton = ttk.Checkbutton(control_area, text=Text.AUTO, variable=auto_var)

generate_button.grid(row=0, column=0, sticky="e", padx=5, pady=5)
copy_button.grid(row=0, column=1, sticky="w", padx=5, pady=5)
assessment_button.grid(row=1, column=0, sticky="e", padx=5, pady=5)
auto_checkbutton.grid(row=1, column=1, sticky="w", padx=5, pady=5)

assessment_text_label = tk.Label(assessment_area, text=Text.SAFETY_ASSESSMENT, font=Fonts.TITLE)
assessment_result_frame = tk.Frame(assessment_area, relief="solid", borderwidth=1)

assessment_text_label.grid(row=0, column=0, sticky="w", pady=5)
assessment_result_frame.grid(row=1, column=0, sticky="we")

password_entropy_label = tk.Label(assessment_result_frame, text=Template.ENTROPY.format("?"), font=Fonts.TEXT)
number_of_breaches_label = tk.Label(assessment_result_frame, text=Template.BREACH_COUNT.format("?"), font=Fonts.TEXT)

password_entropy_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
number_of_breaches_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

root.mainloop()