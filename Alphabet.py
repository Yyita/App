import tkinter as tk
import string


TITLE = "字母表"

FLOOR = 1
CAP = 26

ITEM_WIDTH = 2
MARGIN = 15

CASE_PAIRS = map(''.join, zip(string.ascii_uppercase, string.ascii_lowercase))
ITEM_MAP = {i: item for i, item in enumerate(CASE_PAIRS, start=FLOOR)}


class Colors:
    GRAY = "#888888"
    BLACK = "#000000"


class Fonts:
    ITEM = ("TkDefaultFont", 17)


def update_item(pointer_str: str) -> None:
    pointer = int(pointer_str)
    char_on_left_label.config(text=ITEM_MAP.get(pointer - 1, ""))
    char_on_center_label.config(text=ITEM_MAP.get(pointer, ""))
    char_on_right_label.config(text=ITEM_MAP.get(pointer + 1, ""))


root = tk.Tk()
root.title(TITLE)
root.resizable(False, False)

frame = tk.Frame(root)

frame.grid_rowconfigure((0,), weight=1)
frame.grid_columnconfigure((0, 1, 2), weight=1)

frame.pack(fill=tk.BOTH, expand=True, padx=MARGIN, pady=MARGIN)

scale = tk.Scale(frame, command=update_item, orient=tk.HORIZONTAL,
                 from_=FLOOR, to=CAP, length=(CAP-FLOOR+1) * 7,
                 width=20, sliderlength=20)
char_on_left_label = tk.Label(frame, font=Fonts.ITEM, fg=Colors.GRAY, width=ITEM_WIDTH)
char_on_center_label = tk.Label(frame, font=Fonts.ITEM, fg=Colors.BLACK, width=ITEM_WIDTH)
char_on_right_label = tk.Label(frame, font=Fonts.ITEM, fg=Colors.GRAY, width=ITEM_WIDTH)
update_item(str(FLOOR))

char_on_left_label.grid(row=0, column=0, sticky="nswe")
char_on_center_label.grid(row=0, column=1, sticky="nswe")
char_on_right_label.grid(row=0, column=2, sticky="nswe")
scale.grid(row=1, column=0, columnspan=3, sticky="nswe")

root.mainloop()