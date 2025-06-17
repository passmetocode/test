import xml.etree.ElementTree as ET
from collections import defaultdict
from xml.dom import minidom  # for pretty print
import config

line_number = 1

 # ✅ nozzle에 A_tag_no 부여
def update_Nozzle_A_tag_no_from_Equipment(root):
    # 1. i1_operating_pressure가 있는 object들을 대상으로
    for obj in root.findall(f".//diagram[@name='{config.current_page}']//object[@i1_operating_pressure]"):
        mx_cell = obj.find("mxCell")
        if mx_cell is None:
            continue
        parent_id = mx_cell.get("parent") 
        if not parent_id:
            continue

        # 2. 같은 시트 안의 mxCell 중에서 동일한 parent를 가진 것 찾기
        target_mxcell = root.find(f".//diagram[@name='{config.current_page}']//mxCell[@parent='{parent_id}']")
        if target_mxcell is not None:
            value = target_mxcell.get("value")

            # ✅ value가 없거나 빈 문자열이면 "none" 처리
            tag_value = value.strip() if value else "none"
            if tag_value == "":
                tag_value = "none"

            # ✅ A_tag_no가 비어 있거나 기존 값을 덮어쓰도록 강제 설정
            tag_value = tag_value + ':Noz'
            obj.set("A_tag_no", tag_value)
            # print (tag_value)
            
    return

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
    error_message=""
    input_error_message = []    
    if 'i1_flowrate' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of liquid line
        if not is_convertible_to_number(object.attrib.get('i1_flowrate')) :
            error_message = "line no. " + str(line_number) + " {error: i1_flowrate = " + object.attrib.get('i1_flowrate') +" m3/hr}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i2_density')) :
            error_message = "line no. " + str(line_number) + " {error: i2_density = " + object.attrib.get('i2_density') +" kg/m3}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i3_viscosity')) :
            error_message = "line no. " + str(line_number) + " {error: i3_viscosity = " + object.attrib.get('i3_viscosity') +" cP}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i4_pipe_size_ID')) :
            error_message = "line no. " + str(line_number) + " {error: i4_pipe_size_ID = " + object.attrib.get('i4_pipe_size_ID') +" inch}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i5_roughness')) :
            error_message = "line no. " + str(line_number) + " {error: i5_roughness = " + object.attrib.get('i5_roughness') +" ft}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i6_equivalent_length')) :
            error_message = "line no. " + str(line_number) + " {error: i6_equivalent_length = " + object.attrib.get('i6_equivalent_length') +" m}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        line_number +=1
        
    if 'i2_MW' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of vapor line
        if not is_convertible_to_number(object.attrib.get('i1_flowrate')) :
            error_message = "line no. " + str(line_number) + " {error: i1_flowrate = " + object.attrib.get('i1_flowrate') +" kg/hr}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i2_MW')) :
            error_message = "line no. " + str(line_number) + " {error: i2_MW = " + object.attrib.get('i2_MW') +" [-]}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i3_viscosity')) :
            error_message = "line no. " + str(line_number) + " {error: i3_viscosity = " + object.attrib.get('i3_viscosity') +" cP}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i4_temperature')) :
            error_message = "line no. " + str(line_number) + " {error: i4_temperature = " + object.attrib.get('i4_temperature') +" deg.C}  ID : {" + object_id +"}"
            input_error_message.append (error_message)         
        if not is_convertible_to_number(object.attrib.get('i5_compressible_factor_z')) :
            error_message = "line no. " + str(line_number) + " {error: i5_compressible_factor_z = " + object.attrib.get('i5_compressible_factor_z') +" [-]}  ID : {" + object_id +"}"
            input_error_message.append (error_message)  
        if not is_convertible_to_number(object.attrib.get('i6_specific_heat_Cp_Cv')) :
            error_message = "line no. " + str(line_number) + " {error: i6_specific_heat_Cp_Cv = " + object.attrib.get('i6_specific_heat_Cp_Cv') +" [-]}  ID : {" + object_id +"}"
            input_error_message.append (error_message)  
        if not is_convertible_to_number(object.attrib.get('i7_pipe_size_ID')) :
            error_message = "line no. " + str(line_number) + " {error: i7_pipe_size_ID = " + object.attrib.get('i7_pipe_size_ID') +" inch}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i8_roughness')) :
            error_message = "line no. " + str(line_number) + " {error: i8_roughness = " + object.attrib.get('i8_roughness') +" ft}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i9_equivalent_length')) :
            error_message = "line no. " + str(line_number) + " {error: i9_equivalent_length = " + object.attrib.get('i9_equivalent_length') +" m}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        line_number +=1      

    if 'i1_liquid_flowrate' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of 2 phase line
        if not is_convertible_to_number(object.attrib.get('i1_liquid_flowrate')) :
            error_message = "line no. " + str(line_number) + " {error: i1_liquid_flowrate = " + object.attrib.get('i1_liquid_flowrate') +" kg/hr}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i2_liquid_density')) :
            error_message = "line no. " + str(line_number) + " {error: i2_liquid_density = " + object.attrib.get('i2_liquid_density') +" kg/m3}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i3_vapor_flowrate')) :
            error_message = "line no. " + str(line_number) + " {error: i3_vapor_flowrate = " + object.attrib.get('i3_vapor_flowrate') +" kg/hr}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i4_vapor_density')) :
            error_message = "line no. " + str(line_number) + " {error: i4_vapor_density = " + object.attrib.get('i4_vapor_density') +" kg/m3}  ID : {" + object_id +"}"
            input_error_message.append (error_message)            
        if not is_convertible_to_number(object.attrib.get('i5_pipe_size_ID')) :
            error_message = "line no. " + str(line_number) + " {error: i5_pipe_size_ID = " + object.attrib.get('i5_pipe_size_ID') +" inch}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i5_roughness')) :
            error_message = "line no. " + str(line_number) + " {error: i6_roughness = " + object.attrib.get('i6_roughness') +" ft}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        if not is_convertible_to_number(object.attrib.get('i6_equivalent_length')) :
            error_message = "line no. " + str(line_number) + " {error: i7_equivalent_length = " + object.attrib.get('i7_equivalent_length') +" m}  ID : {" + object_id +"}"
            input_error_message.append (error_message) 
        line_number +=1
          
    if 'i1_operating_pressure' in object.attrib and 'i2_nozzle_elevation' in object.attrib:  # ckeck input of nozzle  
        if not is_convertible_to_number(object.attrib.get('i1_operating_pressure')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_operating_pressure = " + object.attrib.get('i1_operating_pressure') +" kg/cm2.g}  ID : {" + object_id +"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i2_nozzle_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_nozzle_elevation = " + object.attrib.get('i2_nozzle_elevation') +" m}  ID : {" + object_id +"}"
            input_error_message.append (error_message)         

    if 'i1_pressure_drop' in object.attrib and 'i2_elevation' in object.attrib:  # check input of delta_P Eq 
        if not is_convertible_to_number(object.attrib.get('i1_pressure_drop')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_pressure_drop = " + object.attrib.get('i1_pressure_drop') +" kg/cm2}  ID : {" + object_id +"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i2_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_elevation = " + object.attrib.get('i2_elevation') +" m}  ID : {" + object_id +"}"
            input_error_message.append (error_message)

    if 'i1_elevation' in object.attrib:  # check input of Junction 
        if not is_convertible_to_number(object.attrib.get('i1_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_elevation = " + object.attrib.get('i1_elevation') +" m}  ID : {" + object_id +"}"
            input_error_message.append (error_message)

    if 'i1_differential_pressure' in object.attrib and 'i2_elevation' in object.attrib:  # check input of Fixed Control Valve or Manual Dummy valve
        if (not is_convertible_to_number(object.attrib.get('i1_differential_pressure'))) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_differential_pressure = " + object.attrib.get('i1_differential_pressure') +" kg/cm2}  ID : {" + object_id +"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i2_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_elevation = " + object.attrib.get('i2_elevation') +" m}  ID : {" + object_id +"}"
            input_error_message.append (error_message)
        
    if not('i1_differential_pressure' in object.attrib) and not('i1_pressure_drop' in object.attrib) and 'i2_elevation' in object.attrib:  # check input of Control Valve 
        if not is_convertible_to_number(object.attrib.get('i2_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_elevation = " + object.attrib.get('i2_elevation') +" m}  ID : {" + object_id +"}"
            input_error_message.append (error_message)

        
    if 'i2_vapor_pressure' in object.attrib:  # check input of variable pump and fixed pump 
        if 'i1_differential_pressure' in object.attrib: # 없으면 variable로 알고 통과하고,  fixed pump 값 체크
            if (not is_convertible_to_number(object.attrib.get('i1_differential_pressure'))) :
                    error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i1_differential_pressure = " + object.attrib.get('i1_differential_pressure') +" kg/cm2}  ID : {" + object_id +"}"
                    input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i2_vapor_pressure')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i2_vapor_pressure = " + object.attrib.get('i2_vapor_pressure') +" kg/cm2.A}  ID : {" + object_id +"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i3_specific_gravity')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i3_specific_gravity = " + object.attrib.get('i3_specific_gravity') +" }  ID : {" + object_id +"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i4_viscosity')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i4_viscosity = " + object.attrib.get('i4_viscosity') +" cP}  ID : {" + object_id +"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i5_suction_min_liquid_level_from_GL')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i5_suction_min_liquid_level_from_GL = " + object.attrib.get('i5_suction_min_liquid_level_from_GL') +" m}  ID : {" + object_id +"}"
            input_error_message.append (error_message)
        if not is_convertible_to_number(object.attrib.get('i6_baseplate_elevation')) :
            error_message = "tag no. : " + object.attrib.get('A_tag_no') + " {error: i6_baseplate_elevation = " + object.attrib.get('i6_baseplate_elevation') +" m}  ID : {" + object_id +"}"
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
                        cal_obj ['equivalent_length'] = object.attrib.get('i6_equivalent_length')  
                                              
                    if 'i2_MW' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of vapor line
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'vapor_line'
                        cal_obj ['A_tag_no'] = line_ids.index(target_id)+1
                        cal_obj ['flowrate'] = object.attrib.get('i1_flowrate')
                        cal_obj ['mw'] = object.attrib.get('i2_MW')
                        cal_obj ['viscosity'] = object.attrib.get('i3_viscosity')    
                        cal_obj ['temperature'] = object.attrib.get('i4_temperature') 
                        cal_obj ['z'] = object.attrib.get('i5_compressible_factor_z')                                                
                        cal_obj ['CpCv'] = object.attrib.get('i6_specific_heat_Cp_Cv')   
                        cal_obj ['pipe_size_ID'] = object.attrib.get('i7_pipe_size_ID')                        
                        cal_obj ['roughness'] = object.attrib.get('i8_roughness')                        
                        cal_obj ['equivalent_length'] = object.attrib.get('i9_equivalent_length')
                        
                    if 'i1_liquid_flowrate' in object.attrib:  #object.find('.//mxCell[@edge="1"]'): # check input of line
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'two_phase_line'
                        cal_obj ['A_tag_no'] = line_ids.index(target_id)+1
                        cal_obj ['liquid_flowrate'] = object.attrib.get('i1_liquid_flowrate')
                        cal_obj ['liquid_density'] = object.attrib.get('i2_liquid_density')
                        cal_obj ['vapor_flowrate'] = object.attrib.get('i3_vapor_flowrate')
                        cal_obj ['vapor_density'] = object.attrib.get('i4_vapor_density')                        
                        cal_obj ['pipe_size_ID'] = object.attrib.get('i5_pipe_size_ID')                        
                        cal_obj ['roughness'] = object.attrib.get('i6_roughness')                        
                        cal_obj ['equivalent_length'] = object.attrib.get('i7_equivalent_length')
                                                 
                    if 'i1_operating_pressure' in object.attrib and 'i2_nozzle_elevation' in object.attrib:  # ckeck input of nozzle  
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'SorD'
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        cal_obj ['operating_pressure'] = object.attrib.get('i1_operating_pressure')
                        cal_obj ['elevation'] = object.attrib.get('i2_nozzle_elevation')

                    if 'i1_elevation' in object.attrib:  # check input of Junction 
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'delta_P_all'
                        cal_obj ['A_tag_no'] = 'junction'
                        cal_obj ['elevation'] = object.attrib.get('i1_elevation')
                        cal_obj ['pressure_drop'] = float(0)
                        
                    if 'i1_pressure_drop' in object.attrib and 'i2_elevation' in object.attrib:  # check input of delta_P Eq / Inst 
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'delta_P_all'                        
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        cal_obj ['pressure_drop'] = object.attrib.get('i1_pressure_drop')
                        cal_obj ['elevation'] = object.attrib.get('i2_elevation')

                    if 'i1_differential_pressure' in object.attrib and 'i2_elevation' in object.attrib:  # check input of Fixed Control Valve / HV or dummy valve
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'fixed_control_valve'
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        cal_obj ['pressure_drop'] = object.attrib.get('i1_differential_pressure') ###
                        cal_obj ['elevation'] = object.attrib.get('i2_elevation')

                    if not('i1_differential_pressure' in object.attrib) and not('i1_pressure_drop' in object.attrib) and 'i2_elevation' in object.attrib:  # check input of Control Valve
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'control_valve'
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        ##cal_obj ['differential_pressure'] = 'NULL' ## control valve는 'NULL'로 입력함.
                        cal_obj ['elevation'] = object.attrib.get('i2_elevation')

                    if 'i2_vapor_pressure' in object.attrib:  # check input of pump 
                        cal_obj ['ID'] = object.get("id")
                        cal_obj ['type'] = 'fixed_pump'
                        cal_obj ['A_tag_no'] = object.attrib.get('A_tag_no')
                        if 'i1_differential_pressure' in object.attrib :
                            cal_obj ['type'] = 'fixed_pump'
                            cal_obj ['differential_pressure'] = object.attrib.get('i1_differential_pressure') ###
                        else :
                            cal_obj ['type'] = 'variable_pump'
                            ##cal_obj ['differential_pressure'] = 'NULL' ## variable pump는 'NULL'로 입력함.
                        cal_obj ['vapor_pressure'] = object.attrib.get('i2_vapor_pressure')
                        cal_obj ['specific_gravity'] = object.attrib.get('i3_specific_gravity')                        
                        cal_obj ['viscosity'] = object.attrib.get('i4_viscosity')
                        cal_obj ['suction_min_liquid_level_from_GL'] = object.attrib.get('i5_suction_min_liquid_level_from_GL')                        
                        cal_obj ['elevation'] = object.attrib.get('i6_baseplate_elevation')                       
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

