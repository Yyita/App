# 资源管理器的半成品，暂未考虑跨平台。
# 由于是半成品，某些操作可能造成破坏性行为，请勿轻易尝试边缘操作。
# 本程序已终止开发。

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Literal
from collections import abc
from functools import partial, wraps
from enum import Enum, auto
import os
import pyperclip
import send2trash
import shutil
import datetime
import time
import math


TITLE = "资源管理器"
NAME = "name"
CATEGORY = "category"
HEADINGS = "headings"
FOLDER = "文件夹"
UNKNOWN = "未知"
BREAK = "break"
BreakType = Literal["break"]

# 自定义的拓展名描述
DESCRIPTION = {
    "txt": "文本文档",
    "lnk": "快捷方式",
    "py": "Python 源文件",
    "cpp": "C 源文件",
    "json": "JSON 源文件",
    "go": "Go 源文件",
    "md": "Markdown 文件"
}

# 【新建】菜单选项
NEW_MENU_OPTIONS = [
    ("文本文档", "txt"),
    ("Python 源文件", "py"),
    ("C 源文件", "cpp"),
    ("JSON 源文件", "json"),
    ("Go 源文件", "go"),
    ("Markdown 文件", "md")
]

# Windows 下命名禁用的字符
DISABLE_CHARS = ("\\", "/", ":", "*", "?", '"', "<", ">", "|")

# 中文星期名映射
WEEKDAY_CN_MAP = dict(zip(range(0, 7), ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")))
# 数据单位（进率：1024）
DATA_UNITS = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[INFO] {func.__name__} Args: {args}, Keyword Args: {kwargs}")
        return func(*args, **kwargs)
    return wrapper

class Utils:
    @staticmethod
    def timestamp(mode: Literal['date', 'time', 'datetime'] = "datetime",
                precision: Literal['s', 'ms', 'μs', 'ns'] = "s",
                date_sep: str = "-", time_sep: str = ":") -> str:
        """获取格式化的当前时间戳"""
        # 获取当前时间
        current_time = time.time()
        struct_time = time.localtime(current_time)
        # 提取基本日期、基本时间
        date_part = time.strftime(f"%Y{date_sep}%m{date_sep}%d", struct_time)
        time_part = time.strftime(f"%H{time_sep}%M{time_sep}%S", struct_time)
        # 根据模式格式化结果
        match mode:
            case "date": return date_part
            case "time": template = f"{time_part}"
            case "datetime": template = f"{date_part} {time_part}"
            case _: raise ValueError(f"不受支持的模式：{mode}")
        # 处理小数部分，将其转换成'fff'的模式
        fractional = str(current_time - int(current_time))[2:]
        # 提取精度，返回结果
        match precision:
            case 's': return template
            case 'ms': return f"{template}.{fractional[:3]:0<3}"
            case 'μs': return f"{template}.{fractional[:6]:0<6}"
            case 'ns': return f"{template}.{fractional[:9]:0<9}"
            case _: raise ValueError(f"不支持的精度：{precision}")

    @staticmethod
    def dirCount(directory: str) -> tuple[int, int]:
        """统计「目录」所包含的「文件」和「目录」的数量"""
        fileCount = 0
        dirCount = 0

        for _, dirs, files in os.walk(directory):
            fileCount += len(files)
            dirCount += len(dirs)

        return fileCount, dirCount

    @staticmethod
    def open_in_explorer(path: str | Path, /) -> None:
        os.startfile(path)

    @staticmethod
    def category(path: Path) -> str:
        if path.is_file():
            suffix = path.suffix.lstrip('.')
            default = f"{suffix.upper()} 文件"
            return DESCRIPTION.get(suffix, default)

        if path.is_dir():
            return FOLDER

        return UNKNOWN


class TkUtils:
    @staticmethod
    def center(window: tk.Tk | tk.Toplevel) -> None:
        """Tk/Toplevel 窗口移动到屏幕中心"""
        window.update_idletasks()
        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        # 获取窗口尺寸（不含标题栏、边框）
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        # 定义标题栏、边框占用的像素
        offset_x = 2
        offset_y = 52
        # 计算坐标
        x = (screen_width - window_width - offset_x) // 2
        y = (screen_height - window_height - offset_y) // 2
        # 移动窗口
        window.geometry(f"+{x}+{y}")

    @staticmethod
    def center_on_master(window: tk.Toplevel) -> None:
        """Toplevel 窗口移动到 master 中心"""
        window.update_idletasks()
        master = window.master
        # 获取窗口尺寸
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        # 获取父控件尺寸、坐标
        master_width = master.winfo_width()
        master_height = master.winfo_height()
        master_x = master.winfo_x()
        master_y = master.winfo_y()
        # 计算坐标
        x = master_x - (window_width - master_width) // 2
        y = master_y - (window_height - master_height) // 2
        # 移动窗口
        window.geometry(f"+{x}+{y}")

    @staticmethod
    def center_on_cursor(window: tk.Tk | tk.Toplevel) -> None:
        """Tk/Toplevel 窗口中心移动到光标"""
        window.update_idletasks()
        # 获取光标相对屏幕的坐标
        cursor_x = window.winfo_pointerx()
        cursor_y = window.winfo_pointery()
        # 获取窗口相对屏幕的坐标
        window_x = window.winfo_rootx()
        window_y = window.winfo_rooty()
        # 计算光标相对窗口的坐标
        rel_x = cursor_x - window_x
        rel_y = cursor_y - window_y
        # 计算坐标
        x = rel_x - window.winfo_width() // 2
        y = rel_y - window.winfo_height() // 2
        # 移动窗口
        window.geometry(f"+{x}+{y}")


class Events:
    LEFT_CLICK = "<Button-1>"
    RIGHT_CLICK = "<Button-3>"
    DOUBLE_CLICK  = "<Double-1>"
    ENTER = "<Return>"


class ClipboardMode(Enum):
    CUT = auto()
    COPY = auto()


class Actions:
    BACK = "返回"
    FORWARD = "前进"
    UP = "上层"
    TOP = "顶层"
    REFRESH = "刷新"
    
    NEW = "新建"
    PROPERTIES = "属性"
    RENAME = "重命名"
    
    COPY_PATH = "复制路径"
    CUT = "剪切"
    COPY = "复制"
    PASTE = "粘贴"
    DELETE = "删除"


class Headings:
    NAME = "名称"
    CATEGORY = "类别"


startupPage = Path.home()


class Navigate:
    @staticmethod
    def go_back(event: Optional[tk.Event] = None) -> None:
        if not backStack:
            return

        newPath = backStack.pop()
        forwardStack.append(currentPath)
        navigationMenu.entryconfigure(Actions.FORWARD, state=tk.NORMAL)

        if not backStack:
            navigationMenu.entryconfigure(Actions.BACK, state=tk.DISABLED)

        sync_currentPath(newPath)
        sync_addressBar(newPath)
        Navigate.refresh_treeview()

    @staticmethod
    def go_forward(event: Optional[tk.Event] = None) -> None:
        if not forwardStack:
            return

        newPath = forwardStack.pop()
        backStack.append(currentPath)
        navigationMenu.entryconfigure(Actions.BACK, state=tk.NORMAL)

        if not forwardStack:
            navigationMenu.entryconfigure(Actions.FORWARD, state=tk.DISABLED)

        sync_currentPath(newPath)
        sync_addressBar(newPath)
        Navigate.refresh_treeview()

    @staticmethod
    def go_up(event: Optional[tk.Event] = None) -> None:
        """返回上一级"""
        parent = currentPath.parent

        if currentPath != parent:
            backStack.append(currentPath)
            forwardStack.clear()
            navigationMenu.entryconfigure(Actions.BACK, state=tk.NORMAL)
            navigationMenu.entryconfigure(Actions.FORWARD, state=tk.DISABLED)

            sync_currentPath(parent)
            sync_addressBar(parent)
            Navigate.refresh_treeview()

    @staticmethod
    def driveRoot(event: Optional[tk.Event] = None) -> None:
        """导航到驱动器根目录"""
        drive = Path(f"{currentPath.drive}\\")
        sync_currentPath(drive)
        sync_addressBar(drive)
        Navigate.refresh_treeview()

    @staticmethod
    def refresh_treeview(event: Optional[tk.Event] = None) -> None:
        """刷新树形视图"""
        # 获取当前目录下对象的信息
        paths = tuple(currentPath.glob("*"))
        names = (p.name for p in paths)
        categories = (Utils.category(p) for p in paths)
        # 清空原有条目
        for item in treeview.get_children():
            treeview.delete(item)
        # 添加现有条目
        for row in zip(names, categories):
            treeview.insert("", tk.END, values=row)


class NamingWindow(tk.Toplevel):
    def __init__(self, root: tk.Tk, *, content: Optional[str] = None) -> None:
        super().__init__(root)
        self.withdraw()
        self.title("命名")
        self.minsize(300, 0)
        self.resizable(False, False)
        self.transient(root)
        self.grab_set()
        self.bind(Events.ENTER, self._ok)

        self.rootFrame = tk.Frame(self)
        self.rootFrame.grid_columnconfigure(0, weight=1)
        self.rootFrame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.entryFrame = tk.Frame(self.rootFrame)

        self.entryFrame.grid_rowconfigure(0, weight=1)
        self.entryFrame.grid_columnconfigure(0, weight=1)

        self.entryFrame.grid(row=0, column=0, sticky=tk.NSEW)

        # 单行文本框、水平滚动条
        self.entry = tk.Entry(self.entryFrame, font=("Fira Code", 11), width=1,
                              validate="key", validatecommand=(root.register(NamingWindow._validate_input), '%P'))
        self.x_scrollbar = tk.Scrollbar(self.entryFrame, orient=tk.HORIZONTAL, command=self.entry.xview)

        self.entry.focus_set()
        self.entry.config(xscrollcommand=self.x_scrollbar.set)
        if content is not None:
            self.entry.insert(0, content)

        self.entry.grid(row=0, column=0, sticky="ew")
        self.x_scrollbar.grid(row=1, column=0, sticky="ew")

        TkUtils.center_on_master(self)
        self.deiconify()

        # 初始化结果并等待操作
        self.result = None
        self.wait_window()

    @staticmethod
    def _validate_input(newText: str) -> bool:
        return not any(char in DISABLE_CHARS for char in newText)

    def _ok(self, event: Optional[tk.Event] = None) -> None:
        self.result = self.entry.get()
        self.destroy()


class PropertiesWindow(tk.Toplevel):
    def __init__(self, root: tk.Tk, *, path: Path, name: str) -> None:
        super().__init__(root)
        self.withdraw()
        self.title(f"{name} 属性")
        self.transient(root)

        self.rootFrame = tk.Frame(self)
        self.rootFrame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.labelColumnFrame = tk.Frame(self.rootFrame)
        self.valueColumnFrame = tk.Frame(self.rootFrame)

        self.labelColumnFrame.grid(row=0, column=0, sticky="ns")
        self.valueColumnFrame.grid(row=0, column=1, sticky="ns")

        self.nameTextLabel = tk.Label(self.labelColumnFrame, text="名称", width=10)
        self.categoryTextLabel = tk.Label(self.labelColumnFrame, text="类型", width=10)
        self.positionTextLabel = tk.Label(self.labelColumnFrame, text="位置", width=10)
        self.sizeTextLabel = tk.Label(self.labelColumnFrame, text="大小", width=10)
        self.occupySpaceTextLabel = tk.Label(self.labelColumnFrame, text="占用空间", width=10)
        self.createdTextLabel =  tk.Label(self.labelColumnFrame, text="创建时间", width=10)
        self.modifiedTextLabel =  tk.Label(self.labelColumnFrame, text="修改时间", width=10)
        self.accessedTextLabel =  tk.Label(self.labelColumnFrame, text="访问时间", width=10)

        self.nameTextLabel.grid(row=0, column=0)
        self.categoryTextLabel.grid(row=1, column=0)
        self.positionTextLabel.grid(row=2, column=0)
        self.sizeTextLabel.grid(row=3, column=0)
        self.occupySpaceTextLabel.grid(row=4, column=0)
        self.createdTextLabel.grid(row=5, column=0)
        self.modifiedTextLabel.grid(row=6, column=0)
        self.accessedTextLabel.grid(row=7, column=0)

        suffix = path.suffix.lstrip(".")
        categoryValue = FOLDER if path.is_dir() else f"{DESCRIPTION.get(suffix, f'{suffix.upper()} 文件')} (.{suffix})"
        statResult = path.stat()
        byteSize = statResult.st_size
        if byteSize != 0:
            index = math.floor(math.log(byteSize, 1024))
            unit = DATA_UNITS[index]
            size = byteSize / (1024.0 ** index)
        else:
            unit = DATA_UNITS[0]
            size = 0.0
        createdDatetime = datetime.datetime.fromtimestamp(statResult.st_ctime)
        modifiedDatetime = datetime.datetime.fromtimestamp(statResult.st_mtime)
        accessedDatetime = datetime.datetime.fromtimestamp(statResult.st_atime)
        createdValue = createdDatetime.strftime(f"%Y年%m月%d日，{WEEKDAY_CN_MAP[createdDatetime.weekday()]}，%H:%M:%S")
        modifiedValue = modifiedDatetime.strftime(f"%Y年%m月%d日，{WEEKDAY_CN_MAP[modifiedDatetime.weekday()]}，%H:%M:%S")
        accessedValue = accessedDatetime.strftime(f"%Y年%m月%d日，{WEEKDAY_CN_MAP[accessedDatetime.weekday()]}，%H:%M:%S")

        self.nameValueLabel = tk.Label(self.valueColumnFrame, text=path.name)
        self.categoryValueLabel = tk.Label(self.valueColumnFrame, text=categoryValue)
        self.positionValueLabel = tk.Label(self.valueColumnFrame, text=f"{path.parent}")
        self.sizeValueLabel = tk.Label(self.valueColumnFrame, text=f"{size:.2f} {unit} ({byteSize:,} B)")
        self.occupySpaceValueLabel = tk.Label(self.valueColumnFrame)
        self.createdValueLabel =  tk.Label(self.valueColumnFrame, text=createdValue)
        self.modifiedValueLabel =  tk.Label(self.valueColumnFrame, text=modifiedValue)
        self.accessedValueLabel =  tk.Label(self.valueColumnFrame, text=accessedValue)

        self.nameValueLabel.grid(row=0, column=0, sticky="w")
        self.categoryValueLabel.grid(row=1, column=0, sticky="w")
        self.positionValueLabel.grid(row=2, column=0, sticky="w")
        self.sizeValueLabel.grid(row=3, column=0, sticky="w")
        self.occupySpaceValueLabel.grid(row=4, column=0, sticky="w")
        self.createdValueLabel.grid(row=5, column=0, sticky="w")
        self.modifiedValueLabel.grid(row=6, column=0, sticky="w")
        self.accessedValueLabel.grid(row=7, column=0, sticky="w")

        if categoryValue == FOLDER:
            fileCount, dirCount = Utils.dirCount(path)

            self.inclusionTextLabel = tk.Label(self.labelColumnFrame, text="包含")
            self.inclusionValueLabel = tk.Label(self.valueColumnFrame, text=f"{fileCount} 个文件，{dirCount} 个文件夹")

            self.inclusionTextLabel.grid(row=8, column=0)
            self.inclusionValueLabel.grid(row=8, column=0, sticky="w")

        TkUtils.center_on_master(self)
        self.deiconify()


def set_address(content: str) -> None:
    """将地址替换为给定内容"""
    addressBar.delete(0, tk.END)
    addressBar.insert(0, content)

def sync_addressBar(path: Path, /) -> None:
    # 同步到地址栏
    set_address(str(path))
    # 将插入光标、水平视图均移动到结尾
    addressBar.icursor(tk.END)
    addressBar.xview_moveto(1.0)

def sync_currentPath(path: Path, /) -> None:
    global currentPath
    # 同步到路径值
    currentPath = path

def navigation_onTreeview(event: Optional[tk.Event] = None) -> None:
    selectedItems = treeview.selection()
    if not selectedItems:
        return

    itemId = selectedItems[0]
    values = treeview.item(itemId, "values")
    newPath = currentPath / values[0]

    if newPath.is_dir():
        backStack.append(currentPath)
        forwardStack.clear()
        navigationMenu.entryconfigure(Actions.BACK, state=tk.NORMAL)
        navigationMenu.entryconfigure(Actions.FORWARD, state=tk.DISABLED)

        sync_currentPath(newPath)
        sync_addressBar(newPath)
        Navigate.refresh_treeview()
    else:
        Utils.open_in_explorer(newPath)

@log_call
def navigation_onAddressBar(event: Optional[tk.Event] = None) -> None:
    newPathStr = addressBar.get()
    newPath = Path(newPathStr)

    if not newPath.exists():
        msg = f"Windows 找不到“{newPathStr}”。请检查拼写并重试。"
        messagebox.showerror(TITLE, msg)
        set_address(str(currentPath))    # 还原地址
        return

    if newPath.is_dir():
        backStack.append(currentPath)
        forwardStack.clear()
        navigationMenu.entryconfigure(Actions.BACK, state=tk.NORMAL)
        navigationMenu.entryconfigure(Actions.FORWARD, state=tk.DISABLED)

        sync_currentPath(newPath)
        Navigate.refresh_treeview()
    else:
        Utils.open_in_explorer(newPath)


class Resource:
    @staticmethod
    def on_new(event: Optional[tk.Event] = None) -> None:
        def new_dir():
            namingWindow = NamingWindow(root, content=Utils.timestamp(time_sep='`'))
            name = namingWindow.result

            if name is None:
                return

            path = currentPath / name
            # 处理新建文件夹时，已存在同名文件夹的情况
            if path.exists():
                messagebox.showerror(TITLE, "已存在同名文件夹！")
                return

            path.mkdir()
            treeview.insert("", tk.END, values=(name, Utils.category(path)))

        def new_file(suffix: str) -> None:
            def callback(suffix=suffix):
                namingWindow = NamingWindow(root, content=f"{Utils.timestamp(time_sep='`')}.{suffix}")
                name = namingWindow.result

                if name is None:
                    return

                path = currentPath / name
                # 处理新建文件时，已存在同名文件的情况
                if path.exists():
                    messagebox.showerror(TITLE, "已存在同名文件！")
                    return

                path.touch()
                treeview.insert("", tk.END, values=(name, Utils.category(path)))

            return callback

        menu = tk.Menu(tearoff=False)
        menu.add_command(label=FOLDER, command=new_dir)

        for desc, suffix in NEW_MENU_OPTIONS:
            menu.add_command(label=desc, command=new_file(suffix))
        
        menu.post(event.x_root, event.y_root)

    @staticmethod
    def copy_path(event: Optional[tk.Event] = None) -> None:
        """将被选中项的路径复制到系统剪贴板"""
        selectedItems = treeview.selection()

        if not selectedItems:
            return

        path_list = []
        for itemId in selectedItems:
            path = str(currentPath / treeview.item(itemId, "values")[0])
            path_list.append(path)

        pyperclip.copy('\n'.join(path_list))

    @staticmethod
    def moveTo_recycleBin(event: Optional[tk.Event] = None) -> None:
        """将选中的项移动到回收站"""
        selectedItems = treeview.selection()

        if not selectedItems:
            return

        for itemId in selectedItems:
            path = str(currentPath / treeview.item(itemId, "values")[0])

            send2trash.send2trash(path)
            treeview.delete(itemId)

    @staticmethod
    def _copy_resource(event: Optional[tk.Event] = None, *, mode: int) -> None:
        """复制选中的资源到剪贴板"""
        global clipboard, clipboardMode

        selectedItems = treeview.selection()

        if not selectedItems:
            return

        # 将选中的资源及其所在地址记录到剪贴板
        result = [currentPath]
        for itemId in selectedItems:
            result.append(treeview.item(itemId, "values")[0])
        clipboard = result

        # 记录剪贴板模式
        clipboardMode = mode

    copy_resource = partial(_copy_resource, mode=ClipboardMode.COPY)
    cut_resource = partial(_copy_resource, mode=ClipboardMode.CUT)

    @staticmethod
    def paste_resource(event: Optional[tk.Event] = None) -> None:
        """从剪贴板中粘贴资源到当前路径"""
        global clipboard, clipboardMode

        if clipboard is None:
            return

        def paste(method: abc.Callable) -> None:
            # 获取该批资源的原始地址
            originalAddress = clipboard[0]

            # 复制每个资源到目标路径
            for name in clipboard[1:]:
                # 获取当前原始资源的完整路径、目标路径
                originalPath = originalAddress / name
                targetPath = currentPath / name

                # 处理原始资源丢失的情况
                if not originalPath.exists():
                    # 不进行任何操作（暂定）
                    continue

                # 处理已存在同名资源的情况
                if targetPath.exists():
                    # 不进行任何操作（暂定）
                    continue

                # 按传入的方法对原始资源进行操作
                method(originalPath)
                # 同步到资源展示
                treeview.insert("", tk.END, values=(name, Utils.category(targetPath)))

        if clipboardMode == ClipboardMode.COPY:
            def copy(originalPath: Path) -> None:
                if originalPath.is_dir():
                    shutil.copytree(originalPath, currentPath)
                else:
                    shutil.copy2(originalPath, currentPath)
            paste(copy)
        else:
            def cut(originalPath: Path) -> None:
                shutil.move(originalPath, currentPath)
            paste(cut)

    @staticmethod
    def on_rename(event: Optional[tk.Event] = None) -> None:
        selectedItems = treeview.selection()
        # 仅处理单个资源的重命名（暂定）
        if len(selectedItems) != 1:
            return

        itemId = selectedItems[0]
        values = treeview.item(itemId, "values")
        oldName = values[0]

        namingWindow = NamingWindow(root, content=oldName)
        newName = namingWindow.result

        if newName is not None and oldName != newName:
            # 在系统中重命名选定的资源
            (currentPath / oldName).rename(currentPath / newName)
            # 同步到资源展示
            treeview.set(itemId, NAME, namingWindow.result)

    @staticmethod
    def on_properties(event: Optional[tk.Event] = None) -> None:
        selectedItems = treeview.selection()

        # 未选中项时，查看属性的对象为当前路径。
        if not selectedItems:
            if currentPath == currentPath.parent:
                # 不处理磁盘的属性展示（暂定）
                return

            PropertiesWindow(root, path=currentPath, name=currentPath.name)
            return

        # 仅处理单个资源的属性显示（暂定）
        if len(selectedItems) != 1:
            return

        itemId = selectedItems[0]
        values = treeview.item(itemId, "values")
        oldName = values[0]

        PropertiesWindow(root, path=(currentPath / oldName), name=oldName)

@log_call
def show_contentMenu(event: Optional[tk.Event]) -> None:
    selectedItems = treeview.selection()
    if not selectedItems:
        menu = tk.Menu(root, tearoff=False)
        menu.add_command(label=Actions.NEW, accelerator="Ctrl+N", command=Resource.on_new)
        menu.add_command(label=Actions.PROPERTIES, accelerator="Alt+Enter", command=Resource.on_properties)
        if clipboard is not None:
            menu.add_command(label=Actions.PASTE, accelerator="Ctrl+V", command=Resource.paste_resource)

    else:
        menu = tk.Menu(root, tearoff=False)
        menu.add_command(label=Actions.PROPERTIES, accelerator="Alt+Enter", command=Resource.on_properties)
        menu.add_command(label=Actions.RENAME, accelerator="F2", command=Resource.on_rename)
        menu.add_command(label=Actions.COPY_PATH, accelerator="Ctrl+Shift+C", command=Resource.copy_path)
        menu.add_separator()
        menu.add_command(label=Actions.CUT, accelerator="Ctrl+X", command=Resource.cut_resource)
        menu.add_command(label=Actions.COPY, accelerator="Ctrl+C", command=Resource.copy_resource)
        if clipboard is not None:
            menu.add_command(label=Actions.PASTE, accelerator="Ctrl+V", command=Resource.paste_resource)
        menu.add_separator()
        menu.add_command(label=Actions.DELETE, accelerator="Ctrl+D", command=Resource.moveTo_recycleBin)

    menu.post(event.x_root, event.y_root)

@log_call
def on_treeviewClick(event: tk.Event) -> None:
    x, y = event.x, event.y
    region = treeview.identify_region(x, y)

    if region == "heading":
        return

    itemId = treeview.identify_row(y)
    if not itemId:
        treeview.selection_remove(treeview.selection())

@log_call
def on_enter(event: tk.Event) -> BreakType:
    state = event.state

    # Alt+Enter
    if state & 0x20000:
        Resource.on_properties(event)
        return BREAK
    
    # Enter
    navigation_onTreeview(event)
    return BREAK


# TODO
#   · 实现「搜索」功能

if __name__ == "__main__":
    # 根窗口
    root = tk.Tk()
    root.withdraw()
    root.title(TITLE)
    root.geometry("600x400")
    root.minsize(600, 400)
    root.iconphoto(True, tk.PhotoImage(width=1, height=1))
    root.bind_all("<Alt-Left>", Navigate.go_back)
    root.bind_all("<Alt-Right>", Navigate.go_forward)
    root.bind_all("<Alt-Up>", Navigate.go_up)
    root.bind_all("<Control-Alt-Up>", Navigate.driveRoot)
    root.bind_all("<F2>", Resource.on_rename)
    root.bind_all("<F5>", Navigate.refresh_treeview)
    root.bind_all("<Control-n>", Resource.on_new); root.bind_all("<Control-N>", Resource.on_new)
    root.bind_all("<Control-x>", Resource.cut_resource); root.bind_all("<Control-X>", Resource.cut_resource)
    root.bind_all("<Control-c>", Resource.copy_resource); root.bind_all("<Control-C>", Resource.copy_resource)
    root.bind_all("<Control-v>", Resource.paste_resource); root.bind_all("<Control-V>", Resource.paste_resource)
    root.bind_all("<Control-d>", Resource.moveTo_recycleBin); root.bind_all("<Control-D>", Resource.moveTo_recycleBin)
    root.bind_all("<Control-Shift-c>", Resource.copy_path); root.bind_all("<Control-Shift-C>", Resource.copy_path)

    # 初始化各种值
    backStack = []
    forwardStack = []
    currentPath = startupPage
    clipboardMode: Optional[int] = None    # 剪贴板模式：决定粘贴的方式
    clipboard: Optional[list[Path | str]] = None    # 索引 0 为原始路径，其后均为复制的原始资源的名称

    # 主菜单
    menuBar = tk.Menu(root, tearoff=False)
    navigationMenu = tk.Menu(menuBar, tearoff=False)

    menuBar.add_cascade(label="导航", menu=navigationMenu)

    navigationMenu.add_command(label=Actions.BACK, accelerator="Alt+←", command=Navigate.go_back, state=tk.DISABLED)
    navigationMenu.add_command(label=Actions.FORWARD, accelerator="Alt+→", command=Navigate.go_forward, state=tk.DISABLED)
    navigationMenu.add_command(label=Actions.UP, accelerator="Alt+↑", command=Navigate.go_up)
    navigationMenu.add_separator()
    navigationMenu.add_command(label=Actions.TOP, accelerator="Ctrl+Alt+↑", command=Navigate.driveRoot)
    navigationMenu.add_separator()
    navigationMenu.add_command(label=Actions.REFRESH, accelerator="F5", command=Navigate.refresh_treeview)

    root.config(menu=menuBar)

    # 根框架
    rootFrame = tk.Frame(root)
    rootFrame.rowconfigure(1, weight=1)
    rootFrame.columnconfigure(0, weight=4)
    rootFrame.columnconfigure(1, weight=3)
    rootFrame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    addressBar = tk.Entry(rootFrame, font=("Fira Code", 11), width=1)
    searchBox = tk.Entry(rootFrame, font=("Fira Code", 11), width=1)
    resourceFrame = tk.Frame(rootFrame)

    resourceFrame.rowconfigure(0, weight=1)
    resourceFrame.columnconfigure(0, weight=1)

    addressBar.grid(row=0, column=0, padx=(0, 5), pady=(0, 10), sticky=tk.EW)
    searchBox.grid(row=0, column=1, padx=(5, 20), pady=(0, 10), sticky=tk.EW)
    resourceFrame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=tk.NSEW)

    # 地址栏
    addressBar.bind(Events.ENTER, navigation_onAddressBar)

    # 搜索框
    searchBox.insert(0, "搜索... (未实现)")

    # 资源框架
    treeview = ttk.Treeview(resourceFrame, columns=(NAME, CATEGORY), show=HEADINGS)
    x_scrollbar = tk.Scrollbar(resourceFrame, orient=tk.HORIZONTAL, command=treeview.xview)
    y_scrollbar = tk.Scrollbar(resourceFrame, orient=tk.VERTICAL, command=treeview.yview)

    treeview.heading(NAME, text=Headings.NAME)
    treeview.heading(CATEGORY, text=Headings.CATEGORY)
    treeview.column(NAME, width=150, anchor="w")
    treeview.column(CATEGORY, width=50, anchor="w")
    treeview.bind(Events.DOUBLE_CLICK, navigation_onTreeview)
    treeview.bind(Events.RIGHT_CLICK, show_contentMenu)
    treeview.bind(Events.LEFT_CLICK, on_treeviewClick)
    treeview.bind(Events.ENTER, on_enter)

    treeview.config(xscrollcommand=x_scrollbar.set,
                    yscrollcommand=y_scrollbar.set)

    treeview.grid(row=0, column=0, sticky=tk.NSEW)
    x_scrollbar.grid(row=1, column=0, sticky=tk.EW)
    y_scrollbar.grid(row=0, column=1, sticky=tk.NS)

    # 初始化资源
    sync_addressBar(currentPath)
    Navigate.refresh_treeview()

    TkUtils.center(root)
    root.deiconify()
    root.mainloop()