import xml.etree.ElementTree as ET
import pandas as pd
from xml.dom import minidom  # for pretty print
import config

def clear_stream_result_contents_only(root):
    # 1. 'hydro' diagram 찾기
    diagram = next(
        (d for d in root.findall("diagram") if d.attrib.get("name") == config.current_page),
        None
    )
    if diagram is None:
        raise ValueError("hydro diagram을 찾을 수 없습니다.")

    graph_model = diagram.find("mxGraphModel")
    root_elem = graph_model.find("root")

    # 2. stream_result 레이어 ID 찾기
    stream_layer_id = None
    for cell in root_elem.findall("mxCell"):
        if cell.attrib.get("value") == "stream_result":
            stream_layer_id = cell.attrib["id"]
            break

    if not stream_layer_id:
        raise ValueError("stream_result 레이어를 찾을 수 없습니다.")

    # 3. stream_result 레이어 아래 셀만 삭제 (재귀적으로)
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

    return root_elem, stream_layer_id

def add_dataframe_to_layer(df, root_elem, parent_id, start_x=30, start_y=900,
                           index_col_width=110, col_width=50, cell_height=15, font_size=9, max_cols=20, row_spacing=2):
    import uuid
    def gen_id():
        return str(uuid.uuid4())

    def add_cells(df, root_elem, parent_id, start_x, start_y, index_col_width, col_width, cell_height, font_size, max_cols, row_offset=0, col_offset=0, row_spacing=20):
        # 💡 컬럼명 (Stream No. 등) 출력
        for col_index, col_name in enumerate(df.columns[col_offset:col_offset + max_cols]):
            x = start_x + index_col_width + col_width * col_index
            y = start_y + row_offset * (cell_height + row_spacing)  # 새로운 행으로 이동

            cell_id = gen_id()
            cell = ET.SubElement(root_elem, "mxCell", {
                "id": cell_id,
                "value": str(col_name),
                "style": f"shape=rectangle;whiteSpace=wrap;fontSize={font_size};html=1;fontStyle=1;",  # fontStyle=1 → bold
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
            x = start_x
            y = start_y + (row_index + 1) * cell_height + row_offset * (cell_height + row_spacing)  # 헤더 때문에 +1

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

        # 💡 데이터
        for row_index, (_, row) in enumerate(df.iterrows()):
            for col_index, value in enumerate(row[col_offset:col_offset + max_cols]):
                x = start_x + index_col_width + col_width * col_index
                y = start_y + (row_index + 1) * cell_height + row_offset * (cell_height + row_spacing)  # 새로운 행으로 이동

                cell_id = gen_id()
                cell = ET.SubElement(root_elem, "mxCell", {
                    "id": cell_id,
                    "value": str(value),
                    "style": f"shape=rectangle;whiteSpace=wrap;fontSize={font_size};html=1;",
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

        # 재귀적으로 다음 열 그룹 추가
        if col_offset + max_cols < len(df.columns):
            add_cells(df, root_elem, parent_id, start_x, start_y, index_col_width, col_width, cell_height, font_size, max_cols, row_offset + len(df.index) + 1, col_offset + max_cols, row_spacing)

    add_cells(df, root_elem, parent_id, start_x, start_y, index_col_width, col_width, cell_height, font_size, max_cols, row_spacing=row_spacing)

def add_string_content_to_drawio(content, root_elem, parent_id, start_x=30, start_y=900, col_width=200, cell_height=100, font_size=9):
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
        "style": f"shape=rectangle;whiteSpace=wrap;fontSize={font_size};html=1;align=left;strokeColor=none;fillColor=none;",
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
  
def tree_write_lines (file_path, root, only_lines): # ✅ drawio 파일에 write
    calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    for obj in calculation_sheet.findall('.//object'):
        for line in only_lines :
            if obj.get('id') == line['ID'] :
              obj.set('o1_reynolds', "{:.0f}".format(line['reynolds']))
              obj.set('o2_velocity', "{:.2f}".format(line['velocity']))
              obj.set('o3_friction_loss', "{:.2f}".format(line['pressure_drop']))
              obj.set('o4_static_pressure', "{:.2f}".format(line['static_pressure']))
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

def tree_write_in_drawio_file(file_path, root):
    # # XML 문자열 생성 (pretty print 없이)
    # xml_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
    # xml_str = xml_str.replace('\n', '&#10;')  # Direct replacement

    # # XML 파일에 직접 저장 (불필요한 공백 없이)
    # with open(file_path, "w", encoding="utf-8") as f:
    #     f.write(xml_str)

    #     rough_string = ET.tostring(self.root, encoding='utf-8')
    #     reparsed = minidom.parseString(rough_string)
    #     with open(self.file_path, 'w', encoding='utf-8') as f:
    #         f.write(reparsed.toprettyxml(indent='  '))


    # Save XML without extra escape of '&'
    rough_string = ET.tostring(root, encoding='utf-8').decode('utf-8')
    # Ensure &#10; remains intact without being converted
    rough_string = rough_string.replace('&amp;#10;', '&#10;').replace('&#10;', '&#xa;')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(rough_string)                    
    return


def tree_write_running_status (file_path, root, running_status): # ✅ drawio 파일에 write
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
    return