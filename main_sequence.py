import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import socket

import pandas as pd

import hydro.module_graphic as module_graphic
import hydro.module_hyd as module_hyd 
import hydro.module_mapping as module_mapping
import hydro.module_output_drawio as module_output_drawio, config

def calculation_sequence (file_path, running_status):

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

    file_name = os.path.basename(file_path)
    date_string = datetime.now() ; date_string = date_string.strftime("%Y-%m-%d %H:%M:%S")
    # print(date_string)  # 출력: 2025-03-31 12:00:00
    # temp = f'Filename : {file_name} / Pagename : {config.current_page}'    
    # running_status.add_message(temp) 
    # temp = f'\nChecking user input data ({date_string})'
    # running_status.add_message(temp) 
    # 파일명 메시지 (전체 파란색)
    temp = f'<span style="color:blue;">Filename : {file_name} / Pagename : {config.current_page}</span>'
    running_status.add_message(temp)

    # 날짜 메시지 (문장 파란색, 날짜만 빨간색)
    temp = f'<span style="color:blue;">\nChecking user input data (<span style="color:red;">{date_string}</span>)</span>'
    running_status.add_message(temp)

    # ✅ 계산가능한 page 인지 검사
    calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    if calculation_sheet is not None:
        has_all_attributes = False
        for obj in calculation_sheet.findall(".//object"):
            if obj.get("hydro_version") and obj.get("pressure_selection") and obj.get("running_status"):
                has_all_attributes = True
                config.pressure_selection = (obj.get("pressure_selection")).lower()
                break # 하나라도 빠진 경우 처리 필요함..
            else:
                print(f"⚠️ This page ({config.current_page}) is not a calculation page.")
                sys.exit(1)
    if not has_all_attributes:            
        print(f"⚠️ This page ({config.current_page}) is not a calculation page.")
        sys.exit(1)


    # ✅ nozzle에 A_tag_no 부여
    x = module_graphic.update_Nozzle_A_tag_no_from_Equipment(root)

    # ✅ user input 값 체크
    user_input_error = module_graphic.check_input_value(root) # 사용자 Input값이 문자인지 숫자인지 체크
    if user_input_error: #에러가 있다는 뜻
        result_text = '\n'.join(f"  {i+1}. {item}" for i, item in enumerate(user_input_error))
        print("⚠️ user input error \n" + result_text)  # 에러 메시지 출력
        result_text = "⚠️ user input error \n"
        running_status.add_message(result_text)  # 자동 줄바꿈 포함
        # module_output_drawio.tree_write_running_status (file_path, root, running_status)
        # module_output_drawio.tree_write_in_drawio_file (file_path, root)
        # sys.exit(1)
        return abnormal_termination(file_path, root, running_status)  # 에러 발생시 종료
    else: #에러 없으면   
        result_text = '\n\n✅ No Error in user input values'
        running_status.add_message(result_text)  # 자동 줄바꿈 포함
    
    # ✅ Loop 체크
    running_status.add_message("\nSearching hydraulic loop\n")
    routes, routes_id, line_ids = module_graphic.find_routes_from_drawio(root)
    
    for i, route in enumerate(routes):
        # print(f" Loop {i}. : "," -> ".join(route))  # A_tag_no로 변환된 경로 출력
        temp = f"  Loop {{{i+1}}} : " + " \u2192 ".join(route)
        running_status.add_message(temp + "\n")
        # print(route) tag_no로 변환된 경로 출력
    # ✅ Loop 안의 data input 이름을 계산에 편한 보편적 이름으로 바꾸고 문자를 숫자로 변경, type 결정
    routes = module_graphic.object_classification(root, routes_id, line_ids) 
    module_graphic.verify_routes(routes)
    
    # print(routes)
    # ✅ Loop 분류 (같은 Header에 묶인것을 분류함)
    grouped_routes = module_graphic.group_routes_by_overlap(routes)
    # print(grouped_routes)
    running_status.add_message("\nGrouping hydraulic loop\n")
    for idx, group in enumerate(grouped_routes):
        # print(f"Group {idx + 1}: {[ [obj for obj in route] for route in group ]} \n")
        # print (idx, "\nn", group,"\nn")
        running_status.add_message(f"  Group {{{idx+1}}} : \n") 
        for loop in group: # error 코드 만들어야 함. 잘못 연결된 경우 멈추는 경우에 대하여 ..
            temp= []
            for item in loop :
                if item['type'] in ['liquid_line', 'vapor_line', 'two_phase_line'] :
                    temp.append(f'[{item['A_tag_no']}]')    
                else :    
                    temp.append(item['A_tag_no'])
            temp_join = f"     " + " \u2192 ".join(str(item) for item in temp) # 오른쪽 화살표
            running_status.add_message(temp_join + "\n")
            # print("  Grouping hydraulic loop done.\n")
    # ✅ Analyzing loop & group
    running_status.add_message("\nAnalyzing hydraulic loop")
    for route in routes :
        for item in route :
            count_control_vlave = sum(1 for item in route if item['type'] == 'control_valve')
            if count_control_vlave >= 2 : 
                temp = f"""  impossible to solve {count_control_vlave}ea serial control valves in this loop. \n  please, 
                install only one control valve and fixed pressure drop control valves in one loop."""
                running_status.add_message(temp)
                print(temp)
                sys.exit(1)
                return
            count_variable_pump = sum(1 for item in route if item['type'] == 'variable_pump')
            if count_variable_pump >= 2 : 
                temp = f"""  impossible to solve {count_variable_pump}ea serial pumps in this loop. \n  please, 
                install only one pump and fixed diff. pressure pumps in one loop."""
                running_status.add_message(temp)
                print(temp) 
                sys.exit(1)         
                return
    temp = '\n \nNo Error in each hydraulic loop.'
    running_status.add_message(temp)
    
    # ✅ Hyd calculation
    routes = module_hyd.calculate_each_route_object_reverse (routes)
    grouped_routes = module_graphic.group_routes_by_overlap(routes)
    header_grouped_routes = module_hyd.group_header_determination (grouped_routes)


    final_grouped_routes = module_hyd.calculate_each_route_object_forward(header_grouped_routes)
    
    # ✅ line만 처리
    only_lines =module_hyd.extract_lines (final_grouped_routes)
    # print(only_lines)
    line_data = module_mapping.stream_mapping (only_lines, config.pressure_selection)
    sorted_line_data = dict(sorted(line_data.items()))

    # pressure_selection 값에 따라 단위 설정
    pressure_unit = 'bar' if config.pressure_selection == 'bar' else 'kg/cm2'
    pressure_unit_g = f'{pressure_unit}.g'
    pressure_unit_100m = f'{pressure_unit}/100m'

    # index 리스트 정의
    index = [
        'phase',
        'line size [inch]',
        'mass flowrate [kg/hr]',
        'volume flowrate [m3/hr]',
        'density [kg/m3]',
        'temperature [deg.C]',
        'viscosity [cP]',
        'roughness [ft]',
        'equiv. length [m]',
        'reynolds num [-]',
        'velocity [m/sec]',
        f'static head [{pressure_unit}]',
        f'inlet press. [{pressure_unit_g}]',
        f'outlet press. [{pressure_unit_g}]',
        f'press. drop [{pressure_unit}]',
        f'\u0394P [{pressure_unit_100m}]'
    ]
    # DataFrame 생성
    df = pd.DataFrame (sorted_line_data, index)
    root_elem, CalculationResult_layer_id, top_left_position = module_output_drawio.clear_calculation_result_contents_only(root)
    # print(top_left_position)
    if top_left_position: # 사용자가 이동하면서 지정한 위치
        start_x, start_y = top_left_position
        start_y = start_y -15
    else:
        start_x, start_y = 30, 900
    module_output_drawio.add_dataframe_to_layer(df, root_elem, CalculationResult_layer_id, start_x=start_x, start_y=start_y)
    # self.text_editor.append(df.to_string(index=True)) # 사용자 뷰에 stream table 보여주기  
    module_output_drawio.tree_write_lines (file_path, root, only_lines, final_grouped_routes )
    # print(df)

    # ✅ control valve & fixed valve 처리 
    only_valves = module_hyd.extract_control_valves (final_grouped_routes)
    # print (only_valves)
    valves_data = module_mapping.valve_mapping (only_valves)     
    sorted_control_valves = dict(sorted(valves_data.items()))
    if (sorted_control_valves) :  # control valve가 없는 경우도 많다.
        index_cv = ['inlet P', 'outlet P', f'\u0394P [{pressure_unit}]' ]       
        df_cv = pd.DataFrame (sorted_control_valves, index_cv)
        # print(df_cv)
        module_output_drawio.add_dataframe_to_layer(df_cv, root_elem, CalculationResult_layer_id, start_x=958, start_y=20, index_col_width=55, col_width=45, cell_height=15, font_size=9, max_cols=3, row_spacing=2)
        # self.text_editor.append(df_cv.to_string(index=True)) # 사용자 뷰에 Control valve table 보여주기  
        module_output_drawio.tree_write_valves (file_path, root, only_valves)

    # ✅ pump 처리 
    only_pumps, only_contents = module_hyd.extract_pumps (final_grouped_routes)
    module_output_drawio.tree_write_pumps (file_path, root, only_pumps)
    module_output_drawio.add_string_content_to_drawio (only_contents, root_elem, CalculationResult_layer_id, start_x=960, start_y=500, col_width=100, cell_height=100, font_size=10)
    
    # ✅ deviation 처리 
    only_deviation = module_hyd.extract_deviation (final_grouped_routes)
    # print (only_deviation)
    module_output_drawio.add_string_content_to_drawio (only_deviation, root_elem, CalculationResult_layer_id, start_x=15, start_y=15, col_width=400, cell_height=30, font_size=10)
    
    def get_local_ip():
        """로컬 IP 주소를 반환"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except Exception:
            return "UNKNOWN_IP"

    def get_hostname():
        """호스트 이름 반환"""
        try:
            return socket.gethostname()
        except Exception:
            return "UNKNOWN_HOST"

    def generate_watermark_text():
        """워터마크 텍스트 생성"""
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        ip_address = get_local_ip()
        hostname = get_hostname()
        watermark_text = f"HYDRO CONFIDENTIAL {timestamp} {ip_address} {hostname}"
        return watermark_text

# # 사용 예시
# print(generate_watermark_text())


#     # 사용 예시
#     # print(generate_watermark_text())
#     asd= generate_watermark_text()
    if config.user == "guest" : 
        module_output_drawio.add_watermark_to_layer (root_elem, CalculationResult_layer_id, generate_watermark_text())
    else:
        pass
    
    # ✅ running_status in drawio.file 
    module_output_drawio.tree_write_running_status (file_path, root, running_status, generate_watermark_text())

    # ✅ save tree in drawio.file 
    module_output_drawio.tree_write_in_drawio_file (file_path, root)



    # ✅ open saved drawio.file        
    # def find_drawio_executable(start_path):
    #     for root, dirs, files in os.walk(start_path):
    #         for file in files:
    #             if file.lower() == "draw.io.exe":
    #                 return os.path.join(root, file)
    #     return None
    # global drawio_path
    # drawio_path = find_drawio_executable("C:\\Program Files")
    return

def abnormal_termination (file_path, root, running_status):
    module_output_drawio.tree_write_running_status (file_path, root, running_status)
    module_output_drawio.tree_write_in_drawio_file (file_path, root)
    sys.exit(1)