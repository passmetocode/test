from collections import defaultdict
import hydro.module_calculation as module_calculation, config

def calculate_each_route_object_reverse (routes) : # 역방향 ✅ 각각의 route를 계산하고 object에 output값 부여
    for route in routes :
        for i in range (len(route)-1, -1, -1) :  # 역방향
            # i = len(route) - 1 - index # index 뒤집기
            if route[i]['type'] == "liquid_line" : 
                flowrate = route[i]['flowrate']
                density = route[i]['density']
                viscosity = route[i]['viscosity']
                pipe_size_ID = route[i]['pipe_size_ID']                
                roughness = route[i]['roughness']
                equivalent_length = route[i]['equivalent_length']                  

                # pressure_loss_kg_cm2, velocity, reynolds_number
                route[i]['pressure_drop'], route[i]['velocity'], route[i]['reynolds'] = (
                module_calculation.liquid_pressure_loss(flowrate, density, viscosity, pipe_size_ID, roughness, equivalent_length)
                )
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                route[i]['P_out'] = route[i+1]['P_in']
                route[i]['P_in'] = route[i]['P_out'] + route[i]['pressure_drop'] + route[i]['static_pressure']
                # P_out = P_in - delta_P - delta_static_P
                # P_in = P_out + delta_P + delta_static_P
                # print (route[i])
                # caled_staticP_and_deltaP_lines.append(target)

            if route[i]['type'] == "vapor_line" :
                flowrate = route[i]['flowrate']
                MW = route[i]['mw']
                fluid_viscosity = route[i]['viscosity']
                fluid_temperature = route[i]['temperature']
                z = route[i]['z']
                cpcv = route[i]['CpCv']
                pipe_size_ID = route[i]['pipe_size_ID']                
                roughness = route[i]['roughness']
                equivalent_length = route[i]['equivalent_length']   
                P_out = route[i+1]['P_in']
                
                route[i]['pressure_drop'], route[i]['density'], route[i]['velocity'], route[i]['reynolds'], route[i]['P_in'], route[i]['Ma1'],  route[i]['P_out'], route[i]['Ma2'],= (
                module_calculation.vapor_pressure_loss_known_P_out(flowrate, MW, fluid_viscosity, fluid_temperature, z, cpcv, pipe_size_ID, roughness, equivalent_length, P_out)
                )
                
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                route[i]['P_out'] = route[i+1]['P_in']
                route[i]['P_in'] = route[i]['P_out'] + route[i]['pressure_drop'] + route[i]['static_pressure']

            if route[i]['type'] == "two_phase_line" : 
                wt_liquid = route[i]['liquid_flowrate'] 
                density_liquid = route[i]['liquid_density'] 
                wt_vapor = route[i]['vapor_flowrate'] 
                density_vapor = route[i] ['vapor_density']                        
                pipe_size_ID = route[i]['pipe_size_ID']                
                roughness = route[i]['roughness']
                equivalent_length = route[i]['equivalent_length']   

                route[i]['pressure_drop'], route[i]['density'], route[i]['velocity'], route[i]['reynolds'] = (
                module_calculation.two_phase_pressure_loss_homogeneous (wt_liquid, density_liquid, wt_vapor, density_vapor, pipe_size_ID, roughness, equivalent_length)          
                ) 
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                route[i]['P_out'] = route[i+1]['P_in']
                route[i]['P_in'] = route[i]['P_out'] + route[i]['pressure_drop'] + route[i]['static_pressure']                

            if route[i]['type'] == "user_line" : 
                pipe_size_ID = route[i]['pipe_size_ID']                
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                route[i]['P_out'] = route[i+1]['P_in']
                route[i]['P_in'] = route[i]['P_out'] + route[i]['pressure_drop'] + route[i]['static_pressure']    
                     
            if route[i]['type'] == "SorD" : 
                route[i]['EL_in'] =  route[i]['elevation']
                route[i]['EL_out'] =  route[i]['elevation']
                if i == (len(route)-1) : # 시작을 destination에서 부터
                    route[i]['P_in'] = route[i]['operating_pressure']
                    route[i]['P_out'] = route[i]['operating_pressure']
                if i == 0 :   # 끝을 Source 에서 마감.
                    route[i]['P_in'] = route[i]['operating_pressure']
                    route[i]['P_out'] = route[i+1]['P_in']
                # route[i]['deviation'] = route[i]['operating_pressure'] - route[i]['P_in'] 
                # 역방향으로 왔고, pump가 없다면, 처음 출발 여기에 deviation 적어둠.
                                
            if route[i]['type'] == "delta_P_all" : # ΔP Eq, Inst, valve, junction, etc,
                route[i]['EL_in'] = route[i]['elevation']
                route[i]['EL_out'] = route[i]['elevation']
                # print (i, route[i]['A_tag_no'], route[i]['pressure_drop'], route)
                route[i]['P_out'] = route[i+1]['P_in']
                route[i]['P_in'] = route[i]['P_out'] + route[i]['pressure_drop'] 

            if route[i]['type'] == "fixed_control_valve" : # valve
                route[i]['EL_in'] = route[i]['elevation']
                route[i]['EL_out'] = route[i]['elevation']
                route[i]['P_out'] = route[i+1]['P_in']
                route[i]['P_in'] = route[i]['P_out'] + route[i]['pressure_drop'] 
                       
            if route[i]['type'] == "control_valve" : # header 찾기용으로 값없음.
                route[i]['EL_in'] =  route[i]['elevation']
                route[i]['EL_out'] =  route[i]['elevation']
                route[i]['P_out'] = route[i+1]['P_in']        
                route[i]['P_in'] = route[i]['P_out'] 
   
            if route[i]['type'] == "fixed_pump" or route[i]['type'] == "variable_pump" : 
                route[i]['EL_in'] =  route[i]['elevation']
                route[i]['EL_out'] =  route[i]['elevation']
                route[i]['P_out'] = route[i+1]['P_in']
                break

    return routes
        
def calculate_each_route_object_forward (grouped_routes) : # 순방향
    main_header_discharge_pressure = None  # 루프 밖에 선언해두면 기억됨
    for k, routes in enumerate(grouped_routes):
        for j, route in enumerate(routes):
            for i, object in enumerate(route) :
                if object['type'] == "liquid_line" : 
                    flowrate = object['flowrate']
                    pipe_size_ID = object['pipe_size_ID']
                    equivalent_length = object['equivalent_length']  
                    density = object['density']
                    viscosity = object['viscosity']
                    roughness = object['roughness']
                    # pressure_loss_kg_cm2, velocity, reynolds_number
                    route[i]['pressure_drop'], route[i]['velocity'], route[i]['reynolds'] = module_calculation.liquid_pressure_loss(flowrate, density, viscosity, pipe_size_ID, roughness, equivalent_length)
                    route[i]['pressure_drop'] = route[i]['pressure_drop']
                    route[i]['velocity'] = route[i]['velocity']
                    route[i]['reynolds'] = route[i]['reynolds']

                    route[i]['EL_in'] =  route[i-1]['elevation']
                    route[i]['EL_out'] =  route[i+1]['elevation']
                    route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop'] - route[i]['static_pressure']
                    route[i]['vol_flowrate'] = flowrate / density
                    route[i]['pressure_drop_100m'] = route[i]['pressure_drop'] / equivalent_length * 100
                    route[i]['phase'] = 'liquid'

                if object['type'] == "vapor_line" :
                    flowrate = object['flowrate']
                    MW = object['mw']
                    fluid_viscosity = object['viscosity']
                    fluid_temperature = object['temperature']
                    z = object['z']
                    cpcv = object['CpCv']
                    pipe_size_ID = object['pipe_size_ID']                
                    roughness = object['roughness']
                    equivalent_length = object['equivalent_length']   
                    P_in = route[i-1]['P_out']
                    
                    route[i]['pressure_drop'], route[i]['density'], route[i]['velocity'], route[i]['reynolds'], route[i]['P_in'], route[i]['Ma1'],  route[i]['P_out'], route[i]['Ma2'],= (
                    module_calculation.vapor_pressure_loss_known_P_in(flowrate, MW, fluid_viscosity, fluid_temperature, z, cpcv, pipe_size_ID, roughness, equivalent_length, P_in)
                    )
                    route[i]['pressure_drop'] = route[i]['pressure_drop']
                    route[i]['velocity'] = route[i]['velocity']
                    route[i]['reynolds'] = route[i]['reynolds']
                    route[i]['P_in'] = route[i]['P_in']
                    route[i]['Ma1'] = route[i]['Ma1']
                    route[i]['P_out'] = route[i]['P_out']
                    route[i]['Ma2'] = route[i]['Ma2']

                    route[i]['EL_in'] =  route[i-1]['elevation']
                    route[i]['EL_out'] =  route[i+1]['elevation']
                    route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop'] - route[i]['static_pressure']
                    route[i]['vol_flowrate'] = flowrate / route[i]['density']
                    route[i]['pressure_drop_100m'] = route[i]['pressure_drop'] / equivalent_length * 100
                    route[i]['temperature'] = fluid_temperature
                    route[i]['phase'] = 'vapor'

                if object['type'] == "two_phase_line" : 
                    wt_liquid = object['liquid_flowrate'] 
                    density_liquid = object['liquid_density'] 
                    wt_vapor = object['vapor_flowrate'] 
                    density_vapor = object['vapor_density']                        
                    pipe_size_ID = object['pipe_size_ID']                
                    roughness = object['roughness']
                    equivalent_length = object['equivalent_length']   

                    route[i]['pressure_drop'], route[i]['density'], route[i]['velocity'], route[i]['reynolds'] = (
                    module_calculation.two_phase_pressure_loss_homogeneous (wt_liquid, density_liquid, wt_vapor, density_vapor, pipe_size_ID, roughness, equivalent_length)          
                    ) 
                    route[i]['pressure_drop'] = route[i]['pressure_drop']
                    route[i]['density'] = route[i]['density']                    
                    route[i]['velocity'] = route[i]['velocity']
                    route[i]['reynolds'] = route[i]['reynolds']

                    route[i]['EL_in'] =  route[i-1]['elevation']
                    route[i]['EL_out'] =  route[i+1]['elevation']
                    route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop'] - route[i]['static_pressure']
                    route[i]['flowrate'] = wt_liquid + wt_vapor
                    route[i]['vol_flowrate'] = route[i]['flowrate'] / route[i]['density']
                    route[i]['pressure_drop_100m'] = route[i]['pressure_drop'] / equivalent_length * 100      
                    route[i]['phase'] = '2 phase'

                if object['type'] == "user_line" : 
                    # route[i]['pressure_drop'] = route[i]['pressure_drop']
                    # route[i]['density'] = "-"                    
                    # route[i]['velocity'] = "-"
                    # route[i]['reynolds'] = "-"
                    pipe_size_ID = route[i]['pipe_size_ID']   
                    route[i]['EL_in'] =  route[i-1]['elevation']
                    route[i]['EL_out'] =  route[i+1]['elevation']
                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop'] - route[i]['static_pressure']
                    # route[i]['flowrate'] = "-"
                    # route[i]['vol_flowrate'] = "-"
                    # route[i]['pressure_drop_100m'] = "-"      
                    route[i]['phase'] = 'user'
                    # print("oK")
                    
                if object['type'] == "SorD" : 
                    object['EL_in'] =  object['elevation']
                    object['EL_out'] =  object['elevation']
                    if i == (len(route)-1) : # 종점 destination
                        route[i]['P_in'] = route[i-1]['P_out']
                        route[i]['P_out'] = route[i]['operating_pressure']
                        ii = next((ii for ii, obj in enumerate(route) if obj.get('type') == 'control_valve'), -1)
                        # print(route)
                        if not(ii == -1) : # control valve가 있다.
                            if any(route[ii]['ID'] in {o['ID'] for r in routes if r != route for o in r} for object in route): # 다른 header에 겹쳤는가?
                                if route[ii]['pressure_drop'] == 0 : # 0가 들어있으면 sub header control valve
                                    route[ii]['pressure_drop'] = route[i]['P_in'] - route[i]['P_out']
                                    route[i]['P_in'] = route[i]['P_out']
                            else: # main control valve는 이미 pump에서 계산되었음.
                                # route[ii]['pressure_drop'] = route[i]['P_in'] - route[i]['P_out']
                                route[i]['P_in'] = route[i]['P_out']
                    if i == 0 :   # 출발점 Source 
                        route[i]['P_in'] = route[i]['operating_pressure']
                        route[i]['P_out'] = route[i]['operating_pressure']
                                                
                    # route[i]['deviation'] = route[i]['operating_pressure'] - route[i]['P_in'] 
                    # 순방향으로 왔고, 종점에 deviation 적어둠
                    
                if object['type'] == "delta_P_all" : # ΔP Eq, Inst, valve, junction, etc,
                    route[i]['EL_in'] = route[i]['elevation']
                    route[i]['EL_out'] = route[i]['elevation']
                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop'] 

                if object['type'] == "fixed_control_valve" : #valve
                    route[i]['EL_in'] = route[i]['elevation']
                    route[i]['EL_out'] = route[i]['elevation']
                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop'] 
                 
                if route[i]['type'] == "control_valve" : # 순방향... 두 종류가 있음..
                    if 'pressure_drop' in route[i] and route[i]['pressure_drop'] is not None: # main header control valve, 이미 pressure_drop이 결정되었음.
                        route[i]['EL_in'] = route[i]['elevation']
                        route[i]['EL_out'] = route[i]['elevation']
                        route[i]['P_in'] = route[i-1]['P_out'] 
                        route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop']

                    else:
                        route[i]['EL_in'] = route[i]['elevation']
                        route[i]['EL_out'] = route[i]['elevation']
                        route[i]['P_in'] = route[i-1]['P_out'] 
                        # route[i]['pressure_drop'] = route[len(route)-1]['P_in'] - route[len(route)-1]['P_out'] # 종점 destination에 적어둔 값
                        route[i]['pressure_drop'] = route[i]['P_in'] - route[i]['P_out'] # 종점 destination에 적어둔 값
                        
                    # if i == (len(route)-1) : # 종점 destination
                    #     route[i]['P_in'] = route[i-1]['P_out']
                    # try:
                    #     print(i,j,k,"C/V", i, route[i]['A_tag_no'], route[i]['P_in'], route[i]['P_out'], route[i]['pressure_drop'])
                    # except KeyError:
                    #     # print(i,j,k,route)
                    #     print(f"🚨 KeyError at i={i}: {route[i]}")
                    #     raise  # 에러 다시 던짐

                    # route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop']

                if object['type'] == "fixed_pump" or object['type'] == "variable_pump" : 
                    
                    if object['type'] == "fixed_pump" :
                        route[i]['P_in'] = route[i-1]['P_out'] 
                        route[i]['P_out'] = route[i]['P_in'] + route[i]['differential_pressure'] # pump head 고정형
                        ii = next((ii for ii, obj in enumerate(route) if obj.get('type') == 'control_valve'), -1)
                        if ii == -1 : # C/V가 없다
                            pass
                        else : # C/V 있음
                            pass                        
                    
                    else: # variable pump
                        route[i]['P_in'] = route[i-1]['P_out']
                        if j == 0 : # header의 첫번째 route
                            main_header_discharge_pressure = route[i]['P_out'] # 역방향에서 구한값 
                            ii = next((ii for ii, obj in enumerate(route) if obj.get('type') == 'control_valve'), -1)
                            if ii == -1 : # C/V가 없다  
                                route[i]['P_out'] = main_header_discharge_pressure
                            else : # C/V가 있는 main header
                                discharge_route = route[i+1:len(route)-1]
                                route[ii]['pressure_drop'] = 0 # 아래 sum이 안되는 문제발생으로 초기값 넣어줌.
                                total_pressure_drop = sum(item['pressure_drop'] for item in discharge_route) # dynamic loss
                                control_valve_pressure_drop = total_pressure_drop * 0.333
                                if control_valve_pressure_drop < 0.5 : 
                                    control_valve_pressure_drop = 0.5
                                # print (f'control valve {control_valve_pressure_drop}')
                                route[i]['P_out'] = main_header_discharge_pressure + control_valve_pressure_drop
                                route[ii]['pressure_drop'] = control_valve_pressure_drop

                            route[i]['differential_pressure'] = route[i]['P_out'] - route[i]['P_in']
                            main_header_discharge_pressure = route[i]['P_out']

                            # print ("pump", i, ii, control_valve_pressure_drop, route[ii]['pressure_drop'])
                        else : # C/V는 있는데 sub header branch 
                            route[i]['P_out'] = main_header_discharge_pressure  # 이미 main header에서 구한값
                            route[i]['differential_pressure'] = route[i]['P_out'] - route[i]['P_in']

                    # NPSH 구하기 
                    static_head = route[i]['suction_min_liquid_level_from_GL'] - route[0]['elevation'] 
                    NPSHa = (route[i]['P_in'] - (route[i]['vapor_pressure'] - (1.01325 if config.pressure_selection == 'bar' else 1.033))) / (route[i]['specific_gravity']*1000) * (10197 if config.pressure_selection == 'bar' else 10000)  + static_head
                    route[i]['NPSHa'] = NPSHa
                    route[i]['differential_head'] =  route[i]['differential_pressure'] * (10.197 if config.pressure_selection == 'bar' else 10.000) / route[i]['specific_gravity']
                    route[i]['capacity'] =  route[i-1]['flowrate']
                       
    return grouped_routes   
                   
def cal_static_head (routes):
    caled_staticP_and_deltaP_lines =[]
    for route in routes :
        for i, target in enumerate(route) :
            if route[i]['type'] == "liquid_line" : # 여기서 line의 Static head 계산됨.
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                route[i]['static_pressure'] = (route[i+1]['elevation'] - route[i-1]['elevation']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                
                flowrate = route[i]['flowrate']
                density = route[i]['density']
                viscosity = route[i]['viscosity']
                pipe_size_ID = route[i]['pipe_size_ID']                
                roughness = route[i]['roughness']
                equivalent_length = route[i]['equivalent_length']                        
              
                # print (route[i])
                # pressure_loss_kg_cm2, velocity, reynolds_number
                route[i]['delta_P'], route[i]['velocity'], route[i]['reynolds'] = module_calculation.liquid_pressure_loss(flowrate, density, viscosity, pipe_size_ID, roughness, equivalent_length)
                caled_staticP_and_deltaP_lines.append(target)
            if route[i]['type'] == "vapor_line" : # 여기서 line의 Static head 계산됨.    
                # fluid_density = (p1/101.325) * MW / 0.0820544 / (fluid_temperature * z)
                pass
    # line들이 route별로 있으므로 중복된 line이 많음. / 하여 중복된 line을 제거하고 하나로 만듬. 속도 빠르고 실수 없도록 변환환
    seen = set()
    unique_caled_staticP_and_deltaP_lines = []
    for d in caled_staticP_and_deltaP_lines:
        t = tuple(sorted(d.items()))
        if t not in seen:
            seen.add(t)
            unique_caled_staticP_and_deltaP_lines.append(d)
    # print (unique_caled_staticP_and_deltaP_lines)
    return unique_caled_staticP_and_deltaP_lines

def group_header_determination (grouped_routes):
    for routes in grouped_routes :
        for i, route in enumerate(routes):
            ii = next((ii for ii, obj in enumerate(route) if obj.get('type') == 'variable_pump' or obj.get('type') == 'fixed_pump'), -1)
            if ii == -1 : # pump 없음.
                if i==0:            
                    pressure_origin = route[i]['P_out']
                else:
                    pressure_new = route[i]['P_out']    
                    if pressure_origin > pressure_new :
                        pass
                    else:
                        item = routes.pop(i)  
                        routes.insert(0, item) # Header를 맨 앞으로..
                        pressure_origin = pressure_new
                # print (i, ii, route)        
            else: # pump 있음 ii 순서에 pump 있음 
                if i==0:            
                    pressure_origin = route[ii]['P_out']
                else:
                    pressure_new = route[ii]['P_out']    
                    if pressure_origin > pressure_new :
                        pass
                    else:
                        item = routes.pop(i)  
                        routes.insert(0, item) # Header를 맨 앞으로..
                        pressure_origin = pressure_new                
    return grouped_routes    

def extract_lines(final_grouped_routes):
    only_lines = []
    seen_tags = set()  # 중복 방지용 집합
    # print(final_grouped_routes[0])
    for routes in final_grouped_routes:
        for route in routes:
            for obj in route:
                if obj['type'] in ["liquid_line", "vapor_line", "two_phase_line", "user_line"]:
                    tag = obj.get('A_tag_no')
                    if tag not in seen_tags:
                        seen_tags.add(tag)
                        only_lines.append(obj)
    return only_lines
# def extract_lines(final_grouped_routes):
#     only_lines = []
#     seen_tags = set()
#     first_route_processed = False

#     for routes in final_grouped_routes:
#         for route in routes:
#             for obj in route:
#                 if obj['type'] in ["liquid_line", "vapor_line", "two_phase_line"]:
#                     tag = obj.get('A_tag_no')
#                     if tag not in seen_tags:
#                         seen_tags.add(tag)
#                         # 첫 번째 route만 선 두께를 2로 변경
#                         if not first_route_processed:
#                             if 'style' in obj:
#                                 style = obj['style']
#                                 if 'strokeWidth=' in style:
#                                     style = style.replace('strokeWidth=1', 'strokeWidth=2')
#                                 else:
#                                     style += ';strokeWidth=2'
#                                 obj['style'] = style
#                             # obj['strokeWidth'] = 2  # 이렇게 하면 XML에는 반영 안 됨!
#                         only_lines.append(obj)
#             # 첫 번째 route 처리 완료
#             if not first_route_processed:
#                 first_route_processed = True
#     return only_lines

# def extract_control_valves(final_grouped_routes):
#     only_valves = []
#     seen_tags = set()  # 중복 방지용 집합
#     for routes in final_grouped_routes:
#         for route in routes:
#             for obj in route:
#                 if obj['type'] in ["control_valve", "fixed_control_valve"]:
#                     tag = obj.get('A_tag_no')
#                     if tag not in seen_tags:
#                         seen_tags.add(tag)
#                         only_valves.append(obj)
#     return only_valves

def extract_control_valves(final_grouped_routes):
    only_valves = []
    seen_keys = set()  # 중복 방지를 위한 (tag, id) 튜플 집합
    for routes in final_grouped_routes:
        for route in routes:
            for obj in route:
                if obj['type'] in ["control_valve", "fixed_control_valve"]:
                    tag = obj.get('A_tag_no')
                    obj_id = obj.get('ID')  # id도 함께 고려
                    key = (tag, obj_id)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        only_valves.append(obj)
    return only_valves


def extract_pumps (final_grouped_routes):
    only_contents = ""
    only_pumps = []
    seen_tags = set()  # 중복 방지용 집합
    # pressure_selection에 따라 단위 설정
    unit = {
        'pressure': 'bar' if config.pressure_selection == 'bar' else 'kg/cm2',
        'gauge': 'bar.g' if config.pressure_selection == 'bar' else 'kg/cm2.g',
        'absolute': 'bar.A' if config.pressure_selection == 'bar' else 'kg/cm2.A'
    }    
    for routes in final_grouped_routes:
        for route in routes:
            for obj in route:
                if obj['type'] in ["variable_pump", "fixed_pump"]:
                    tag = obj.get('A_tag_no')
                    if tag not in seen_tags:
                        seen_tags.add(tag)
                        vol_capacity = obj['capacity'] /  (obj['specific_gravity'] *1000)
                        contents = (
                            f"{obj['A_tag_no']} \n"
                            f" capacity : {vol_capacity:.2f} [m3/hr] \n"
                            f" diff. P : {obj['differential_pressure']:.2f} [{unit['pressure']}] \n"
                            f" diff. H : {obj['differential_head']:.2f} [m] \n"
                            f" suct. P : {obj['P_in']:.2f} [{unit['gauge']}] \n"
                            f" disc. P : {obj['P_out']:.2f} [{unit['gauge']}] \n"
                            f" sp. gr. : {obj['specific_gravity']:.3f} [-] \n"
                            f" vap. P  : {obj['vapor_pressure']:.2f} [{unit['absolute']}] \n"
                            f" NPSHa : {obj['NPSHa']:.2f} [m] \n  @ pump baseplate {obj['elevation']:.2f} m \n"
                        )
                        only_contents += contents + "\n"   
                        only_pumps.append(obj)
    return only_pumps, only_contents

def extract_deviation (final_grouped_routes) :
    temp_text = "Deviation : \n"
    for idx, group in enumerate(final_grouped_routes):
        # temp_text += f"  Group {{{idx+1}}} : \n"
        for loop in group: # error 코드 만들어야 함. 잘못 연결된 경우 멈추는 경우에 대하여 ..
            temp= []
            for i, item in enumerate(loop) :
                if item['type'] in ['liquid_line', 'vapor_line', 'two_phase_line'] :
                    temp.append(f'[{item['A_tag_no']}]')    
                else :    
                    # temp.append(item['A_tag_no'])
                    pass
                if i == len(loop)-1 : #end
                    deviation = item['P_in'] - item['P_out']
                    temp.append(f"deviation : {deviation:.3f} [{'bar' if config.pressure_selection == 'bar' else 'kg/cm2'}]")
            temp_join = f"     " + " \u2192 ".join(str(item) for item in temp) # 오른쪽 화살표
            temp_text += temp_join +"\n"
    return temp_text        