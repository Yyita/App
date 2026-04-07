import tkinter as tk
import pyperclip
from typing import Optional, Literal


# 辅助函数
def is_listbox_empty(listbox: tk.Listbox) -> bool:
    return listbox.size() == 0

# 列表项相关功能
def add_listItem(event: Optional[tk.Event] = None) -> None:
    editor = EditorWindow(root)

    if editor.result is not None:
        listbox.insert(tk.END, editor.result)
        contentMenu.entryconfigure("删除", state=tk.NORMAL)
        contentMenu.entryconfigure("清空", state=tk.NORMAL)

def clear_listItem(event: Optional[tk.Event] = None) -> None:
    if is_listbox_empty(listbox):
        return

    listbox.delete(0, tk.END)
    contentMenu.entryconfigure("删除", state=tk.DISABLED)
    contentMenu.entryconfigure("清空", state=tk.DISABLED)

def edit_listItem(event: Optional[tk.Event] = None) -> None:
    selectedIndexs = listbox.curselection()

    if selectedIndexs:
        index = selectedIndexs[0]
        content = listbox.get(index)
        editor = EditorWindow(root, content=content)

        if editor.result is not None:
            listbox.delete(index)
            listbox.insert(index, editor.result)

def copy_listItem(event: Optional[tk.Event] = None) -> Literal["break"]:
    selectedIndexs = listbox.curselection()

    if selectedIndexs:
        content = listbox.get(selectedIndexs[0])
        pyperclip.copy(content)

    return "break"

def delete_listItem(event: Optional[tk.Event] = None) -> None:
    selectedIndexs = listbox.curselection()

    if selectedIndexs:
        listbox.delete(selectedIndexs[0])

        if is_listbox_empty(listbox):
            contentMenu.entryconfigure("删除", state=tk.DISABLED)
            contentMenu.entryconfigure("清空", state=tk.DISABLED)


class EditorWindow(tk.Toplevel):
    """编辑器窗口"""

    def __init__(self, root: tk.Tk, *, content: Optional[str] = None) -> None:
        super().__init__(root)
        self.title("条目编辑器")
        self.geometry("300x200")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.transient(root)
        self.grab_set()

        # 根框架
        self.rootFrame = tk.Frame(self)
        self.rootFrame.grid_rowconfigure((0,), weight=1)
        self.rootFrame.grid_rowconfigure((1,), weight=0)
        self.rootFrame.grid_columnconfigure((0,), weight=1)
        self.rootFrame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # 文本框框架、按钮框架
        self.textboxFrame = tk.Frame(self.rootFrame)
        self.buttonFrame = tk.Frame(self.rootFrame)

        self.textboxFrame.grid_rowconfigure((0,), weight=1)
        self.textboxFrame.grid_columnconfigure((0,), weight=1)
        self.buttonFrame.grid_rowconfigure((0,), weight=1)
        self.buttonFrame.grid_columnconfigure((0, 1), weight=1)

        self.textboxFrame.grid(row=0, column=0, sticky=tk.NSEW)
        self.buttonFrame.grid(row=1, column=0, sticky=tk.EW, pady=(15, 0))

        # 文本框、垂直滚动条
        self.textbox = tk.Text(self.textboxFrame, font=("Fira Code", 13), width=1, height=1)
        self.y_scrollbar = tk.Scrollbar(self.textboxFrame, orient=tk.VERTICAL, command=self.textbox.yview)

        self.textbox.focus_set()
        self.textbox.config(yscrollcommand=self.y_scrollbar.set)
        if content is not None:
            self.textbox.insert(tk.END, content)

        self.textbox.grid(row=0, column=0, sticky=tk.NSEW)
        self.y_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 确认按钮、取消按钮
        self.okButton = tk.Button(self.buttonFrame, text="确认", command=self._on_ok, bd=1, width=6)
        self.cancelButton = tk.Button(self.buttonFrame, text="取消", command=self.destroy, bd=1, width=6)

        self.okButton.grid(row=0, column=0)
        self.cancelButton.grid(row=0, column=1)

        # 初始化结果并等待操作
        self.result = None
        self.wait_window()

    def _on_ok(self) -> None:
        """[确认]按钮的回调函数"""
        self.result = self.textbox.get("1.0", "end-1c")
        self.destroy()


# 根窗口
root = tk.Tk()
root.title("文本剪贴板")
root.geometry("300x400")
root.iconphoto(True, tk.PhotoImage(width=1, height=1))
root.resizable(False, False)
root.attributes("-topmost", True)

# 根框架
rootFrame = tk.Frame(root)
rootFrame.grid_rowconfigure(0, weight=1)
rootFrame.grid_columnconfigure(0, weight=1)
rootFrame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# 上下文菜单
def show_contentMenu(event: tk.Event) -> None:
    # 选区功能的启用/禁用
    if not listbox.curselection():
        contentMenu.entryconfigure("编辑", state=tk.DISABLED)
        contentMenu.entryconfigure("复制", state=tk.DISABLED)
        contentMenu.entryconfigure("删除", state=tk.DISABLED)
    else:
        contentMenu.entryconfigure("编辑", state=tk.NORMAL)
        contentMenu.entryconfigure("复制", state=tk.NORMAL)
        contentMenu.entryconfigure("删除", state=tk.NORMAL)

    # 列表项功能的启用/禁用
    if is_listbox_empty(listbox):
        contentMenu.entryconfigure("清空", state=tk.DISABLED)
    else:
        contentMenu.entryconfigure("清空", state=tk.NORMAL)

    contentMenu.post(event.x_root, event.y_root)

contentMenu = tk.Menu(rootFrame, tearoff=False)
contentMenu.add_command(label="新建", command=add_listItem, accelerator="Ctrl+N")
contentMenu.add_separator()
contentMenu.add_command(label="编辑", command=edit_listItem, state=tk.DISABLED, accelerator="Ctrl+E")
contentMenu.add_command(label="复制", command=copy_listItem, state=tk.DISABLED, accelerator="Ctrl+C")
contentMenu.add_command(label="删除", command=delete_listItem, state=tk.DISABLED, accelerator="Delete")
contentMenu.add_separator()
contentMenu.add_command(label="清空", command=clear_listItem, state=tk.DISABLED, accelerator="Ctrl+Delete")

# 列表框框架
listboxFrame = tk.Frame(rootFrame)

listboxFrame.grid_rowconfigure(0, weight=1)
listboxFrame.grid_columnconfigure(0, weight=1)

listboxFrame.grid(row=0, column=0, sticky=tk.NSEW)

listbox = tk.Listbox(listboxFrame, font=("Fira Code", 13), exportselection=False, width=1, height=1)
x_scrollbar = tk.Scrollbar(listboxFrame, orient=tk.HORIZONTAL, command=listbox.xview)
y_scrollbar = tk.Scrollbar(listboxFrame, orient=tk.VERTICAL, command=listbox.yview)

listbox.config(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
listbox.bind("<Button-3>", show_contentMenu)
listbox.bind("<Double-Button-1>", edit_listItem)
listbox.bind("<Control-e>", edit_listItem)
listbox.bind("<Control-E>", edit_listItem)
listbox.bind("<Button-2>", copy_listItem)
listbox.bind("<Control-c>", copy_listItem)
listbox.bind("<Control-C>", copy_listItem)
listbox.bind("<Control-n>", add_listItem)
listbox.bind("<Control-N>", add_listItem)
listbox.bind("<Delete>", delete_listItem)
listbox.bind("<Control-Delete>", clear_listItem)

listbox.grid(row=0, column=0, sticky=tk.NSEW)
x_scrollbar.grid(row=1, column=0, sticky=tk.EW)
y_scrollbar.grid(row=0, column=1, sticky=tk.NS)

# 进入主循环
root.mainloop()