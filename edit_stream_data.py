import tkinter as tk
from tksheet import Sheet
import sys

# file_path = sys.argv[1].strip('"')
# current_page = sys.argv[2]



root = tk.Tk()
root.title("tksheet Test - Editable Spreadsheet")
root.geometry("660x600")

data = [
    ["1", "liquid",  "100000", "","4", 0.0004532, "50", "100"],
    ["2", "liquid",  "100000", "","4", 0.0004532, "50", "100"],
    ["3", "vapor", "",  "1000", "6", 0.0004532, "50", "100"],
    ["4", "vapor", "",  "1000", "6", 0.0004532, "60", "120"]
]

sheet = Sheet(root,
              data=data,
              headers=["Stream\n No.", "phase", "Liquid\n[kg/hr]", "Vapor\n[kg/hr]", "Line Size\n[inch]", "roughness\n[m]", "St. length\n[m]", "Eq. length\n[m]"   ],
              header_height=40,
              show_row_index=False,
              show_header=True)


# sheet.set_corner_text("Stream No")
# 중앙 정렬
sheet.align(align="center", redraw=True)

# 열 너비 조정
for col_index in range(sheet.total_columns()):
    sheet.column_width(col_index, 80)

# 행 높이 조정
# for row_index in range(sheet.total_rows()):
#     sheet.row_height(row_index, 30)


sheet.enable_bindings((
    "single_select",
    "row_select",
    "column_select",
    "drag_select",
    "column_drag_and_drop",
    "row_drag_and_drop",
    "column_resize",
    "row_resize",
    "edit_cell"
))

sheet.pack(expand=True, fill="both")
root.mainloop()
