import tkinter as tk
from tksheet import Sheet

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import socket

import pandas as pd

import hydro.module_graphic as module_graphic
import hydro.module_hyd as module_hyd 
import hydro.module_mapping as module_mapping
import hydro.module_output_drawio as module_output_drawio
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def edit_stream_sequence():
    """
    Stream data를 편집하는 시퀀스 함수
    """
    # # 파일 경로와 현재 페이지 설정
    # file_path = sys.argv[1].strip('"')
    # config.current_page = sys.argv[2]

    # # Draw.io 파일 로드
    # tree, root = load_drawio(file_path)

    # # Stream 데이터 추출
    # only_lines = module_hyd.extract_lines(root)
    
    # # Stream 데이터 매핑
    # line_data = module_mapping.stream_mapping(only_lines, config.pressure_selection)
    
    # # 정렬된 데이터 반환
    # sorted_line_data = dict(sorted(line_data.items()))
    
    # # 결과 출력 (예시로 콘솔에 출력)
    # for tag, row in sorted_line_data.items():
    #     print(f"{tag}: {row}")
        


    sys.stdout.write("✅ 실행 중입니다\n")
    sys.stdout.flush()


    config.file_path = sys.argv[1].strip('"')
    config.current_page = sys.argv[2]
    file_path = sys.argv[1].strip('"')
    def load_drawio(file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        # hydro 전용 태그라면 변환 (in-memory)
        if root.tag == 'hydrofile':
            # print("💡 hydro 전용 파일 감지됨. 태그 변환 중...")
            root.tag = 'mxfile'
            # 여기에 필요한 경우 diagram 내부도 처리 가능
        return tree, root

    root = load_drawio(file_path)
    file_name = os.path.basename(file_path)

    # # ✅ 계산가능한 page 인지 검사
    # calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    # if calculation_sheet is not None:
    #     has_all_attributes = False
    #     for obj in calculation_sheet.findall(".//object"):
    #         if obj.get("hydro_version") and obj.get("pressure_selection") and obj.get("running_status"):
    #             has_all_attributes = True
    #             config.pressure_selection = (obj.get("pressure_selection")).lower()
    #             break # 하나라도 빠진 경우 처리 필요함..
    #         else:
    #             print(f"⚠️ This page ({config.current_page}) is not a calculation page.")
    #             sys.exit(1)
    # if not has_all_attributes:            
    #     print(f"⚠️ This page ({config.current_page}) is not a calculation page.")
    #     sys.exit(1)

    # # ✅ nozzle에 A_tag_no 부여
    # x = module_graphic.update_Nozzle_A_tag_no_from_Equipment(root, config.current_page)

    # ✅ user input 값 체크
    # user_input_error = module_graphic.check_input_value(root) # 사용자 Input값이 문자인지 숫자인지 체크
    # if user_input_error: #에러가 있다는 뜻
    #     result_text = '\n'.join(f"  {i+1}. {item}" for i, item in enumerate(user_input_error))
    #     print("⚠️ user input error \n" + result_text)  # 에러 메시지 출력
    #     result_text = "⚠️ user input error \n"
    #     running_status.add_message(result_text)  # 자동 줄바꿈 포함
    #     # module_output_drawio.tree_write_running_status (file_path, root, running_status)
    #     # module_output_drawio.tree_write_in_drawio_file (file_path, root)
    #     # sys.exit(1)
    #     return abnormal_termination(file_path, root, running_status)  # 에러 발생시 종료
    # else: #에러 없으면   
    #     result_text = '\n\n✅ No Error in user input values'
    #     running_status.add_message(result_text)  # 자동 줄바꿈 포함

    # ✅ Loop 체크
    # running_status.add_message("\nSearching hydraulic loop\n")
    routes, routes_id, line_ids = module_graphic.find_routes_from_drawio(root)

    # for i, route in enumerate(routes):
    #     # print(f" Loop {i}. : "," -> ".join(route))  # A_tag_no로 변환된 경로 출력
    #     temp = f"  Loop {{{i+1}}} : " + " \u2192 ".join(route)
    #     running_status.add_message(temp + "\n")
        # print(route) tag_no로 변환된 경로 출력
    # ✅ Loop 안의 data input 이름을 계산에 편한 보편적 이름으로 바꾸고 문자를 숫자로 변경, type 결정
    routes = module_graphic.object_classification(root, routes_id, line_ids) 
    module_graphic.verify_routes(routes)

    # ✅ Loop 분류 (같은 Header에 묶인것을 분류함)
    grouped_routes = module_graphic.group_routes_by_overlap(routes)
    # print(grouped_routes)
    # running_status.add_message("\nGrouping hydraulic loop\n")
    # for idx, group in enumerate(grouped_routes):
    #     # running_status.add_message(f"  Group {{{idx+1}}} : \n") 
    #     for loop in group: # error 코드 만들어야 함. 잘못 연결된 경우 멈추는 경우에 대하여 ..
    #         temp= []
    #         for item in loop :
    #             if item['type'] in ['liquid_line', 'vapor_line', 'two_phase_line', 'user_line'] :
    #                 temp.append(f'[{item['A_tag_no']}]')    
    #             else :    
    #                 # temp.append(item['A_tag_no'])
    #                 pass
    #         temp_join = f"     " + " \u2192 ".join(str(item) for item in temp) # 오른쪽 화살표
    #         # running_status.add_message(temp_join + "\n")
    #         # print("  Grouping hydraulic loop done.\n")
    # # ✅ Analyzing loop & group
    # # running_status.add_message("\nAnalyzing hydraulic loop")
    # for route in routes :
    #     for item in route :
    #         count_control_vlave = sum(1 for item in route if item['type'] == 'control_valve')
    #         if count_control_vlave >= 2 : 
    #             temp = f"""  impossible to solve {count_control_vlave}ea serial control valves in this loop. \n  please, 
    #             install only one control valve and fixed pressure drop control valves in one loop."""
    #             running_status.add_message(temp)
    #             print(temp)
    #             sys.exit(1)
    #             return
    #         count_variable_pump = sum(1 for item in route if item['type'] == 'variable_pump')
    #         if count_variable_pump >= 2 : 
    #             temp = f"""  impossible to solve {count_variable_pump}ea serial pumps in this loop. \n  please, 
    #             install only one pump and fixed diff. pressure pumps in one loop."""
    #             running_status.add_message(temp)
    #             print(temp) 
    #             sys.exit(1)         
    #             return
    # temp = '\n \nNo Error in each hydraulic loop.'
    # running_status.add_message(temp)

    # ✅ Hyd calculation
    routes = module_hyd.calculate_each_route_object_reverse (routes)
    grouped_routes = module_graphic.group_routes_by_overlap(routes)
    header_grouped_routes = module_hyd.group_header_determination (grouped_routes)


    final_grouped_routes = module_hyd.calculate_each_route_object_forward(header_grouped_routes)

    # ✅ line만 처리
    only_lines =module_hyd.extract_lines (final_grouped_routes)
    print(only_lines)
    # line_data = module_mapping.stream_mapping (only_lines, config.pressure_selection)
    # sorted_line_data = dict(sorted(line_data.items()))
    return

if __name__ == "__main__":
    try:
        sys.stdout.write("✅ 실행 중입니다\n")
        sys.stdout.flush()
        edit_stream_sequence()
        print("✅ edit_stream_data 정상 종료")
    except Exception as e:
        print("❌ 오류 발생:", e)
        import traceback
        traceback.print_exc()
        sys.exit(1)  # 오류 발생 시 exit code 1 반환



# root = tk.Tk()
# root.title("tksheet Test - Editable Spreadsheet")
# root.geometry("660x600")

# data = [
#     ["1", "liquid",  "100000", "","4", 0.0004532, "50", "100"],
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




    

