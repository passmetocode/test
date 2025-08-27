import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from xml.dom import minidom  # for pretty print
import config

line_number = 1

def update_Nozzle_A_tag_no_from_Equipment(root, page_name):
    """
    diagram[@name=page_name] 하위 object 중 i1_operating_pressure가 있는 노즐에
    같은 parent 내 object.label, object/mxCell.value 등에서 라벨을 추출해
    <label>:Noz 형식으로 A_tag_no 세팅

    - 라벨 우선순위: 
        1) i1_operating_pressure 없는 object의 label 
        2) i1_operating_pressure 없는 object의 mxCell.value
        3) 같은 parent를 가진 다른 mxCell의 value
        4) "none"

    ※ Page까지 올라가는 최상위 그룹은 제외하고, 처음 그룹까지만 고려
    """
    parent2obj = defaultdict(list)

    # object들을 parent id 기준으로 그룹핑
    for obj in root.findall(f".//diagram[@name='{page_name}']//object"):
        mxcell = obj.find("mxCell")
        if mxcell is None:
            continue
        parent_id = mxcell.get("parent")

        # Page 바로 아래 그룹까지만 포함
        if parent_id and parent_id != page_name:  # parent_id가 Page 이름이면 제외
            parent2obj[parent_id].append((obj, mxcell))

    for parent_id, objlist in parent2obj.items():
        label = ""
        # 1) i1_operating_pressure 없는 object의 label 우선
        for obj, mxcell in objlist:
            if not obj.get("i1_operating_pressure") :
                if obj.get("label") and obj.get("label").strip():
                    if not obj.get("i1_elevation") and not obj.get("i2_elevation") and not obj.get("A_tag_no"):
                        label = obj.get("label").strip()
                        # print(f"Found label from object: {label}")
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
            if obj.get("i1_operating_pressure") and obj.get("A_tag_no"):
                obj.set("A_tag_no", tag_value)  # 원래 하려는 의도              
            if obj.get("i1_operating_pressure") and not obj.get("A_tag_no"):            
                pass # 원치 않는경우인데, 전부 통과시킴.. Nozzle과 같은 역활을 하는데, A_tag_no가 없는 경우의 Nozzle을 만듬.
                # if obj.get("A_tag_no") == tag_value: 
                #     obj.set("A_tag_no", tag_value)
                # else:    
                #     obj.set("A_tag_no", obj.get("A_tag_no")) 

    # 그룹이 없는 object 선별



def load_xml(file_path):
    """ XML 파일을 로드하고 루트를 반환하는 함수 """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except Exception as e:
        print(f"XML 파일을 로드하는 중 오류 발생: {e}")
        return None

def is_convertible_to_number(input_value, allow_negative=True):
    if input_value is None:
        return False
    try:
        num = float(input_value)
        if not allow_negative and num < 0:
            return False
        return True
    except (ValueError, TypeError):
        return False


def validate_object_data(object):
    global line_number
    object_id = object.get('id')
    # 압력 단위 설정
    unit = 'bar' if config.pressure_selection == 'bar' else 'kg/cm2' if config.pressure_selection == 'kg/cm2' else 'MPa'
    unit_g = f'{unit}.g'
    unit_A = f'{unit}.A'
    error_message=""
    input_error_message = []    
    # Liquid line input check
    if 'i2_density' in object.attrib:
        fields = [
            ('i1_flowrate', 'm3/hr', False),
            ('i2_density', 'kg/m3', False),
            ('i3_viscosity', 'cP', False),
            ('i4_pipe_size_ID', 'inch', False),
            ('i5_roughness', 'm', False),
            ('i6_equivalent_length', 'm', False),
        ]
        for key, unit_str, allow_neg in fields:
            if not is_convertible_to_number(object.attrib.get(key), allow_negative=allow_neg):
                error_message = f"line no. {line_number} {{error: {key} = {object.attrib.get(key)} {unit_str}}}"
                input_error_message.append(error_message)
        line_number +=1
        
    # Vapor line input check
    if 'i2_MW' in object.attrib:
        fields = [
            ('i1_flowrate', 'kg/hr', False),
            ('i2_MW', '[-]', False),
            ('i3_viscosity', 'cP', False),
            ('i4_temperature', 'deg.C', True),  # 음수 허용
            ('i5_compressible_factor_z', '[-]', False),
            ('i6_specific_heat_Cp_Cv', '[-]', False),
            ('i7_pipe_size_ID', 'inch', False),
            ('i8_roughness', 'm', False),
            ('i9_equivalent_length', 'm', False),
        ]

        for key, unit_str, allow_neg in fields:
            value = object.attrib.get(key)
            if not is_convertible_to_number(value, allow_negative=allow_neg):
                error_message = f"line no. {line_number} {{error: {key} = {value} {unit_str}}}"
                input_error_message.append(error_message)
            else:
                # ★ 추가 조건: i4_temperature 절대 영도 이하 제한
                if key == 'i4_temperature':
                    numeric_value = float(value)
                    if numeric_value < -273.13:
                        error_message = (
                            f"line no. {line_number} "
                            f"{{error: {key} = {numeric_value} {unit_str} (Absolute zero limit)}}"
                        )
                        input_error_message.append(error_message)
        line_number += 1


    # 2-phase line input check
    if 'i1_liquid_flowrate' in object.attrib:
        fields = [
            ('i1_liquid_flowrate', 'kg/hr', False),
            ('i2_liquid_density', 'kg/m3', False),
            ('i3_vapor_flowrate', 'kg/hr', False),
            ('i4_vapor_density', 'kg/m3', False),
            ('i5_pipe_size_ID', 'inch', False),
            ('i6_roughness', 'm', False),
            ('i7_equivalent_length', 'm', False),
        ]

        for key, unit_str, allow_neg in fields:
            if not is_convertible_to_number(object.attrib.get(key), allow_negative=allow_neg):
                error_message = f"line no. {line_number} {{error: {key} = {object.attrib.get(key)} {unit_str}}}"
                input_error_message.append(error_message)
        line_number +=1
        
    # User Line ; Static loss & Pipe loss input check
    if 'i2_static_loss' in object.attrib:
        fields = [
            ('i1_pipe_size_ID', 'inch', False),  # 파이프 크기  
            ('i2_static_loss', unit, True),
            ('i3_pipe_loss', unit, True),
        ]

        for key, unit_str, allow_neg in fields:
            if not is_convertible_to_number(object.attrib.get(key), allow_negative=allow_neg):
                error_message = f"line no. {line_number} {{error: {key} = {object.attrib.get(key)} {unit_str}}}"
                input_error_message.append(error_message)
        line_number +=1
                  
    # Nozzle input check
    if 'i1_operating_pressure' in object.attrib and 'i2_nozzle_elevation' in object.attrib:
        fields = [
            ('i1_operating_pressure', unit_g, True),  # 압력 단위 (unit_g 사용)
            ('i2_nozzle_elevation', 'm', True),       # 높이(m)
        ]

        for key, unit_str, allow_neg in fields:
            value = object.attrib.get(key)

            # 숫자 변환 가능 여부 체크
            if not is_convertible_to_number(value, allow_negative=allow_neg):
                error_message = (
                    f"tag no. : {object.attrib.get('A_tag_no')} "
                    f"{{error: {key} = {value} {unit_str}}}"
                )
                input_error_message.append(error_message)
            else:
                # ★ 추가 조건: i1_operating_pressure 절대압 0 이하 금지
                if key == 'i1_operating_pressure':
                    numeric_value = float(value)

                    # 게이지 단위를 절대압으로 변환
                    if unit == 'bar':
                        abs_pressure = numeric_value + 1.013  # bar.g → bar.a
                    elif unit == 'MPa':
                        abs_pressure = numeric_value + 0.10133  # MPa.g → MPa.a    
                    else:  # kg/cm2
                        abs_pressure = numeric_value + 1.033  # kg/cm2.g → kg/cm2.a

                    if abs_pressure <= 0:
                        error_message = (
                            f"tag no. : {object.attrib.get('A_tag_no')} "
                            f"{{error: {key} Absolute Pressure {abs_pressure:.3f} {unit}.A must be > 0}}"
                        )
                        input_error_message.append(error_message)

    # delta_P Eq input check
    if 'i1_pressure_drop' in object.attrib and 'i2_elevation' in object.attrib:
        fields = [
            ('i1_pressure_drop', unit, True),  # 압력단위 (예: bar, kg/cm2)
            ('i2_elevation', 'm', True),       # 높이(m)
        ]

        for key, unit_str, allow_neg in fields:
            value = object.attrib.get(key)
            if not is_convertible_to_number(str(value).strip(), allow_negative=allow_neg):
                error_message = (
                    f"tag no. : {object.attrib.get('A_tag_no')} "
                    f"{{error: {key} = {value} {unit_str}}}"
                )
                input_error_message.append(error_message)


    # Junction input check
    if 'i1_elevation' in object.attrib:
        fields = [
            ('i1_elevation', 'm', True),  # 높이(m)
        ]

        for key, unit_str, allow_neg in fields:
            value = object.attrib.get(key)
            if not is_convertible_to_number(str(value).strip(), allow_negative=allow_neg):
                error_message = (
                    f"tag no. : {object.attrib.get('A_tag_no')} "
                    f"{{error: {key} = {value} {unit_str}}}"
                )
                input_error_message.append(error_message)


    # Fixed Control Valve or Manual Dummy Valve input check
    if 'i1_differential_pressure' in object.attrib and 'i2_elevation' in object.attrib:
        fields = [
            ('i1_differential_pressure', unit, True),  # 압력 단위
            ('i2_elevation', 'm', True),               # 높이(m)
        ]

        for key, unit_str, allow_neg in fields:
            value = object.attrib.get(key)
            if not is_convertible_to_number(str(value).strip(), allow_negative=allow_neg):
                error_message = (
                    f"tag no. : {object.attrib.get('A_tag_no')} "
                    f"{{error: {key} = {value} {unit_str}}}"
                )
                input_error_message.append(error_message)


    # Control Valve input check (without diff_pressure / pressure_drop, only elevation)
    if not ('i1_differential_pressure' in object.attrib) and not ('i1_pressure_drop' in object.attrib) \
    and 'i2_elevation' in object.attrib:
        fields = [
            ('i2_elevation', 'm', True),  # 높이(m)
        ]

        for key, unit_str, allow_neg in fields:
            value = object.attrib.get(key)
            if not is_convertible_to_number(str(value).strip(), allow_negative=allow_neg):
                error_message = (
                    f"tag no. : {object.attrib.get('A_tag_no')} "
                    f"{{error: {key} = {value} {unit_str}}}"
                )
                input_error_message.append(error_message)
        
    # Variable Pump / Fixed Pump input check
    if 'i2_vapor_pressure' in object.attrib:

        # i1_differential_pressure는 없을 수도 있으므로 조건부 추가
        if 'i1_differential_pressure' in object.attrib:
            dp_fields = [
                ('i1_differential_pressure', unit, True),  # 음수 허용
            ]
            for key, unit_str, allow_neg in dp_fields:
                value = object.attrib.get(key)
                if not is_convertible_to_number(str(value).strip(), allow_negative=allow_neg):
                    error_message = (
                        f"tag no. : {object.attrib.get('A_tag_no')} "
                        f"{{error: {key} = {value} {unit_str}}}"
                    )
                    input_error_message.append(error_message)

        # 나머지 필드들
        fields = [
            ('i2_vapor_pressure', unit_A, False),                   # 음수 불가
            ('i3_specific_gravity', '', False),                      # 음수 불가
            ('i4_viscosity', 'cP', False),                           # 음수 불가
            ('i5_suction_min_liquid_level_from_GL', 'm', True),       # 음수 허용
            ('i6_baseplate_elevation', 'm', True),                   # 음수 허용
        ]

        for key, unit_str, allow_neg in fields:
            value = object.attrib.get(key)
            if not is_convertible_to_number(str(value).strip(), allow_negative=allow_neg):
                error_message = (
                    f"tag no. : {object.attrib.get('A_tag_no')} "
                    f"{{error: {key} = {value} {unit_str}}}"
                )
                input_error_message.append(error_message)


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
                line_ids.append (edge_id)                 
                if source and target:
                    # line_ids.append (edge_id) 
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
        # print(final_routes)  # 경로 출력
    return final_routes, routes, line_ids  # 변환된 경로 반환

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
                        
                    if 'i1_liquid_flowrate' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of 2 phase line
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

                    if 'i2_static_loss' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of user line
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'user_line'
                        cal_obj ['A_tag_no'] = line_ids.index(target_id)+1
                        cal_obj ['pipe_size_ID'] = object.attrib.get('i1_pipe_size_ID')                          
                        cal_obj ['static_pressure'] = object.attrib.get('i2_static_loss')
                        cal_obj ['pressure_drop'] = object.attrib.get('i3_pipe_loss')
                                                 
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
