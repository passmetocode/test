import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from xml.dom import minidom  # for pretty print
import config

line_number = 1

import xml.etree.ElementTree as ET
from collections import defaultdict

def update_Nozzle_A_tag_no_from_Equipment(root, page_name):
    """
    diagram[@name=page_name] 하위 object 중 i1_operating_pressure가 있는 노즐에
    같은 parent 내 object.label, object/mxCell.value 등에서 라벨을 추출해
    <label>:Noz 형식으로 A_tag_no 세팅

    - 라벨 우선순위: 1) i1_operating_pressure 없는 object의 label > 
                   2) i1_operating_pressure 없는 object의 mxCell.value >
                   3) 같은 parent를 가진 다른 mxCell의 value >
                   4) "none"
    """
    parent2obj = defaultdict(list)
    # object들을 parent id 기준으로 그룹핑
    for obj in root.findall(f".//diagram[@name='{page_name}']//object"):
        mxcell = obj.find("mxCell")
        if mxcell is None:
            continue
        parent_id = mxcell.get("parent")
        if parent_id:
            parent2obj[parent_id].append((obj, mxcell))

    for parent_id, objlist in parent2obj.items():
        label = ""
        # 1) i1_operating_pressure 없는 object의 label 우선
        for obj, mxcell in objlist:
            if not obj.get("i1_operating_pressure"):
                if obj.get("label") and obj.get("label").strip():
                    label = obj.get("label").strip()
                    break
                # 2) label 없으면 object의 mxCell.value
                if mxcell is not None and mxcell.get("value") and mxcell.get("value").strip():
                    label = mxcell.get("value").strip()
                    break
        # 3) 그래도 label 없으면 같은 parent의 모든 mxCell 중 value 있는 것
        if not label:
            for mxcell in root.findall(f".//diagram[@name='{page_name}']//mxCell[@parent='{parent_id}']"):
                value = mxcell.get("value")
                if value and value.strip():
                    label = value.strip()
                    break
        # 4) 다 없으면 "none"
        tag_value = (label if label else "none") + ":Noz"
        # 그룹 내 i1_operating_pressure 있는 object 모두에 부여
        for obj, _ in objlist:
            if obj.get("i1_operating_pressure"):
                obj.set("A_tag_no", tag_value)

# 사용 예시: XML 문자열에서 파싱 후 함수 실행
if __name__ == "__main__":
    xml_content = '''여기에 XML을 복사/붙여넣으세요'''
    root = ET.fromstring(xml_content)
    page_name = config.current_page  # 예시: diagram의 name 값을 확인하여 지정
    update_Nozzle_A_tag_no_from_Equipment(root, page_name)
    # XML 결과 확인 또는 저장
    print(ET.tostring(root, encoding="unicode"))
    # 또는 결과를 파일로 저장
    # tree = ET.ElementTree(root)
    # tree.write("output.xml", encoding="utf-8")


def load_xml(file_path):
    """ XML 파일을 로드하고 루트를 반환하는 함수 """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except Exception as e:
        print(f"XML 파일을 로드하는 중 오류 발생: {e}")
        return None

def is_convertible_to_number(input_value):
    if input_value == None : input_value =""
    try:
        return isinstance(float(input_value), float)
    except ValueError:
        return False

def validate_object_data(object):
    global line_number
    object_id = object.get('id')
    # 압력 단위 설정
    unit = 'bar' if config.pressure_selection == 'bar' else 'kg/cm2'
    unit_g = f'{unit}.g'
    unit_A = f'{unit}.A'
    error_message=""
    input_error_message = []    
    if 'i2_density' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of liquid line
        if not is_convertible_to_number(object.attrib.get('i1_flowrate')) :
            error_message = "line no. " + str(line_number) + " {error: i1_flowrate = " + object.attrib.get('i1_flowrate') +" m3/hr}"
            input_error_message.append (error_message) 

        # value = object.attrib.get('i1_flowrate')
        # try:
        #     float_value = float(value)
        #     if float_value <= 0:
        #         raise ValueError(f"Flowrate {line_number} must be greater than 0")  # 👈 음수 및 0 차단
        #     object.attrib['i1_flowrate'] = float_value  # ✅ 정상 값일 때만 저장
        # except (ValueError, TypeError):
        #     error_message = f"line no. {line_number} {{error: i1_flowrate = {value} m3/hr}}"
        #     input_error_message.append(error_message)



        if not is_convertible_to_number(object.attrib.get('i2_density')) :
            error_message = "line no. " + str(line_number) + " {error: i2_density = " + object.attrib.get('i2_density') +" kg/m3}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i3_viscosity')) :
            error_message = "line no. " + str(line_number) + " {error: i3_viscosity = " + object.attrib.get('i3_viscosity') +" cP}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i4_pipe_size_ID')) :
            error_message = "line no. " + str(line_number) + " {error: i4_pipe_size_ID = " + object.attrib.get('i4_pipe_size_ID') +" inch}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i5_roughness')) :
            error_message = "line no. " + str(line_number) + " {error: i5_roughness = " + object.attrib.get('i5_roughness') +" m}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i6_equivalent_length')) :
            error_message = "line no. " + str(line_number) + " {error: i6_equivalent_length = " + object.attrib.get('i6_equivalent_length') +" m}"
            input_error_message.append (error_message) 
        line_number +=1
        
    if 'i2_MW' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of vapor line
        if not is_convertible_to_number(object.attrib.get('i1_flowrate')) :
            error_message = "line no. " + str(line_number) + " {error: i1_flowrate = " + object.attrib.get('i1_flowrate') +" kg/hr}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i2_MW')) :
            error_message = "line no. " + str(line_number) + " {error: i2_MW = " + object.attrib.get('i2_MW') +" [-]}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i3_viscosity')) :
            error_message = "line no. " + str(line_number) + " {error: i3_viscosity = " + object.attrib.get('i3_viscosity') +" cP}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i4_temperature')) :
            error_message = "line no. " + str(line_number) + " {error: i4_temperature = " + object.attrib.get('i4_temperature') +" deg.C}"
            input_error_message.append (error_message)         
        if not is_convertible_to_number(object.attrib.get('i5_compressible_factor_z')) :
            error_message = "line no. " + str(line_number) + " {error: i5_compressible_factor_z = " + object.attrib.get('i5_compressible_factor_z') +" [-]}"
            input_error_message.append (error_message)  
        if not is_convertible_to_number(object.attrib.get('i6_specific_heat_Cp_Cv')) :
            error_message = "line no. " + str(line_number) + " {error: i6_specific_heat_Cp_Cv = " + object.attrib.get('i6_specific_heat_Cp_Cv') +" [-]}"
            input_error_message.append (error_message)  
        if not is_convertible_to_number(object.attrib.get('i7_pipe_size_ID')) :
            error_message = "line no. " + str(line_number) + " {error: i7_pipe_size_ID = " + object.attrib.get('i7_pipe_size_ID') +" inch}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i8_roughness')) :
            error_message = "line no. " + str(line_number) + " {error: i8_roughness = " + object.attrib.get('i8_roughness') +" m}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i9_equivalent_length')) :
            error_message = "line no. " + str(line_number) + " {error: i9_equivalent_length = " + object.attrib.get('i9_equivalent_length') +" m}"
            input_error_message.append (error_message) 
        line_number +=1      

    if 'i1_liquid_flowrate' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of 2 phase line
        if not is_convertible_to_number(object.attrib.get('i1_liquid_flowrate')) :
            error_message = "line no. " + str(line_number) + " {error: i1_liquid_flowrate = " + object.attrib.get('i1_liquid_flowrate') +" kg/hr}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i2_liquid_density')) :
            error_message = "line no. " + str(line_number) + " {error: i2_liquid_density = " + object.attrib.get('i2_liquid_density') +" kg/m3}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i3_vapor_flowrate')) :
            error_message = "line no. " + str(line_number) + " {error: i3_vapor_flowrate = " + object.attrib.get('i3_vapor_flowrate') +" kg/hr}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i4_vapor_density')) :
            error_message = "line no. " + str(line_number) + " {error: i4_vapor_density = " + object.attrib.get('i4_vapor_density') +" kg/m3}"
            input_error_message.append (error_message)            
        if not is_convertible_to_number(object.attrib.get('i5_pipe_size_ID')) :
            error_message = "line no. " + str(line_number) + " {error: i5_pipe_size_ID = " + object.attrib.get('i5_pipe_size_ID') +" inch}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i6_roughness')) :
            error_message = "line no. " + str(line_number) + " {error: i6_roughness = " + object.attrib.get('i6_roughness') +" m}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i7_equivalent_length')) :
            error_message = "line no. " + str(line_number) + " {error: i7_equivalent_length = " + object.attrib.get('i7_equivalent_length') +" m}"
            input_error_message.append (error_message) 
        line_number +=1
          
    if 'i1_operating_pressure' in object.attrib and 'i2_nozzle_elevation' in object.attrib:  # ckeck input of nozzle  
        if not is_convertible_to_number(object.attrib.get('i1_operating_pressure')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_operating_pressure = " + object.attrib.get('i1_operating_pressure') + f" {unit_g}"+"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i2_nozzle_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_nozzle_elevation = " + object.attrib.get('i2_nozzle_elevation') +" m}"
            input_error_message.append (error_message)         

    if 'i1_pressure_drop' in object.attrib and 'i2_elevation' in object.attrib:  # check input of delta_P Eq 
        if not is_convertible_to_number(object.attrib.get('i1_pressure_drop')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_pressure_drop = " + object.attrib.get('i1_pressure_drop') +f" {unit}"+"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i2_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_elevation = " + object.attrib.get('i2_elevation') +" m}"
            input_error_message.append (error_message)

    if 'i1_elevation' in object.attrib:  # check input of Junction 
        if not is_convertible_to_number(object.attrib.get('i1_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_elevation = " + object.attrib.get('i1_elevation') +" m}"
            input_error_message.append (error_message)

    if 'i1_differential_pressure' in object.attrib and 'i2_elevation' in object.attrib:  # check input of Fixed Control Valve or Manual Dummy valve
        if (not is_convertible_to_number(object.attrib.get('i1_differential_pressure'))) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_differential_pressure = " + object.attrib.get('i1_differential_pressure') +f" {unit}"+"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i2_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_elevation = " + object.attrib.get('i2_elevation') +" m}"
            input_error_message.append (error_message)
        
    if not('i1_differential_pressure' in object.attrib) and not('i1_pressure_drop' in object.attrib) and 'i2_elevation' in object.attrib:  # check input of Control Valve 
        if not is_convertible_to_number(object.attrib.get('i2_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_elevation = " + object.attrib.get('i2_elevation') +" m}"
            input_error_message.append (error_message)

        
    if 'i2_vapor_pressure' in object.attrib:  # check input of variable pump and fixed pump 
        if 'i1_differential_pressure' in object.attrib: # 없으면 variable로 알고 통과하고,  fixed pump 값 체크
            if (not is_convertible_to_number(object.attrib.get('i1_differential_pressure'))) :
                    error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_differential_pressure = " + object.attrib.get('i1_differential_pressure') +f" {unit}"+"}"
                    input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i2_vapor_pressure')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_vapor_pressure = " + object.attrib.get('i2_vapor_pressure') +f" {unit_A}"+"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i3_specific_gravity')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i3_specific_gravity = " + object.attrib.get('i3_specific_gravity') +" }"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i4_viscosity')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i4_viscosity = " + object.attrib.get('i4_viscosity') +" cP}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i5_suction_min_liquid_level_from_GL')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i5_suction_min_liquid_level_from_GL = " + object.attrib.get('i5_suction_min_liquid_level_from_GL') +" m}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i6_baseplate_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i6_baseplate_elevation = " + object.attrib.get('i6_baseplate_elevation') +" m}"
            input_error_message.append (error_message)

    return input_error_message

def check_input_value(root): # ✅ 사용자 입력값을 검토
    global line_number
    # """ 프로그램 실행 함수 """
    # root = load_xml(file_path)
    
    # if root is None:
    #     print("XML 파일을 로드하지 못했습니다. 프로그램을 종료합니다.")
    #     return

    # 'hydro' 시트에서 바로 'object'를 찾기
    calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    input_error_messages = []
 
    line_number = 1
    objects = calculation_sheet.findall('.//object')
    if len(objects) < 3 :
        print ("❓Please, draw more than current number ("+str(len(objects))+").")
        sys.exit(1)
    for object in calculation_sheet.findall('.//object'):
        input_error_message = validate_object_data(object)
        input_error_messages.extend(input_error_message)
 
    return input_error_messages

def get_tag_no_by_id(root, target_id):
    """ 특정 ID의 A_tag_no 값을 반환 (없으면 ID 유지) """
    global line_number
    for obj in root.findall(".//object"):
        if obj.get("id") == target_id:
            return obj.get("A_tag_no") or f"ID:{target_id}"  # A_tag_no 없으면 ID 그대로 반환
    return f"ID:{target_id}"  # ID가 없으면 그대로 반환

def find_routes_from_drawio(root):  # ✅ HYD에서 route를 찾아서 하나씩 만들어 route에 넣어둠
    # tree = ET.parse(file_path)  # XML 파일 파싱
    # root = tree.getroot()  # 최상위 요소 가져오기
    # root = load_xml(file_path)
    edges = {}  # (source, target) -> edge_id 저장
    nodes = set()  # 노드 (박스) 정보를 저장할 집합
    adjacency_list = defaultdict(list)  # 그래프 구조 저장

    # 'hydro' 시트에서 'object' 찾기
    calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
    if calculation_sheet is None:
        return []  # 해당 시트가 없으면 빈 리스트 반환
    line_ids = []
    for object in calculation_sheet.findall('.//object'):
        for line in object.findall('.//mxCell'):
            if 'edge' in line.attrib:
                edge_id = object.get('id')  # 연결선의 ID
                source = line.get('source')  # 시작 노드 ID
                target = line.get('target')  # 끝 노드 ID
                if source and target:
                    line_ids.append (edge_id) 
                    edges[(source, target)] = edge_id  # 간선 ID 저장
                    adjacency_list[source].append((target, edge_id))  # (노드, 연결선 ID) 저장
                    nodes.update([source, target])  # 노드 집합에 추가

    def dfs(node, path):
        """ 깊이 우선 탐색(DFS)으로 모든 경로 찾기 """
        path.append(node)  # 현재 노드를 경로에 추가
        if node not in adjacency_list or not adjacency_list[node]:  
            routes.append(path[:])  # 경로 저장
        else:
            for neighbor, edge_id in adjacency_list[node]:
                path.append(edge_id)  # 🔹 연결선 ID 추가
                dfs(neighbor, path[:])  # 재귀 호출 (경로 복사)
                path.pop()  # 백트래킹 (이전 상태 복원)

    # 모든 시작점을 찾고 DFS 실행
    routes = []  # 경로 저장 리스트
    start_nodes = nodes - set(target for _, target in edges.keys())  # 진입하는 선이 없는 노드 찾기
    for start in start_nodes:
        dfs(start, [])  # DFS 실행

    # ✅ ID → A_tag_no 변환 (노드와 연결선 ID 모두 변환)⚡  😊 💛 🌈 ⭐  ➡️
    final_routes = []
    for route in routes:
        tag_route = []
        for item in route:
            if item in line_ids :
                line_no = line_ids.index(item)+1 if item in line_ids else -1
                tag_route.append(get_tag_no_by_id(root, item) if item in nodes else f"[{line_no}]")  

            else:
                # temp = ()
                tag_route.append(get_tag_no_by_id(root, item) if item in nodes else f"[{item}]")  
        final_routes.append(tag_route)
        
    return final_routes, routes, line_ids  # 변환된 경로 반환

# def find_routes_from_drawio(root):
#     edges = {}
#     nodes = set()
#     adjacency_list = defaultdict(list)

#     calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
#     if calculation_sheet is None:
#         return [], [], []

#     # ✅ junction ID 모음
#     junction_nodes = {obj.get('id') for obj in calculation_sheet.findall('.//object') if obj.get('type') == 'junction'}

#     line_ids = []
#     for obj in calculation_sheet.findall('.//object'):
#         for line in obj.findall('.//mxCell'):
#             if 'edge' in line.attrib:
#                 edge_id = obj.get('id')
#                 source = line.get('source')
#                 target = line.get('target')
#                 if source and target:
#                     edges[(source, target)] = edge_id
#                     adjacency_list[source].append((target, edge_id))
#                     nodes.update([source, target])
#                     line_ids.append(edge_id)

#     # ✅ DFS + split condition
#     routes_id = []

#     def dfs(node, path):
#         path.append(node)

#         # split 조건: junction 또는 branch
#         if (node in junction_nodes or len(adjacency_list[node]) > 1) and len(path) > 1:
#             routes_id.append(path[:])
#             for neighbor, edge_id in adjacency_list[node]:
#                 dfs(neighbor, [node])
#         elif node not in adjacency_list:
#             routes_id.append(path[:])
#         else:
#             for neighbor, edge_id in adjacency_list[node]:
#                 path.append(edge_id)
#                 dfs(neighbor, path[:])
#                 path.pop()

#     start_nodes = nodes - set(target for _, target in edges.keys())
#     for start in start_nodes:
#         dfs(start, [])

#     # ✅ A_tag_no 변환
#     routes = []
#     for route in routes_id:
#         tag_route = []
#         for item in route:
#             if item in line_ids:
#                 line_no = line_ids.index(item) + 1
#                 tag_route.append(f"[Line:{line_no}]")
#             else:
#                 tag_route.append(get_tag_no_by_id(root, item))
#         routes.append(tag_route)

#     return routes, routes_id, line_ids

# def find_routes_from_drawio(root):
#     """
#     draw.io XML 구조에서 노드/엣지와 분기점(junction) 정보를 파싱하고,
#     경로를 DFS로 완전하게 추출하는 함수.
#     """

#     edges = {}
#     nodes = set()
#     adjacency_list = defaultdict(list)

#     # 1. 해당 다이어그램(페이지) 찾기
#     calculation_sheet = root.find(f".//diagram[@name='{config.current_page}']")
#     if calculation_sheet is None:
#         return [], [], []

#     # 2. junction ID 모음
#     junction_nodes = {obj.get('id') for obj in calculation_sheet.findall('.//object') if obj.get('type') == 'junction'}

#     # 3. 엣지/노드 정보 파싱
#     line_ids = []
#     for obj in calculation_sheet.findall('.//object'):
#         for line in obj.findall('.//mxCell'):
#             if 'edge' in line.attrib:
#                 edge_id = obj.get('id')
#                 source = line.get('source')
#                 target = line.get('target')
#                 if source and target:
#                     edges[(source, target)] = edge_id
#                     adjacency_list[source].append((target, edge_id))
#                     nodes.update([source, target])
#                     line_ids.append(edge_id)

#     routes_id = []

#     # 4. DFS: 분기점에서 path를 복제해서 모든 경로 완전 저장
#     def dfs(node, path):
#         path = path + [node]
#         if node not in adjacency_list:
#             # print("경로:", path)  # 경로 추적
#             routes_id.append(path)
#             return
#         for neighbor, edge_id in adjacency_list[node]:
#             # print(f"현재:{node} → 엣지:{edge_id} → 다음:{neighbor}")
#             dfs(neighbor, path + [edge_id])

#     # 5. 시작 노드: in-degree가 0인 노드만 (예: T-101)
#     all_targets = set(target for _, target in edges.keys())
#     start_nodes = nodes - all_targets
#     for start in start_nodes:
#         dfs(start, [])

#     # 6. A_tag_no 변환 (노드/엣지 → 태그/라인번호)
#     def get_tag_no_by_id(root, obj_id):
#         # 실제 구현에서는 XML에서 obj_id에 해당하는 태그/이름을 추출
#         # 아래는 예시(실제 구현 필요)
#         obj = root.find(f".//object[@id='{obj_id}']")
#         if obj is not None:
#             tag = obj.get('A_tag_no') or obj.get('value') or obj.get('label') or obj_id
#             return tag
#         return obj_id

#     routes = []
#     for route in routes_id:
#         tag_route = []
#         for item in route:
#             if item in line_ids:
#                 line_no = line_ids.index(item) + 1
#                 tag_route.append(f"[Line:{line_no}]")
#             else:
#                 tag_route.append(get_tag_no_by_id(root, item))
#         routes.append(tag_route)

#     return routes, routes_id, line_ids

# --- 사용 예시 (draw.io XML 파싱 및 config 객체 필요) ---

# from xml.etree import ElementTree as ET
# root = ET.parse('your_drawio_file.xml').getroot()
# class Config: current_page = 'P&ID'
# config = Config()
# routes, routes_id, line_ids = find_routes_from_drawio(root, config)
# for route in routes:
#     print(' → '.join(route))


def object_classification (root, routes_id, line_ids): # ✅ route안의 input data 이름을 계산에 편한 보편적 이름으로 바꾸고 문자를 숫자로 변경
    """ 특정 ID의 A_tag_no 값을 반환 (없으면 ID 유지) """
    """Type of Object
        - liquid_line / vapor_line / 2_phase_line
        - SorD / delta_P_EQ
        - manual_valve / control_valve
        - variable_pump / fixed_pump
    """

    cal_obj = {}
    cal_route = []
    cal_routes = []
    for route in routes_id :
        for target_id in route :
            for object in root.findall(".//object"):
                if object.get("id") == target_id:
                    # print(obj.get("A_tag_no") or f"ID:{target_id}")  # A_tag_no 없으면 ID 그대로 반환
                    if 'i1_flowrate' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of liquid line
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'liquid_line'
                        cal_obj ['A_tag_no'] = line_ids.index(target_id)+1
                        cal_obj ['flowrate'] = object.attrib.get('i1_flowrate')
                        cal_obj ['density'] = object.attrib.get('i2_density')
                        cal_obj ['viscosity'] = object.attrib.get('i3_viscosity')                        
                        cal_obj ['pipe_size_ID'] = object.attrib.get('i4_pipe_size_ID')                        
                        cal_obj ['roughness'] = object.attrib.get('i5_roughness')                        
                        cal_obj ['straight_length'] = object.attrib.get('i60_straight_length')  
                        cal_obj ['equivalent_length'] = object.attrib.get('i6_equivalent_length')  

                    if 'i2_MW' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of vapor line
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'vapor_line'
                        cal_obj ['A_tag_no'] = line_ids.index(target_id)+1
                        cal_obj ['flowrate'] = object.attrib.get('i1_flowrate')
                        cal_obj ['mw'] = object.attrib.get('i2_MW')
                        cal_obj ['viscosity'] = object.attrib.get('i3_viscosity')    
                        cal_obj ['temperature'] = float(object.attrib.get('i4_temperature'))
                        cal_obj ['z'] = object.attrib.get('i5_compressible_factor_z')                                                
                        cal_obj ['CpCv'] = object.attrib.get('i6_specific_heat_Cp_Cv')   
                        cal_obj ['pipe_size_ID'] = object.attrib.get('i7_pipe_size_ID')                        
                        cal_obj ['roughness'] = object.attrib.get('i8_roughness')                        
                        cal_obj ['straight_length'] = object.attrib.get('i90_straight_length')
                        cal_obj ['equivalent_length'] = object.attrib.get('i9_equivalent_length')                        
                        
                    if 'i1_liquid_flowrate' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of line
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'two_phase_line'
                        cal_obj ['A_tag_no'] = line_ids.index(target_id)+1
                        cal_obj ['liquid_flowrate'] = object.attrib.get('i1_liquid_flowrate')
                        cal_obj ['liquid_density'] = object.attrib.get('i2_liquid_density')
                        cal_obj ['vapor_flowrate'] = object.attrib.get('i3_vapor_flowrate')
                        cal_obj ['vapor_density'] = object.attrib.get('i4_vapor_density')                        
                        cal_obj ['viscosity'] = 0.1 # object.attrib.get('i3_viscosity')  # 2 phase line은 viscosity를 계산하지 않음   
                        cal_obj ['pipe_size_ID'] = object.attrib.get('i5_pipe_size_ID')                        
                        cal_obj ['roughness'] = object.attrib.get('i6_roughness')
                        cal_obj ['straight_length'] = object.attrib.get('i70_straight_length')                        
                        cal_obj ['equivalent_length'] = object.attrib.get('i7_equivalent_length')
                                                 
                    if 'i1_operating_pressure' in object.attrib and 'i2_nozzle_elevation' in object.attrib:  # ckeck input of nozzle  
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'SorD'
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        cal_obj ['operating_pressure'] = float(object.attrib.get('i1_operating_pressure'))
                        cal_obj ['elevation'] = float(object.attrib.get('i2_nozzle_elevation'))

                    if 'i1_elevation' in object.attrib:  # check input of Junction 
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'delta_P_all'
                        cal_obj ['A_tag_no'] = 'junction'
                        cal_obj ['elevation'] = float(object.attrib.get('i1_elevation'))
                        cal_obj ['pressure_drop'] = float(0)
                        
                    if 'i1_pressure_drop' in object.attrib and 'i2_elevation' in object.attrib:  # check input of delta_P Eq / Inst 
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'delta_P_all'                        
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        cal_obj ['pressure_drop'] = float(object.attrib.get('i1_pressure_drop'))
                        cal_obj ['elevation'] = float(object.attrib.get('i2_elevation'))

                    if 'i1_differential_pressure' in object.attrib and 'i2_elevation' in object.attrib:  # check input of Fixed Control Valve / HV or dummy valve
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'fixed_control_valve'
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        cal_obj ['pressure_drop'] = float(object.attrib.get('i1_differential_pressure')) ###
                        cal_obj ['elevation'] = float(object.attrib.get('i2_elevation'))

                    if 'i2_elevation' in object.attrib and 'o1_differential_pressure' in object.attrib:  # check input of Control Valve
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'control_valve'
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        ##cal_obj ['differential_pressure'] = 'NULL' ## control valve는 'NULL'로 입력함.
                        cal_obj ['elevation'] = float(object.attrib.get('i2_elevation'))

                    if 'i2_vapor_pressure' in object.attrib:  # check input of pump 
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'fixed_pump'
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        if 'i1_differential_pressure' in object.attrib :
                            cal_obj ['type'] = 'fixed_pump'
                            cal_obj ['differential_pressure'] = float(object.attrib.get('i1_differential_pressure')) ###
                        else :
                            cal_obj ['type'] = 'variable_pump'
                            ##cal_obj ['differential_pressure'] = 'NULL' ## variable pump는 'NULL'로 입력함.
                        cal_obj ['vapor_pressure'] = object.attrib.get('i2_vapor_pressure')
                        cal_obj ['specific_gravity'] = object.attrib.get('i3_specific_gravity')                        
                        cal_obj ['viscosity'] = object.attrib.get('i4_viscosity')
                        cal_obj ['suction_min_liquid_level_from_GL'] = float(object.attrib.get('i5_suction_min_liquid_level_from_GL'))                        
                        cal_obj ['elevation'] = float(object.attrib.get('i6_baseplate_elevation'))                     
                    # if  vapor_line, 2_phase_line, 더 만들것
            cal_route.append (cal_obj)
            cal_obj={}
        # print(cal_route , "\n\n")    
        cal_routes.append (cal_route)
        cal_route = []
    
    recal_obj = {}
    grouped_route = []
    grouped_routes = []

    for route in cal_routes : # 문자에서 계산 가능한 숫자로 모두 전환   
        for item in route:
            converted_data = {key: float(value) if isinstance(value, str) and value.replace('.', '', 1).isdigit() else value for key, value in item.items()}
            grouped_route.append (converted_data)
            converted_data = {}
        grouped_routes.append (grouped_route)
        grouped_route= []
    return grouped_routes

def group_routes_by_overlap(routes): # ✅ 같은 Header에 묶인것들로 grouping
    """ 
    중첩된 object가 있는 routes들을 같은 그룹으로 묶고,
    하나도 겹치지 않으면 새로운 그룹을 생성하는 함수.
    """
    # print(routes)
    groups = []  # 그룹을 저장할 리스트

    for route in routes:
        matched_groups = []  # 현재 route와 겹치는 그룹들을 저장

        for group in groups:
            # 기존 그룹에 속한 route들과 비교하여 첫 번째 객체가 같은지 확인
            if any((route[0] == existing_route[0]) for existing_route in group):
                matched_groups.append(group)

        if matched_groups:
            # 여러 그룹이 겹칠 경우 하나로 합침
            merged_group = []
            for matched_group in matched_groups:
                groups.remove(matched_group)  # 기존 그룹 제거
                merged_group.extend(matched_group)
            merged_group.append(route)
            groups.append(merged_group)
        else:
            # 겹치는 그룹이 없으면 새로운 그룹 생성
            groups.append([route])

    return groups

def verify_routes(routes):
    """
    주어진 routes 리스트 안의 각 route가
    첫 번째와 마지막 객체의 type이 'SorD'인지 확인한다.
    조건이 맞지 않으면 연결 오류 메시지를 출력한다.
    """
    # print (routes)
    for idx, route in enumerate(routes, start=1):
        if not route:
            print(f"[Route {idx}] 경로에 아무 객체가 없습니다.")
            continue
        
        first = route[0]
        last = route[-1]

        if first.get('type') != 'SorD':
            print(f"[Route {idx}] Disconnected.: A_tag_no={first.get('A_tag_no')}")
            sys.exit(1)
        if last.get('type') != 'SorD':
            print(f"[Route {idx}] Disconnected.: A_tag_no={last.get('A_tag_no')}")
            sys.exit(1)
