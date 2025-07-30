# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox

from tksheet import Sheet

import sys
import xml.etree.ElementTree as ET
import hydro.module_graphic as module_graphic
import config
# file_path = sys.argv[1].strip('"')
# current_page = sys.argv[2]    

def edit_stream_sequence():
    """
    Stream data를 편집하는 시퀀스 함수
    """
    # file_path = sys.argv[1].strip('"')
    # current_page = sys.argv[2]    
    file_path = "p:\\hydro\\default.hydro"
    current_page =  "2 Phase" #"P-101A/B" #
    config.current_page = current_page

    def load_drawio(file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        # hydro 전용 태그라면 변환 (in-memory)
        if root.tag == 'hydrofile':
            # print("💡 hydro 전용 파일 감지됨. 태그 변환 중...")
            root.tag = 'mxfile'
            # 여기에 필요한 경우 diagram 내부도 처리 가능
        return tree, root

    tree, root = load_drawio(file_path)
    # file_name = os.path.basename(file_path)
    
    def get_tag_no_by_id(root, target_id):
        """ 특정 ID의 A_tag_no 값을 반환 (없으면 ID 유지) """
        global line_number
        for obj in root.findall(".//object"):
            if obj.get("id") == target_id:
                return obj.get("A_tag_no") or f"ID:{target_id}"  # A_tag_no 없으면 ID 그대로 반환
        return f"ID:{target_id}"  # ID가 없으면 그대로 반환

    calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    if calculation_sheet is None:
        return []  # 해당 시트가 없으면 빈 리스트 반환
    line_idss = []
    for object in calculation_sheet.findall('.//object'):
        for line in object.findall('.//mxCell'):
            if 'edge' in line.attrib:
                edge_id = object.get('id')  # 연결선의 ID
                source = line.get('source')  # 시작 노드 ID
                target = line.get('target')  # 끝 노드 ID
                line_idss.append (edge_id)                 

    #     return input_error_message, line_type, input_data
    def validate_object_data(object, line_idss):
        global line_number
        object_id = object.get('id')
        line_no = line_idss.index(object_id) + 1 if object_id in line_idss else -1  # 🔥 핵심!

        result = None
        if 'i2_density' in object.attrib:
            result = {'line_no': line_no, 'line_id': object_id}
            for k in ['i1_flowrate', 'i2_density', 'i3_viscosity', 'i4_pipe_size_ID', 'i5_roughness', 'i60_straight_length', 'i6_equivalent_length']:
                result[k] = object.attrib.get(k)
            return 'liquid', result

        elif 'i2_MW' in object.attrib:
            result = {'line_no': line_no, 'line_id': object_id}
            for k in ['i1_flowrate', 'i2_MW', 'i3_viscosity', 'i4_temperature', 'i5_compressible_factor_z',
                    'i6_specific_heat_Cp_Cv', 'i7_pipe_size_ID', 'i8_roughness', 'i90_straight_length', 'i9_equivalent_length']:
                result[k] = object.attrib.get(k)
            return 'vapor', result

        elif 'i1_liquid_flowrate' in object.attrib:
            result = {'line_no': line_no, 'line_id': object_id}
            for k in ['i1_liquid_flowrate', 'i2_liquid_density', 'i3_vapor_flowrate', 'i4_vapor_density',
                    'i5_pipe_size_ID', 'i6_roughness', 'i70_straight_length', 'i7_equivalent_length']:
                result[k] = object.attrib.get(k)
            return '2phase', result

        return None, None

    def check_input_value(root):
        global line_number
        calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")

        # 🔧 Drawio의 라인 ID 확보
        routes, routes_id, line_ids = module_graphic.find_routes_from_drawio(root)

        # 🔍 결과 저장용 리스트
        liquid_inputs = []
        vapor_inputs = []
        two_phase_inputs = []

        # 🔍 각 object 탐색
        for object in calculation_sheet.findall('.//object'):
            phase, values = validate_object_data(object, line_ids)
            if phase == 'liquid':
                liquid_inputs.append(values)
            elif phase == 'vapor':
                vapor_inputs.append(values)
            elif phase == '2phase':
                two_phase_inputs.append(values)

        # ✅ 최종 출력
        # print("💧 Liquid Inputs:", liquid_inputs)
        # print("💨 Vapor Inputs:", vapor_inputs)
        # print("⚪ 2Phase Inputs:", two_phase_inputs)
        # print("🔗 Line IDs:", line_ids)
        return liquid_inputs, vapor_inputs, two_phase_inputs
    
    liquid_inputs, vapor_inputs, two_phase_inputs = check_input_value(root)
    
    def convert_to_tksheet_format(liquid_inputs, vapor_inputs, two_phase_inputs):
        combined = []

        for item in liquid_inputs:
            combined.append({
                'line_no': item['line_no'],
                'row': [
                    str(item['line_no']),
                    "liquid",
                    item.get('i1_flowrate', ''),
                    "",
                    item.get('i4_pipe_size_ID', ''),
                    item.get('i5_roughness', ''),
                    item.get('i60_straight_length', '') or "",
                    item.get('i6_equivalent_length', '')
                ]
            })

        for item in vapor_inputs:
            combined.append({
                'line_no': item['line_no'],
                'row': [
                    str(item['line_no']),
                    "vapor",
                    "",
                    item.get('i1_flowrate', ''),
                    item.get('i7_pipe_size_ID', ''),
                    item.get('i8_roughness', ''),
                    item.get('i90_straight_length', '') or "",
                    item.get('i9_equivalent_length', '')
                ]
            })

        for item in two_phase_inputs:
            combined.append({
                'line_no': item['line_no'],
                'row': [
                    str(item['line_no']),
                    "2phase",
                    item.get('i1_liquid_flowrate', ''),
                    item.get('i3_vapor_flowrate', ''),
                    item.get('i5_pipe_size_ID', ''),
                    item.get('i6_roughness', ''),
                    item.get('i70_straight_length', '') or "",
                    item.get('i7_equivalent_length', '')
                ]
            })

        # 🔢 line_no 기준으로 정렬
        combined_sorted = sorted(combined, key=lambda x: x['line_no'])

        # 📋 tksheet에 넣을 리스트만 추출
        return [item['row'] for item in combined_sorted]

    
    tksheet_data = convert_to_tksheet_format(liquid_inputs, vapor_inputs, two_phase_inputs)
    root = tk.Tk()
    # title = f"{file_path}   pagename : {current_page}"
    root.title(f"{file_path} [{current_page}] - Stream Data Edit")
    root.geometry("660x400")

    sheet = Sheet(root,
                data= tksheet_data,
                headers=["Stream\n No.", "phase", "Liquid\n[kg/hr]", "Vapor\n[kg/hr]", "Line Size\n[inch]", "roughness\n[m]", "St. length\n[m]", "Eq. length\n[m]"   ],
                header_height=40,
                show_row_index=False,
                show_header=True)
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

    sheet.readonly_columns([0, 1])  # 0번 컬럼을 읽기 전용으로 설정
    # sheet.readonly_cells([1,1])  # Stream No, phase 컬럼은 수정 불가
 
    def block_edit_on_phase(event):
        selected = sheet.get_selected_cells()
        if selected:
            row, col = selected[0]
            phase = sheet.get_cell_data(row, 1).strip().lower()  # phase 컬럼은 index 1
            if (phase == "liquid" and col == 3) or (phase == "vapor" and col == 2):
                return "break"  # 편집 차단
        return None

    sheet.extra_bindings("edit_cell", block_edit_on_phase)




    sheet.pack(expand=True, fill="both")
    
    def update_hydro_file(file_path, current_page, updated_data, line_id_map):
        tree = ET.parse(file_path)
        root = tree.getroot()

        if root.tag == 'hydrofile':
            root.tag = 'mxfile'

        diagram = root.find(f".//diagram[@name='{current_page}']")
        if diagram is None:
            print("❌ 해당 페이지를 찾을 수 없습니다.")
            return

        for row in updated_data:
            line_no = int(row[0])
            phase = row[1]
            line_id = line_id_map.get(line_no)
            if not line_id:
                continue

            obj = diagram.find(f".//object[@id='{line_id}']")
            if obj is None:
                continue

            if phase == "liquid":
                obj.set("i1_flowrate", row[2])
                obj.set("i4_pipe_size_ID", row[4])
                obj.set("i5_roughness", row[5])
                obj.set("i60_straight_length", row[6])
                obj.set("i6_equivalent_length", row[7])

            elif phase == "vapor":
                obj.set("i1_flowrate", row[3])
                obj.set("i7_pipe_size_ID", row[4])
                obj.set("i8_roughness", row[5])
                obj.set("i90_straight_length", row[6])
                obj.set("i9_equivalent_length", row[7])

            elif phase == "2phase":
                obj.set("i1_liquid_flowrate", row[2])
                obj.set("i3_vapor_flowrate", row[3])
                obj.set("i5_pipe_size_ID", row[4])
                obj.set("i6_roughness", row[5])
                obj.set("i70_straight_length", row[6])
                obj.set("i7_equivalent_length", row[7])

        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        messagebox.showinfo(f"✅ 수정된 .hydro 파일이 저장되었습니다: {file_path}")

    def on_confirm():
        try:
            # updated_data = sheet.get_sheet_data(return_copy=True)
            
            updated_data = sheet.get_sheet_data()

            # updated_data = sheet.get_sheet_as_nested_list()

            line_id_map = {}
            for item in liquid_inputs + vapor_inputs + two_phase_inputs:
                line_id_map[item['line_no']] = item['line_id']
            
            update_hydro_file(file_path, current_page, updated_data, line_id_map)
            messagebox.showinfo(f"저장 완료 {file_path} 파일이 성공적으로 저장되었습니다.")
            root.destroy()
        except Exception as e:
            messagebox.showerror("오류", "파일 저장 중 문제가 발생했습니다.")


    def on_cancel():
        messagebox.showinfo("❌ 편집 취소됨")
        root.destroy()


    # 기존 root, sheet 생성 코드 이후에 추가
    button_frame = tk.Frame(root)
    button_frame.pack(fill="x", pady=10)

    confirm_btn = tk.Button(button_frame, text="✅ Confirm", command=on_confirm, width=15)
    confirm_btn.pack(side="left", padx=20)

    cancel_btn = tk.Button(button_frame, text="❌ Cancel", command=on_cancel, width=15)
    cancel_btn.pack(side="right", padx=20)
    
    root.mainloop()   

if __name__ == "__main__":
    try:
        # root = tk.Tk()
        # root.title("tksheet Test - Editable Spreadsheet")
        # root.geometry("660x600")
        # root.mainloop()  
        edit_stream_sequence()

    except Exception as e:
        sys.exit(1)  # 오류 발생 시 exit code 1 반환


# root = tk.Tk()
# root.title("tksheet Test - Editable Spreadsheet")
# root.geometry("660x600")

# data = [
#     [current_page, file_path,  "100000", "","4", 0.0004532, "50", "100"],
#     ["2", "liquid",  "100000", "","4", 0.0004532, "50", "100"],
#     ["3", "vapor", "",  "1000", "6", 0.0004532, "50", "100"],
#     ["4", "vapor", "",  "1000", "6", 0.0004532, "60", "120"]
# ]

# sheet = Sheet(root,
#               data=data,
#               headers=["Stream\n No.", "phase", "Liquid\n[kg/hr]", "Vapor\n[kg/hr]", "Line Size\n[inch]", "roughness\n[m]", "St. length\n[m]", "Eq. length\n[m]"   ],
#               header_height=40,
#               show_row_index=False,
#               show_header=True)


# # sheet.set_corner_text("Stream No")
# # 중앙 정렬
# sheet.align(align="center", redraw=True)

# # 열 너비 조정
# for col_index in range(sheet.total_columns()):
#     sheet.column_width(col_index, 80)

# # 행 높이 조정
# # for row_index in range(sheet.total_rows()):
# #     sheet.row_height(row_index, 30)


# sheet.enable_bindings((
#     "single_select",
#     "row_select",
#     "column_select",
#     "drag_select",
#     "column_drag_and_drop",
#     "row_drag_and_drop",
#     "column_resize",
#     "row_resize",
#     "edit_cell"
# ))

# sheet.pack(expand=True, fill="both")
# root.mainloop()