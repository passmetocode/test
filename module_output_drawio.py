import xml.etree.ElementTree as ET
import pandas as pd
from xml.dom import minidom  # for pretty print
import config
import re
import uuid

def clear_calculation_result_contents_only(root):
    # 1. 'hydro' diagram 찾기
    diagram = next(
        (d for d in root.findall("diagram") if d.attrib.get("name") == config.current_page),
        None
    )
    if diagram is None:
        raise ValueError("hydro diagram을 찾을 수 없습니다.")

    graph_model = diagram.find("mxGraphModel")
    root_elem = graph_model.find("root")

    # 2. calculation_result 레이어 ID 찾기
    stream_layer_id = None
    for cell in root_elem.findall("mxCell"):
        if cell.attrib.get("value") == "Calculation Result":
            stream_layer_id = cell.attrib["id"]
            break

    if not stream_layer_id:
        raise ValueError("Calculation Result 레이어를 찾을 수 없습니다.")


    # 2.5. 기존 좌표 찾기
    top_left_position_stream = None
    for cell in root_elem.findall("mxCell"):
        if cell.attrib.get("parent") == stream_layer_id:
            value = cell.attrib.get("value")
            if value and value.strip().lower() in ["phase", "line size[inch]"]:  # 기준 셀
                geometry = cell.find("mxGeometry")
                if geometry is not None:
                    x = float(geometry.attrib.get("x", 0))
                    y = float(geometry.attrib.get("y", 0))
                    top_left_position_stream = (x, y)
                    break

    top_left_position_control_valve = None
    for cell in root_elem.findall("mxCell"):
        if cell.attrib.get("parent") == stream_layer_id:
            value = cell.attrib.get("value")
            if value and value.strip().lower() in ["inlet p", "outlet p"]:  # 기준 셀
                geometry = cell.find("mxGeometry")
                if geometry is not None:
                    x = float(geometry.attrib.get("x", 0))
                    y = float(geometry.attrib.get("y", 0))
                    top_left_position_control_valve = (x, y)
                    break

    top_left_position_pump_context_box = None
    top_left_position_deviation_context_box = None

    for cell in root_elem.findall("mxCell"):
        if cell.attrib.get("parent") != stream_layer_id:
            continue

        style = cell.attrib.get("style", "")
        if "boxName=pump_content_box" in style or "boxName=deviation_content_box" in style:
            geometry = cell.find("mxGeometry")
            if geometry is not None:
                x = float(geometry.attrib.get("x", 0))
                y = float(geometry.attrib.get("y", 0))

                if "boxName=pump_content_box" in style:
                    top_left_position_pump_context_box = (x, y)

                elif "boxName=deviation_content_box" in style:
                    top_left_position_deviation_context_box = (x, y)



    # 3. Calculation Result 레이어 아래 셀만 삭제 (재귀적으로)
    def collect_children_ids(parent_id):
        children = []
        for cell in root_elem.findall("mxCell"):
            if cell.attrib.get("parent") == parent_id:
                children.append(cell.attrib["id"])
                children += collect_children_ids(cell.attrib["id"])
        return children

    to_delete_ids = collect_children_ids(stream_layer_id)

    for cell in root_elem.findall("mxCell"):
        if cell.attrib.get("id") in to_delete_ids:
            root_elem.remove(cell)

    return (
        root_elem,
        stream_layer_id,
        top_left_position_stream,
        top_left_position_control_valve,
        top_left_position_pump_context_box,
        top_left_position_deviation_context_box
    )

def add_dataframe_to_layer(df, root_elem, parent_id, start_x=30, start_y=900,
                           index_col_width=110, col_width=50, cell_height=15,
                           font_size=9, max_cols=20, row_spacing=2):
    import uuid
    import xml.etree.ElementTree as ET

    def gen_id():
        return str(uuid.uuid4())

    def add_cells(df, root_elem, parent_id, start_x, start_y, index_col_width,
                  col_width, cell_height, font_size, max_cols,
                  row_offset=0, col_offset=0, row_spacing=20):
        # # 💡 컬럼명 (Stream No. 등)
        # for col_index, col_name in enumerate(df.columns[col_offset:col_offset + max_cols]):
        #     x = start_x + index_col_width + col_width * col_index
        #     y = start_y + row_offset * (cell_height + row_spacing)

        #     cell_id = gen_id()
        #     cell = ET.SubElement(root_elem, "mxCell", {
        #         "id": cell_id,
        #         "value": str(col_name),
        #         "style": f"shape=rectangle;whiteSpace=wrap;fontSize={font_size};html=1;fontStyle=1;",
        #         "parent": parent_id,
        #         "vertex": "1"
        #     })
        #     geometry = ET.SubElement(cell, "mxGeometry", {
        #         "x": str(x),
        #         "y": str(y),
        #         "width": str(col_width),
        #         "height": str(cell_height)
        #     })
        #     geometry.set("as", "geometry")
        # 💡 컬럼명 (Stream No. 등)
        for col_index, col_name in enumerate(df.columns[col_offset:col_offset + max_cols]):
            x = start_x + index_col_width + col_width * col_index
            y = start_y + row_offset * (cell_height + row_spacing)

            cell_id = gen_id()
            
            # 글자 수에 따라 폰트 크기 조절
            adjusted_font_size = 7 if len(str(col_name)) >= 8 else font_size

            cell = ET.SubElement(root_elem, "mxCell", {
                "id": cell_id,
                "value": str(col_name),
                "style": f"shape=rectangle;whiteSpace=wrap;fontSize={adjusted_font_size};html=1;fontStyle=1;",
                "parent": parent_id,
                "vertex": "1"
            })
            geometry = ET.SubElement(cell, "mxGeometry", {
                "x": str(x),
                "y": str(y),
                "width": str(col_width),
                "height": str(cell_height)
            })
            geometry.set("as", "geometry")

        # 💡 인덱스 (A, B, C...)
        for row_index, idx in enumerate(df.index):
            if str(idx).strip().lower() == "criteria":
                continue
            x = start_x
            y = start_y + (row_index + 1) * cell_height + row_offset * (cell_height + row_spacing)

            cell_id = gen_id()
            cell = ET.SubElement(root_elem, "mxCell", {
                "id": cell_id,
                "value": str(idx),
                "style": f"shape=rectangle;whiteSpace=wrap;fontSize={font_size};html=1;align=left;",
                "parent": parent_id,
                "vertex": "1"
            })
            geometry = ET.SubElement(cell, "mxGeometry", {
                "x": str(x),
                "y": str(y),
                "width": str(index_col_width),
                "height": str(cell_height)
            })
            geometry.set("as", "geometry")

        # # 💡 기준값 범위 설정
        # limits = {
        #     "liquid": {
        #         "velocity_min": 0.3,
        #         "velocity_max": 3.0,
        #         "dp_min": 0.3,
        #         "dp_max": 0.6
        #     },
        #     "vapor": {
        #         "velocity_min": 10.0,
        #         "velocity_max": 30.0,
        #         "dp_min": 2.0,
        #         "dp_max": 5.0
        #     },
        #     "2 phase": {
        #         "velocity_min": 10.0,
        #         "velocity_max": 25.0,
        #         "dp_min": 0.8,
        #         "dp_max": 1.5
        #     }
        # }

        # 💡 데이터 셀
        for row_index, (idx, row) in enumerate(df.iterrows()):  # 한줄씩 아래로 
            if str(idx).strip().lower() == "criteria":  # ✅ "criterial" 인덱스는 출력 제외
                continue
            for col_index, value in enumerate(row[col_offset:col_offset + max_cols]): # 오른쪽으로 
                x = start_x + index_col_width + col_width * col_index
                y = start_y + (row_index + 1) * cell_height + row_offset * (cell_height + row_spacing)

                style = f"shape=rectangle;whiteSpace=wrap;fontSize={font_size};html=1;"

                try:
                    criteria = df.iloc[-1, col_offset + col_index]
                    if isinstance(criteria, dict):
                        velocity_min = criteria.get('min_vel')
                        velocity_max = criteria.get('max_vel')
                        dp_min = criteria.get('min_dp')
                        dp_max = criteria.get('max_dp')
                        # print (velocity_max)

                    # if df.shape[0] > 0 and col_offset + col_index < len(df.columns):
                    #     phase = str(df.iloc[0, col_offset + col_index]).strip().lower()
                    #     criteria = limits.get(phase, {})
                    #     velocity_min = criteria.get("velocity_min")
                    #     velocity_max = criteria.get("velocity_max")
                    #     dp_min = criteria.get("dp_min")
                    #     dp_max = criteria.get("dp_max")
                    else:
                        velocity_min = velocity_max = dp_min = dp_max = None

                    if idx == "velocity [m/sec]" and velocity_min is not None and velocity_max is not None:
                        if float(value) < velocity_min:
                            value = f"<font color='#0000ff'>{value}</font>"  # Blue for low
                            style += "fontColor=blue;"
                        elif float(value) > velocity_max:
                            value = f"<font color='#ff0000'>{value}</font>"  # Red for high
                            style += "fontColor=red;"

                    elif "ΔP" in idx and dp_min is not None and dp_max is not None:
                        if float(value) < dp_min:
                            value = f"<font color='#0000ff'>{value}</font>"  # Blue for low
                            style += "fontColor=blue;"
                        elif float(value) > dp_max:
                            value = f"<font color='#ff0000'>{value}</font>"  # Red for high
                            style += "fontColor=red;"

                except Exception:
                    pass

                cell_id = gen_id()
                cell = ET.SubElement(root_elem, "mxCell", {
                    "id": cell_id,
                    "value": str(value),
                    "style": style,
                    "parent": parent_id,
                    "vertex": "1"
                })
                geometry = ET.SubElement(cell, "mxGeometry", {
                    "x": str(x),
                    "y": str(y),
                    "width": str(col_width),
                    "height": str(cell_height)
                })
                geometry.set("as", "geometry")

        # 💡 다음 열 그룹 재귀 호출
        if col_offset + max_cols < len(df.columns):
            add_cells(df, root_elem, parent_id, start_x, start_y,
                      index_col_width, col_width, cell_height,
                      font_size, max_cols,
                      row_offset + len(df.index) + 1,
                      col_offset + max_cols,
                      row_spacing)

    add_cells(df, root_elem, parent_id, start_x, start_y,
              index_col_width, col_width, cell_height,
              font_size, max_cols, row_spacing=row_spacing)

def add_string_content_to_drawio(content, root_elem, parent_id, start_x=30, start_y=900, col_width=200, cell_height=100, font_size=9, box_name="content_box"):
    # ✅ deviation, pump가 이걸 사용해서 나옴. 테이블 없는것은 이쪽으로..
    import uuid
    def gen_id():
        return str(uuid.uuid4())
    
    def calculate_box_size(text, col_width, cell_height, font_size):
    # 텍스트 길이에 따라 박스 크기 계산
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines)
        box_width = max(col_width, max_line_length * font_size * 0.6)  # 글자당 약 0.6 * font_size 만큼의 너비 필요
        box_height = max(cell_height, len(lines) * (font_size + 2))  # 줄당 font_size + 2 만큼의 높이 필요
        return box_width, box_height
    col_width, cell_height = calculate_box_size (content, col_width, cell_height, font_size)
    # draw.io 형식으로 변환
    cell_id = gen_id()
    cell = ET.SubElement(root_elem, "mxCell", {
        "id": cell_id,
        "value": content,
        "style": f"shape=rectangle;whiteSpace=wrap;fontSize={font_size};html=1;align=left;strokeColor=none;fillColor=none;boxName={box_name};",
        "parent": parent_id,
        "vertex": "1"
    })
    geometry = ET.SubElement(cell, "mxGeometry", {
        "x": str(start_x),
        "y": str(start_y),
        "width": str(col_width),
        "height": str(cell_height)
    })
    geometry.set("as", "geometry")
  
# def tree_write_lines (file_path, root, only_lines, final_grouped_routes ): # ✅ drawio 파일에 write
#     calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
#     for obj in calculation_sheet.findall('.//object'):
#         for line in only_lines :
#             if obj.get('id') == line['ID'] :
#               obj.set('o1_reynolds', "{:.0f}".format(line['reynolds']))
#               obj.set('o2_velocity', "{:.2f}".format(line['velocity']))
#               obj.set('o3_friction_loss', "{:.2f}".format(line['pressure_drop']))
#               obj.set('o4_static_pressure', "{:.2f}".format(line['static_pressure']))
#     return 

def tree_write_lines(file_path, root, only_lines, final_grouped_routes):
    # 현재 페이지의 diagram 찾기
    calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    if calculation_sheet is None:
        print(f"❌ diagram '{config.current_page}' not found.")
        return

    # only_lines의 ID만 추출
    line_ids = {line['ID'] for line in only_lines}
    # final_grouped_routes가 한 덩어리로 묶여 있을 경우 풀어줌
    if len(final_grouped_routes) == 1 and isinstance(final_grouped_routes[0], list):
        final_grouped_routes = final_grouped_routes[0]

    # 모든 선을 strokeWidth=1로 초기화 (only_lines에 포함된 것만)
    for obj in calculation_sheet.findall('.//object'):
        obj_id = obj.get('id')
        if obj_id in line_ids:
            mxcell = obj.find('.//mxCell')
            if mxcell is not None and mxcell.get('edge') == '1':
                style = mxcell.get('style') or ''
                style = re.sub(r'strokeWidth=\d+;?', '', style)
                mxcell.set('style', f"{style}strokeWidth=1;")
    # 첫 루트의 선만 strokeWidth=2로 강조
    if final_grouped_routes:
        first_route = final_grouped_routes[0]
        first_route_ids = {line['ID'] for line in first_route if isinstance(line, dict) and 'ID' in line}

        for obj in calculation_sheet.findall('.//object'):
            obj_id = obj.get('id')
            if obj_id in first_route_ids and obj_id in line_ids:
                mxcell = obj.find('.//mxCell')
                if mxcell is not None and mxcell.get('edge') == '1':
                    style = mxcell.get('style') or ''
                    style = re.sub(r'strokeWidth=\d+;?', '', style)
                    mxcell.set('style', f"{style}strokeWidth=2;")

    # 계산 결과를 object에 기록
    for obj in calculation_sheet.findall('.//object'):
        obj_id = obj.get('id')

        for line in only_lines:
            if line.get('type') == "user_line":
                continue  # 이 object는 건너뜀            
            if obj_id == line['ID']:
                obj.set('o1_reynolds', f"{line.get('reynolds', 0):.0f}")
                obj.set('o2_velocity', f"{line.get('velocity', 0):.2f}")
                obj.set('o3_friction_loss', f"{line.get('pressure_drop', 0):.2f}")
                obj.set('o4_static_pressure', f"{line.get('static_pressure', 0):.2f}")
    return

def tree_write_valves (file_path, root, only_valves): # ✅ drawio 파일에 write
    calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    for obj in calculation_sheet.findall('.//object'):
        for valve in only_valves :
            if obj.get('id') == valve['ID'] and valve['type'] == 'control_valve' :
              obj.set('o1_differential_pressure', "{:.2f}".format(valve['pressure_drop']))
    return 

def tree_write_pumps (file_path, root, only_pumps): # ✅ drawio 파일에 write
    calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    for obj in calculation_sheet.findall('.//object'):
        for pump in only_pumps :
            if (obj.get('id') == pump['ID']) and (pump['type'] == 'variable_pump' or pump['type'] == 'fixed_pump')  :            
                obj.set('o2_differential_head', "{:.2f}".format(pump['differential_head']))          
                obj.set('o3_suction_pressure', "{:.2f}".format(pump['P_in']))
                obj.set('o4_discharge_pressure', "{:.2f}".format(pump['P_out']))
                obj.set('o5_NPSHa', "{:.2f}".format(pump['NPSHa']))                                            
                if obj.get('id') == pump['ID'] and pump['type'] == 'variable_pump' :
                    obj.set('o1_differential_pressure', "{:.2f}".format(pump['differential_pressure']))
    return 

# def tree_write_in_drawio_file (file_path, root) :
#     # XML pretty print 저장
#     rough_string = ET.tostring(root, encoding="utf-8")
#     reparsed = minidom.parseString(rough_string)
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(reparsed.toprettyxml(indent="  "))  
#     return 

# def tree_write_in_drawio_file(file_path, root):
#     # # XML 문자열 생성 (pretty print 없이)
#     # xml_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
#     # xml_str = xml_str.replace('\n', '&#10;')  # Direct replacement

#     # # XML 파일에 직접 저장 (불필요한 공백 없이)
#     # with open(file_path, "w", encoding="utf-8") as f:
#     #     f.write(xml_str)

#     #     rough_string = ET.tostring(self.root, encoding='utf-8')
#     #     reparsed = minidom.parseString(rough_string)
#     #     with open(self.file_path, 'w', encoding='utf-8') as f:
#     #         f.write(reparsed.toprettyxml(indent='  '))


#     # Save XML without extra escape of '&'
#     rough_string = ET.tostring(root, encoding='utf-8').decode('utf-8')
#     # Ensure &#10; remains intact without being converted
#     rough_string = rough_string.replace('&amp;#10;', '&#10;').replace('&#10;', '&#xa;')

#     with open(file_path, 'w', encoding='utf-8') as f:
#         f.write(rough_string)                    
#     return

def tree_write_in_drawio_file(file_path, root):
    # mxfile 태그를 hydrofile로 되돌림
    if root.tag == 'mxfile':
        root.tag = 'hydrofile'

    # XML 문자열로 변환
    rough_string = ET.tostring(root, encoding='utf-8').decode('utf-8')

    # &amp;#10; 관련 처리
    rough_string = rough_string.replace('&amp;amp;#10;', '&amp;#10;').replace('&amp;#10;', '&amp;#xa;')

    # 파일에 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(rough_string)
    return


def tree_write_running_status (file_path, root, running_status, water_mark): # ✅ drawio 파일에 write
    def convert_to_encoded_string(text: str) -> str:
        return text.replace("\n", "&#10;")
    # text = "yangslkfgsdoifgsdlfgjsl;dkfgjsdf;kgjsd;lfjkgs;dlfkgjs;ldkfgjs;ldkfgjs;ldkfgjs;ldkfgjsdlkgfsldfkjasldkfjalskdfj"
    converted_text = convert_to_encoded_string(running_status.get_combined_message())
    # print(running_status.get_combined_message())
    # print()
    # print(converted_text)    

    calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    for obj in calculation_sheet.findall(".//object"):
        if obj.get("label") is not None and obj.get("id") is not None and obj.get("hydro_version"):
            obj.set('running_status', converted_text)
            obj.set('hydro_version', 'v1.0.0 - beta') # version 정보 추가
            obj.set('user_information', water_mark)
    return



def add_watermark_to_layer(
    root_elem,
    parent_id,
    text="For educational purposes only (교육용)",
    x=600, y=20,
    width=1, height=1,
    font_size=14,
    rotation=0,
    opacity=100,
    font_color="#CCCCCC"
):
    """
    hydro에 워터마크 노드를 추가하는 함수

    Parameters:
    - root_elem: XML의 <root> 요소
    - parent_id: 부모 노드 ID
    - text: 워터마크 텍스트
    - x, y: 위치 좌표
    - width, height: 크기
    - font_size: 폰트 크기
    - rotation: 회전 각도
    - opacity: 불투명도 (0~100)
    - font_color: 폰트 색상 (예: "#CCCCCC")

    Returns:
    - 생성된 셀의 ID
    """
    def gen_id():
        return str(uuid.uuid4())

    cell_id = gen_id()
    style = (
        f"locked=1;opacity={opacity};rotation={rotation};fillColor=none;"
        f"strokeColor=none;fontSize={font_size};fontColor={font_color};"
    )

    cell = ET.SubElement(root_elem, "mxCell", {
        "id": cell_id,
        "value": text,
        "style": style,
        "parent": parent_id,
        "vertex": "1"
    })

    geometry = ET.SubElement(cell, "mxGeometry", {
        "x": str(x),
        "y": str(y),
        "width": str(width),
        "height": str(height),
        "as": "geometry"
    })

    return cell_id
