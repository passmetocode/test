from collections import defaultdict
import math, config
# ✅ Liquid Line sizing
def liquid_pressure_loss(flow_rate, fluid_density, fluid_viscosity, pipe_diameter, pipe_roughness, pipe_length):
    """
    Calculate the pressure loss in a pipeline.

    Parameters:
    flow_rate (float): Flow rate of the fluid in cubic meters per hour (kg/h)
    pipe_diameter (float): Inner diameter of the pipe in inches (inch)
    pipe_length (float): Length of the pipe in meters (m)
    fluid_density (float): Density of the fluid in kilograms per cubic meter (kg/m^3)
    fluid_viscosity (float): Dynamic viscosity of the fluid in centipoise (cP)
    pipe_roughness (float): Roughness of the inner surface of the pipe in feet (ft)

    Returns:
    float: Pressure loss in kg/cm²
    """
    # Convert flow rate from kg/h to m^3/h
    flow_rate = flow_rate / fluid_density
  
    # Convert flow rate from m^3/h to m^3/s
    flow_rate = flow_rate / 3600
    
    # Convert fluid viscosity from cP to Pa.s
    fluid_viscosity = fluid_viscosity / 1000
    
    # Convert pipe diameter from inches to meters
    pipe_diameter = pipe_diameter * 0.0254
    
    # Convert pipe roughness from feet to meters
    pipe_roughness = pipe_roughness
    
    # Calculate the cross-sectional area of the pipe
    area = math.pi * (pipe_diameter / 2) ** 2
    
    # Calculate the velocity of the fluid m/sec
    velocity = flow_rate / area

    # Calculate the Reynolds number
    reynolds_number = (fluid_density * velocity * pipe_diameter) / fluid_viscosity
    
    # Calculate the friction factor using the 1979 Chen Equation
    def chen_friction_factor(reynolds_number, pipe_roughness, pipe_diameter):
        if reynolds_number < 2100 :
            return 64/reynolds_number
        A4 = (pipe_roughness/pipe_diameter)**1.1098 / 2.8257 + (7.149/reynolds_number)**0.8981
        f = -4.0 * math.log10( (pipe_roughness/pipe_diameter)/3.7065 - 5.0452/reynolds_number*math.log10(A4))
        # A = (-4.0 * math.log10(pipe_roughness / (3.7 * pipe_diameter))) ** -2
        # B = (5335.0 / reynolds_number) ** 0.9
        friction_factor = 1.0 / math.sqrt(f)
        return friction_factor
    
        # Calculate the friction factor using the Serghides (1984) Equation
    def serghides_friction_factor(reynolds_number, pipe_roughness, pipe_diameter):
        if reynolds_number < 2100 :
            return 64/reynolds_number
        A = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 12 / reynolds_number)) 
        B = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 2.51 * A / reynolds_number )) 
        C = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 2.51 * B / reynolds_number ))
        
        friction_factor = (A - ((B - A) ** 2) / (C - 2 * B + A)) ** -2
        return friction_factor
    
    # friction_factor = chen_friction_factor(reynolds_number, pipe_roughness, pipe_diameter)
    friction_factor = serghides_friction_factor(reynolds_number, pipe_roughness, pipe_diameter)    
    # Calculate the pressure loss using the Darcy-Weisbach equation
    # pressure_loss_pa = friction_factor * (pipe_length / pipe_diameter) * 0.5 * fluid_density * velocity ** 2
    
    # Convert pressure loss from Pascals to kg/cm²
    pressure_loss_kg_cm2 = friction_factor * (pipe_length / pipe_diameter) * (velocity**2 / (2 * 9.80665)) * (fluid_density / 10000)

    # Convert to other units
    pressure_loss_bar = pressure_loss_kg_cm2 * 0.980665
    pressure_loss_MPa = pressure_loss_kg_cm2 * 0.0980665

    # pressure_selection에 따라 반환
    if config.pressure_selection == 'bar':
        pressure_loss = pressure_loss_bar
    elif config.pressure_selection == 'MPa':
        pressure_loss = pressure_loss_MPa
    else:  # 기본값은 kg/cm²
        pressure_loss = pressure_loss_kg_cm2

    return pressure_loss, velocity, reynolds_number

# ⚡ # Example usage
# flow_rate = 100000  # kg/h
# pipe_diameter = 4.023  # inch
# pipe_length = 100  # m
# fluid_density = 960  # kg/m^3
# fluid_viscosity = 0.95  # cP
# pipe_roughness = 0.000328084  # ft

# pressure_loss = liquid_pressure_loss(flow_rate, fluid_density, fluid_viscosity, pipe_diameter, pipe_roughness, pipe_length)

# print(f"Pressure loss: {pressure_loss[0]} kg/cm² {pressure_loss[1]} m/s  {pressure_loss[2]}" )

# ✅ Vapor_Line sizing
def vapor_pressure_loss_known_P_in(flow_rate, MW, fluid_viscosity, fluid_temperature, z, cpcv, pipe_diameter, pipe_roughness, pipe_length, P_in): # 정방향
    """
    Calculate the final pressure (P2) in a pipeline for vapor fluid using the Newton-Raphson method.

    Parameters:
    flow_rate (float): Flow rate of the vapor in cubic meters per hour (kg/h)
    pipe_diameter (float): Inner diameter of the pipe in inches (inch)
    pipe_length (float): Length of the pipe in meters (m)
    fluid_mw (float): Density of the vapor in kilograms per cubic meter (kg/m^3)
    fluid_viscosity (float): Dynamic viscosity of the vapor in centipoise (cP)
    pipe_roughness (float): Roughness of the inner surface of the pipe in feet (ft)
    p1 (float): Initial pressure in kg/cm2.g
    Returns:
    float: Final pressure P2 in kg/cm²
    """
    # pressure_selection에 따라 입력 압력 단위 변환
    if config.pressure_selection == 'bar':
        P_in_kgcm2 = P_in * 1.01972  # Convert bar to kg/cm².g
    elif config.pressure_selection == 'MPa':
        P_in_kgcm2 = P_in * 10.1972  # Convert MPa to kg/cm².g
    else:
        P_in_kgcm2 = P_in
                 
    p1 = P_in_kgcm2
    # Convert flow rate from kg/h to kg/s
    flow_rate = flow_rate / 3600   
    p1 = (p1 + 1.03323) * 98.0665 # kg/cm2.g를 환산 kPaA   
    fluid_temperature = (273.15 + fluid_temperature)
    fluid_density = (p1/101.325) * MW / 0.0820544 / (fluid_temperature * z)
    # Convert flow rate from kg/s to m^3/s
    flow_rate_vol = flow_rate / fluid_density # m^3/s
    
    # Convert fluid viscosity from cP to Pa.s
    fluid_viscosity = fluid_viscosity / 1000
    
    # Convert pipe diameter from inches to meters
    pipe_diameter = pipe_diameter * 0.0254
    
    # Convert pipe roughness from feet to meters
    pipe_roughness = pipe_roughness 
   
    # Calculate the cross-sectional area of the pipe
    area = math.pi * (pipe_diameter / 2) ** 2

     # Calculate the velocity of the vapor
    velocity = flow_rate_vol / area

    # Calculate the velocity of the vapor
    Ma1 = 3.25 * 10**-5 * (flow_rate * 3600 / (p1 * pipe_diameter**2))*(z*fluid_temperature/MW/cpcv)**0.5
    
    # Calculate the Reynolds number
    reynolds_number = (fluid_density * velocity * pipe_diameter) / fluid_viscosity

    # Calculate the friction factor using the Serghides (1984) Equation
    def serghides_friction_factor(reynolds_number, pipe_roughness, pipe_diameter):
        if reynolds_number < 2100 :
            return 64/reynolds_number
        A = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 12 / reynolds_number)) 
        B = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 2.51 * A / reynolds_number )) 
        C = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 2.51 * B / reynolds_number ))
        
        friction_factor = (A - ((B - A) ** 2) / (C - 2 * B + A)) ** -2
        return friction_factor
    friction_factor = serghides_friction_factor(reynolds_number, pipe_roughness, pipe_diameter)    
        
    # Define the function for final pressure P2 calculation using Newton-Raphson method
    def newton_raphson(f, df, x0, tol = 1e-6, max_iter =100):
        x = x0
        for _ in range(max_iter):
            x_new = x - f(x) / df(x) # NR 공식 적용
            if abs(x_new-x) < tol:  # 수렴조건
                return x_new
            x = x_new
            return x # 최대 반복후 반환
    f = lambda p2:  friction_factor * pipe_length / pipe_diameter - 1 / math.pow(Ma1, 2) * (1 - math.pow(p2 / p1, 2)) - math.log(math.pow(p1 / p2, 2))   
    df = lambda p2:  2 * p2 / (p1**2 * math.pow(Ma1, 2)) + 2 / p2   
    
    p2_guess = newton_raphson (f, df, p1*0.95)
    Ma2 = 3.25 * 10**-5 * (flow_rate * 3600 / (p2_guess * pipe_diameter**2))*(z*fluid_temperature/MW/cpcv)**0.5    
    p2_kg_cm2 = p2_guess / 98.0665 - 1.03323
    # Convert p2 from kg/cm² to bar and MPa
    p2_bar = p2_kg_cm2 * 0.980665
    p2_MPa = p2_kg_cm2 * 0.0980665

    # pressure_selection에 따라 압력 손실 계산
    if config.pressure_selection == 'bar':
        pressure_loss = P_in - p2_bar
        p2_out = p2_bar
    elif config.pressure_selection == 'MPa':
        pressure_loss = P_in - p2_MPa
        p2_out = p2_MPa
    else:  # 기본값은 kg/cm²
        pressure_loss = P_in - p2_kg_cm2
        p2_out = p2_kg_cm2

    # 결과 반환
    return pressure_loss, fluid_density, velocity, reynolds_number, P_in, Ma1, p2_out, Ma2

# ⚡ # Example usage
# flow_rate = 10000  # kg/h
# pipe_diameter = 6.026  # inch
# pipe_length = 100  # m
# pipe_roughness = 0.000328084  # ft
# fluid_viscosity = 0.0181  # cP (viscosity of air at room temperature)
# fluid_temperature = 60  # deg C
# p1 = 5  # kg/cm2.g (initial pressure)
# MW = 36
# z=1
# cpcv=1.4
# # friction_factor = 0.02  # Known friction factor

# p2_kg_cm2 = vapor_pressure_loss_known_P_in(flow_rate, MW, fluid_viscosity, fluid_temperature, z, cpcv, pipe_diameter, pipe_roughness, pipe_length, p1)
# print(f"Final pressure P1 -> P2 : {p2_kg_cm2} kg/cm² g")

# ✅ Vapor_Line sizing
def vapor_pressure_loss_known_P_out(flow_rate, MW, fluid_viscosity, fluid_temperature, z, cpcv, pipe_diameter, pipe_roughness, pipe_length, P_out): # 역방향
    if config.pressure_selection == 'bar':
        P_kgcm2_out = P_out * 1.01972 # Convert bar to kg/cm².g  bar로 입력한 경우.
    elif config.pressure_selection == 'MPa':
        P_kgcm2_out = P_out * 10.1972  # Convert MPa to kg/cm².g 
    else:
        P_kgcm2_out = P_out  
    # Convert flow rate from kg/h to kg/s
    p2 = P_kgcm2_out
    # print(config.pressure_selection, p2)
    flow_rate = flow_rate / 3600   
    p2 = (p2 + 1.03323) * 98.0665 # kg/cm2.g를 환산 kPa   
    fluid_temperature = (273.15 + fluid_temperature)
    fluid_density = (p2/101.325) * MW / 0.0820544 / (fluid_temperature * z)
    # Convert flow rate from kg/s to m^3/s
    flow_rate_vol = flow_rate / fluid_density # m^3/s
    
    # Convert fluid viscosity from cP to Pa.s
    fluid_viscosity = fluid_viscosity / 1000
    
    # Convert pipe diameter from inches to meters
    pipe_diameter = pipe_diameter * 0.0254
    
    # Convert pipe roughness from feet to meters
    pipe_roughness = pipe_roughness 
   
    # Calculate the cross-sectional area of the pipe
    area = math.pi * (pipe_diameter / 2) ** 2

     # Calculate the velocity of the vapor
    velocity = flow_rate_vol / area

    # Calculate the velocity of the vapor
    Ma2 = 3.25 * 10**-5 * (flow_rate * 3600 / (p2 * pipe_diameter**2))*(z*fluid_temperature/MW/cpcv)**0.5
    
    # Calculate the Reynolds number
    reynolds_number = (fluid_density * velocity * pipe_diameter) / fluid_viscosity

    # Calculate the friction factor using the Serghides (1984) Equation
    def serghides_friction_factor(reynolds_number, pipe_roughness, pipe_diameter):
        if reynolds_number < 2100 :
            return 64/reynolds_number
        A = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 12 / reynolds_number)) 
        B = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 2.51 * A / reynolds_number )) 
        C = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 2.51 * B / reynolds_number ))
        
        friction_factor = (A - ((B - A) ** 2) / (C - 2 * B + A)) ** -2
        return friction_factor
    friction_factor = serghides_friction_factor(reynolds_number, pipe_roughness, pipe_diameter)    
        
    # Define the function for final pressure P2 calculation using Newton-Raphson method
    def newton_raphson(f, df, x0, tol = 1e-6, max_iter =100):
        x = x0
        for _ in range(max_iter):
            x_new = x - f(x) / df(x) # NR 공식 적용
            if abs(x_new-x) < tol:  # 수렴조건
                return x_new
            x = x_new
            return x # 최대 반복후 반환
    f = lambda p1:  friction_factor * pipe_length / pipe_diameter - 1 / math.pow(Ma2, 2) * math.pow(p1/p2,2) * (1 - math.pow(p2 / p1, 2)) - math.log(math.pow(p1 / p2, 2))   
    df = lambda p1:  -2/p1 - (2*p1* (1-p2**2/p1**2) / (Ma2**2 * p2**2)) - 2/(Ma2**2*p1)
    
    p1_guess = newton_raphson (f, df, p2*1.05)
    Ma1 = 3.25 * 10**-5 * (flow_rate * 3600 / (p1_guess * pipe_diameter**2))*(z*fluid_temperature/MW/cpcv)**0.5

    p1_kg_cm2 = p1_guess / 98.0665 - 1.03323
    # Convert p1 from kg/cm² to bar and MPa
    p1_bar = p1_kg_cm2 * 0.980665
    p1_MPa = p1_kg_cm2 * 0.0980665
    # print (config.pressure_selection, p1_kg_cm2, p1_MPa)
    # pressure_selection에 따라 압력 손실 계산
    if config.pressure_selection == 'bar':
        pressure_loss = p1_bar - P_out
        p1_out = p1_bar
    elif config.pressure_selection == 'MPa':
        pressure_loss = p1_MPa - P_out
        p1_out = p1_MPa
    else:  # 기본값은 kg/cm²
        pressure_loss = p1_kg_cm2 - P_out
        p1_out = p1_kg_cm2
    # print(config.pressure_selection, p1_out)
    # print (config.pressure_selection, p1_MPa, P_out, "dp=", pressure_loss)
    # 결과 반환
    return pressure_loss, fluid_density, velocity, reynolds_number, p1_out, Ma1, P_out, Ma2

# ⚡ # Example usage
# flow_rate = 10000  # kg/h
# pipe_diameter = 6.026  # inch
# pipe_length = 100  # m
# pipe_roughness = 0.000328084  # ft
# fluid_viscosity = 0.0181  # cP (viscosity of air at room temperature)
# fluid_temperature = 60  # deg C
# p2 = 4.87  # kg/cm2.g (initial pressure)
# MW = 36
# z=1
# cpcv=1.4
# # friction_factor = 0.02  # Known friction factor

# p1_kg_cm2 = vapor_pressure_loss_known_P_out(flow_rate, MW, fluid_viscosity, fluid_temperature, z, cpcv, pipe_diameter, pipe_roughness, pipe_length, p2)
# print(f"Final pressure P1 <- P2 : {p1_kg_cm2} kg/cm² g")

# ✅ 2 Phase Line Sizing
def two_phase_pressure_loss_homogeneous (wt_liquid, density_liquid, wt_vapor, density_vapor, pipe_diameter, pipe_roughness, pipe_length) :
    # Convert flow rate from m3/h to m^3/s
    flowrate_liquid = wt_liquid / density_liquid
    flowrate_liquid = flowrate_liquid / 3600
    flowrate_vapor = wt_vapor / density_vapor
    flowrate_vapor = flowrate_vapor / 3600    
    # Convert fluid viscosity from cP to Pa.s
    fluid_viscosity = 0.1 / 1000   # Homogeneous에서는 iviscosity를 0.1 cP로 가정함.
    
    # Convert pipe diameter from inches to meters
    pipe_diameter = pipe_diameter * 0.0254
    
    # Convert pipe roughness from feet to meters
    pipe_roughness = pipe_roughness 
    
    # Calculate the cross-sectional area of the pipe
    area = math.pi * (pipe_diameter / 2) ** 2
    
    # Calculate the velocity of the fluid
    velocity = (flowrate_liquid + flowrate_vapor) / area
    
    fluid_density = (wt_liquid + wt_vapor)/(wt_liquid/density_liquid + wt_vapor/density_vapor)
    
    # Calculate the Reynolds number
    reynolds_number = (fluid_density * velocity * pipe_diameter) / fluid_viscosity
    
    # Calculate the friction factor using the 1979 Chen Equation
    def chen_friction_factor(reynolds_number, pipe_roughness, pipe_diameter):
        if reynolds_number < 2100 :
            return 64/reynolds_number
        A4 = (pipe_roughness/pipe_diameter)**1.1098 / 2.8257 + (7.149/reynolds_number)**0.8981
        f = -4.0 * math.log10( (pipe_roughness/pipe_diameter)/3.7065 - 5.0452/reynolds_number*math.log10(A4))
        # A = (-4.0 * math.log10(pipe_roughness / (3.7 * pipe_diameter))) ** -2
        # B = (5335.0 / reynolds_number) ** 0.9
        friction_factor = 1.0 / math.sqrt(f)
        return friction_factor
    
        # Calculate the friction factor using the Serghides (1984) Equation
    def serghides_friction_factor(reynolds_number, pipe_roughness, pipe_diameter):
        if reynolds_number < 2100 :
            return 64/reynolds_number
        A = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 12 / reynolds_number)) 
        B = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 2.51 * A / reynolds_number )) 
        C = (-2 * math.log10(pipe_roughness / (3.7 * pipe_diameter) + 2.51 * B / reynolds_number ))
        
        friction_factor = (A - ((B - A) ** 2) / (C - 2 * B + A)) ** -2
        return friction_factor
    
    # friction_factor = chen_friction_factor(reynolds_number, pipe_roughness, pipe_diameter)
    friction_factor = serghides_friction_factor(reynolds_number, pipe_roughness, pipe_diameter)    
    # Calculate the pressure loss using the Darcy-Weisbach equation
    pressure_loss_pa = friction_factor * (pipe_length / pipe_diameter) * 0.5 * fluid_density * velocity ** 2
    
    # Convert pressure loss from Pascals to kg/cm²
    pressure_loss_kg_cm2 = pressure_loss_pa / 98066.5

    # Convert to other units
    pressure_loss_bar = pressure_loss_kg_cm2 * 0.980665
    pressure_loss_MPa = pressure_loss_kg_cm2 * 0.0980665

    # pressure_selection에 따라 반환
    if config.pressure_selection == 'bar':
        pressure_loss = pressure_loss_bar
    elif config.pressure_selection == 'MPa':
        pressure_loss = pressure_loss_MPa
    else:  # 기본값은 kg/cm²
        pressure_loss = pressure_loss_kg_cm2

    return pressure_loss, fluid_density, velocity, reynolds_number

# ⚡ # Example usage
# wt_liquid = 80000  # kg/h
# wt_vapor = 8000 # KG/H
# pipe_diameter = 6.024  # inch
# pipe_length = 100  # m
# density_liquid = 1000  # kg/m^3
# density_vapor = 14  # kg/m^3
# # fluid_viscosity = 0.1  # cP  default 내장
# pipe_roughness = 0.000328084  # ft

# pressure_loss = two_phase_pressure_loss_homogeneous (wt_liquid, wt_vapor, density_liquid, density_vapor, pipe_diameter, pipe_roughness, pipe_length)

# print(f"Pressure loss: {pressure_loss[0]} kg/cm² {pressure_loss[1]} m/s  {pressure_loss[2]}" )




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
                liquid_pressure_loss(flowrate, density, viscosity, pipe_size_ID, roughness, equivalent_length)
                )
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                # route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000 if config.pressure_selection == 'kg/cm2' else 101970)
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
                fluid_temperature = float(route[i]['temperature'])
                z = route[i]['z']
                cpcv = route[i]['CpCv']
                pipe_size_ID = route[i]['pipe_size_ID']                
                roughness = route[i]['roughness']
                equivalent_length = route[i]['equivalent_length']   
                P_out = route[i+1]['P_in']
                # print(P_out)
                route[i]['pressure_drop'], route[i]['density'], route[i]['velocity'], route[i]['reynolds'], route[i]['P_in'], route[i]['Ma1'],  route[i]['P_out'], route[i]['Ma2'],= (
                vapor_pressure_loss_known_P_out(flowrate, MW, fluid_viscosity, fluid_temperature, z, cpcv, pipe_size_ID, roughness, equivalent_length, P_out)
                )
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                # route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000 if config.pressure_selection == 'kg/cm2' else 101970)

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
                two_phase_pressure_loss_homogeneous (wt_liquid, density_liquid, wt_vapor, density_vapor, pipe_size_ID, roughness, equivalent_length)          
                ) 
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                # route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000 if config.pressure_selection == 'kg/cm2' else 101970)

                route[i]['P_out'] = route[i+1]['P_in']
                route[i]['P_in'] = route[i]['P_out'] + route[i]['pressure_drop'] + route[i]['static_pressure']                

            if route[i]['type'] == "user_line" : 
                pipe_size_ID = route[i]['pipe_size_ID']                
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                route[i]['P_out'] = route[i+1]['P_in']
                route[i]['P_in'] = route[i]['P_out'] + float(route[i]['pressure_drop']) + float(route[i]['static_pressure'])    
                     
            if route[i]['type'] == "SorD" : 
                route[i]['EL_in'] =  route[i]['elevation']
                route[i]['EL_out'] =  route[i]['elevation']
                if i == (len(route)-1) : # 시작을 destination에서 부터
                    route[i]['P_in'] = float(route[i]['operating_pressure'])
                    route[i]['P_out'] = float(route[i]['operating_pressure'])
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
                route[i]['P_in'] = route[i]['P_out'] + float(route[i]['pressure_drop']) 

            if route[i]['type'] == "fixed_control_valve" : # valve
                route[i]['EL_in'] = route[i]['elevation']
                route[i]['EL_out'] = route[i]['elevation']
                route[i]['P_out'] = route[i+1]['P_in']
                route[i]['P_in'] = route[i]['P_out'] + float(route[i]['pressure_drop']) 
                       
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

def convert_dp_from_kgcm2(dp_value, to_unit): 
    if dp_value is None:
        return None
    if to_unit == "kg/cm2":
        return dp_value
    elif to_unit == "bar":
        return dp_value * 0.980665
    elif to_unit == "MPa":
        return dp_value * 0.0980665
    else:
        raise ValueError(f"Unsupported pressure unit: {to_unit}")

        
def calculate_each_route_object_forward (grouped_routes) : # 순방향
    main_header_discharge_pressure = None  # 루프 밖에 선언해두면 기억됨
    limits = {
        "liquid": {
            "water": {
                "suction": {
                    "saturation": {
                        "all": {"velocity_min": 0.61, "velocity_max": 1.83, "dp_min": 0.01, "dp_max": 0.12}
                    },
                    "normal": {
                        "all": {"velocity_min": 1.22, "velocity_max": 2.13, "dp_min": 0.01, "dp_max": 1.0}
                    }
                },
                "discharge": {
                    "normal": {
                        "less than 1": {"velocity_min": 0.61, "velocity_max": 0.91, "dp_min": 0.01, "dp_max": 1.0},
                        "less than 2": {"velocity_min": 0.91, "velocity_max": 1.37, "dp_min": 0.01, "dp_max": 1.0},
                        "less than 4": {"velocity_min": 1.52, "velocity_max": 2.13, "dp_min": 0.01, "dp_max": 1.0},
                        "less than 6": {"velocity_min": 2.13, "velocity_max": 2.74, "dp_min": 0.01, "dp_max": 1.0},
                        "less than 8": {"velocity_min": 2.74, "velocity_max": 3.05, "dp_min": 0.01, "dp_max": 1.0},
                        "less than 10": {"velocity_min": 3.05, "velocity_max": 3.66, "dp_min": 0.01, "dp_max": 1.0},
                        "less than 12": {"velocity_min": 3.05, "velocity_max": 4.27, "dp_min": 0.01, "dp_max": 1.0},
                        "less than 16": {"velocity_min": 3.05, "velocity_max": 4.57, "dp_min": 0.01, "dp_max": 1.0},
                        "above 16": {"velocity_min": 3.05, "velocity_max": 4.88, "dp_min": 0.01, "dp_max": 1.0}
                    }
                }
            },
            "HC": {
                "suction": {
                    "saturation": {
                        "all": {"velocity_min": 0.61, "velocity_max": 1.83, "dp_min": 0.01, "dp_max": 1.0}
                    },
                    "normal": {
                        "all": {"velocity_min": 1.22, "velocity_max": 2.44, "dp_min": 0.01, "dp_max": 1.0}
                    }
                },
                "discharge": {
                    "normal": {
                        "all": {"velocity_min": 1.5, "velocity_max": 4.5, "dp_min": 0.01, "dp_max": 0.23}
                    }
                }
            }
        },
        "vapor": {
            "steam": {
                "all": {
                    "normal": {
                        "all": {"velocity_min": None, "velocity_max": 60.96, "dp_min": 0.001, "dp_max": 1.0}
                    }
                }
            },
            "gas": {
                "less than 3.5": {
                    "normal": {
                        "all": {"velocity_min": None, "velocity_max": None, "dp_min": 0.001, "dp_max": 0.06}
                    }
                },
                "less than 10.5": {
                    "normal": {
                        "all": {"velocity_min": None, "velocity_max": None, "dp_min": 0.001, "dp_max": 0.11}
                    }
                },
                "less than 21.1": {
                    "normal": {
                        "all": {"velocity_min": None, "velocity_max": None, "dp_min": 0.001, "dp_max": 0.23}
                    }
                },
                "above 21.1": {
                    "normal": {
                        "all": {"velocity_min": None, "velocity_max": None, "dp_min": 0.001, "dp_max": 0.35}
                    }
                }
            }
        },
        "2 phase": {
            "all": {
                "all": {
                    "all": {
                        "all": {"velocity_min": 1, "velocity_max": 22.86, "dp_min": None, "dp_max": None}
                    }
                }
            }
        }
    }
  
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
                    route[i]['pressure_drop'], route[i]['velocity'], route[i]['reynolds'] = liquid_pressure_loss(flowrate, density, viscosity, pipe_size_ID, roughness, equivalent_length)
                    route[i]['pressure_drop'] = route[i]['pressure_drop']
                    route[i]['velocity'] = route[i]['velocity']
                    route[i]['reynolds'] = route[i]['reynolds']

                    route[i]['EL_in'] =  route[i-1]['elevation']
                    route[i]['EL_out'] =  route[i+1]['elevation']
                    # route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                    route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000 if config.pressure_selection == 'kg/cm2' else 101970)

                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop'] - route[i]['static_pressure']
                    route[i]['vol_flowrate'] = flowrate / density
                    route[i]['pressure_drop_100m'] = route[i]['pressure_drop'] / equivalent_length * 100
                    route[i]['phase'] = 'liquid'
                    
                    # 기준값 판단 로직 (이전 답변에서 제공한 코드)
                    phase = 'liquid'
                    fluid = 'water' if density > 900 else 'HC'

                    pump_indices = [idx for idx, obj in enumerate(route) if obj['type'] in ['fixed_pump', 'variable_pump']]
                    if pump_indices:
                        location = 'suction' if any(i < pump_idx for pump_idx in pump_indices) else 'discharge'
                        nearest_pump_idx = min(pump_indices, key=lambda x: abs(x - i))
                        vapor_pressure = route[nearest_pump_idx].get('vapor_pressure', 0)
                        state = 'saturation' if vapor_pressure > 1 else 'normal'
                        pipesize = 'all'
                        # print(fluid, location, state, pipesize, pump_indices)
                    else:    
                        location = 'discharge'
                        state = 'normal'
                        pipesize = 'all'
                        
                    if fluid == 'water' and location == 'discharge' and state == 'normal' :   
                        pipe_size = route[i]['pipe_size_ID']
                        if pipe_size < 1.1:
                            pipesize = 'less than 1'
                        elif pipe_size < 2.2:
                            pipesize = 'less than 2'
                        elif pipe_size < 4.4:
                            pipesize = 'less than 4'
                        elif pipe_size < 6.4:
                            pipesize = 'less than 6'
                        elif pipe_size < 8.2:
                            pipesize = 'less than 8'
                        elif pipe_size < 10.25:
                            pipesize = 'less than 10'
                        elif pipe_size < 12.26:
                            pipesize = 'less than 12'
                        elif pipe_size < 16:
                            pipesize = 'less than 16'
                        else:
                            pipesize = 'above 16'
                    else:
                        pipesize = 'all'

                    # criteria = limits.get(phase, {}).get(fluid, {}).get(location, {}).get(state, {}).get(pipesize, {})
                    # route[i]['criteria'] = {
                    #     'min_vel': criteria.get('velocity_min'),
                    #     'max_vel': criteria.get('velocity_max'),
                    #     'min_dp': criteria.get('dp_min'),
                    #     'max_dp': criteria.get('dp_max')
                    # }

                    criteria = limits.get(phase, {}).get(fluid, {}).get(location, {}).get(state, {}).get(pipesize, {})
                    dp_unit = config.pressure_selection  # "kg/cm2", "bar", "MPa"
                    route[i]['criteria'] = {
                        'min_vel': criteria.get('velocity_min'),
                        'max_vel': criteria.get('velocity_max'),
                        'min_dp': convert_dp_from_kgcm2(criteria.get('dp_min'), dp_unit),
                        'max_dp': convert_dp_from_kgcm2(criteria.get('dp_max'), dp_unit)
                    }
                    
                if object['type'] == "vapor_line" :
                    flowrate = object['flowrate']
                    MW = object['mw']
                    fluid_viscosity = object['viscosity']
                    fluid_temperature = float(object['temperature'])
                    z = object['z']
                    cpcv = object['CpCv']
                    pipe_size_ID = object['pipe_size_ID']                
                    roughness = object['roughness']
                    equivalent_length = object['equivalent_length']   
                    P_in = route[i-1]['P_out']
                    
                    route[i]['pressure_drop'], route[i]['density'], route[i]['velocity'], route[i]['reynolds'], route[i]['P_in'], route[i]['Ma1'],  route[i]['P_out'], route[i]['Ma2'],= (
                    vapor_pressure_loss_known_P_in(flowrate, MW, fluid_viscosity, fluid_temperature, z, cpcv, pipe_size_ID, roughness, equivalent_length, P_in)
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
                    # route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                    route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000 if config.pressure_selection == 'kg/cm2' else 101970)

                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop'] - route[i]['static_pressure']
                    route[i]['vol_flowrate'] = flowrate / route[i]['density']
                    route[i]['pressure_drop_100m'] = route[i]['pressure_drop'] / equivalent_length * 100
                    route[i]['temperature'] = fluid_temperature
                    route[i]['phase'] = 'vapor'
                    

                    phase = 'vapor'
                    # 분자량 기준으로 steam/gas 구분
                    fluid = 'steam' if abs(route[i]['mw'] - 18.01528) < 0.025 else 'gas'
                   
                    state = 'normal'
                    pipesize = 'all'

                    # 압력 기준으로 location 구분
                    if fluid == 'gas':
                        P_in = route[i]['P_in']
                        if P_in < 3.5:
                            location = 'less than 3.5'
                        elif P_in < 10.5:
                            location = 'less than 10.5'
                        elif P_in < 21.1:
                            location = 'less than 21.1'
                        else:
                            location = 'above 21.1'
                    else:  # steam
                        location = 'all'

                    # 기준값 가져오기
                    # criteria = limits.get(phase, {}).get(fluid, {}).get(location, {}).get(state, {}).get(pipesize, {})
                    # route[i]['criteria'] = {
                    #     'min_vel': criteria.get('velocity_min'),
                    #     'max_vel': criteria.get('velocity_max'),
                    #     'min_dp': criteria.get('dp_min'),
                    #     'max_dp': criteria.get('dp_max')
                    # }
                    criteria = limits.get(phase, {}).get(fluid, {}).get(location, {}).get(state, {}).get(pipesize, {})
                    dp_unit = config.pressure_selection  # "kg/cm2", "bar", "MPa"
                    route[i]['criteria'] = {
                        'min_vel': criteria.get('velocity_min'),
                        'max_vel': criteria.get('velocity_max'),
                        'min_dp': convert_dp_from_kgcm2(criteria.get('dp_min'), dp_unit),
                        'max_dp': convert_dp_from_kgcm2(criteria.get('dp_max'), dp_unit)
                    }

                if object['type'] == "two_phase_line" : 
                    wt_liquid = object['liquid_flowrate'] 
                    density_liquid = object['liquid_density'] 
                    wt_vapor = object['vapor_flowrate'] 
                    density_vapor = object['vapor_density']                        
                    pipe_size_ID = object['pipe_size_ID']                
                    roughness = object['roughness']
                    equivalent_length = object['equivalent_length']   

                    route[i]['pressure_drop'], route[i]['density'], route[i]['velocity'], route[i]['reynolds'] = (
                    two_phase_pressure_loss_homogeneous (wt_liquid, density_liquid, wt_vapor, density_vapor, pipe_size_ID, roughness, equivalent_length)          
                    ) 
                    route[i]['pressure_drop'] = route[i]['pressure_drop']
                    route[i]['density'] = route[i]['density']                    
                    route[i]['velocity'] = route[i]['velocity']
                    route[i]['reynolds'] = route[i]['reynolds']

                    route[i]['EL_in'] =  route[i-1]['elevation']
                    route[i]['EL_out'] =  route[i+1]['elevation']
                    # route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                    route[i]['static_pressure'] = (route[i]['EL_out'] - route[i]['EL_in']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000 if config.pressure_selection == 'kg/cm2' else 101970)

                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - route[i]['pressure_drop'] - route[i]['static_pressure']
                    route[i]['flowrate'] = wt_liquid + wt_vapor
                    route[i]['vol_flowrate'] = route[i]['flowrate'] / route[i]['density']
                    route[i]['pressure_drop_100m'] = route[i]['pressure_drop'] / equivalent_length * 100      
                    route[i]['phase'] = '2 phase'

                    # criteria = limits.get('2 phase', {}).get('all', {}).get('all', {}).get('all', {}).get('all', {})
                    # route[i]['criteria'] = {
                    #     'min_vel': criteria.get('velocity_min'),
                    #     'max_vel': criteria.get('velocity_max'),
                    #     'min_dp': criteria.get('dp_min'),
                    #     'max_dp': criteria.get('dp_max')
                    # }
                    criteria = limits.get(phase, {}).get(fluid, {}).get(location, {}).get(state, {}).get(pipesize, {})
                    dp_unit = config.pressure_selection  # "kg/cm2", "bar", "MPa"
                    route[i]['criteria'] = {
                        'min_vel': criteria.get('velocity_min'),
                        'max_vel': criteria.get('velocity_max'),
                        'min_dp': convert_dp_from_kgcm2(criteria.get('dp_min'), dp_unit),
                        'max_dp': convert_dp_from_kgcm2(criteria.get('dp_max'), dp_unit)
                    }
                if object['type'] == "user_line" : 
                    # route[i]['pressure_drop'] = route[i]['pressure_drop']
                    # route[i]['density'] = "-"                    
                    # route[i]['velocity'] = "-"
                    # route[i]['reynolds'] = "-"
                    pipe_size_ID = route[i]['pipe_size_ID']   
                    route[i]['EL_in'] =  route[i-1]['elevation']
                    route[i]['EL_out'] =  route[i+1]['elevation']
                    route[i]['P_in'] = route[i-1]['P_out']
                    route[i]['P_out'] = route[i]['P_in'] - float(route[i]['pressure_drop']) - float(route[i]['static_pressure'])
                    # route[i]['flowrate'] = "-"
                    # route[i]['vol_flowrate'] = "-"
                    # route[i]['pressure_drop_100m'] = "-"      
                    route[i]['phase'] = 'user'
                    route[i]['criteria'] = {
                        'min_vel': None,
                        'max_vel': None,
                        'min_dp': None,
                        'max_dp': None
                    }
                    
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
                                # if control_valve_pressure_drop < 0.7 : 
                                #     control_valve_pressure_drop = 0.7
                                if config.pressure_selection == 'kg/cm2':
                                    if control_valve_pressure_drop < 0.7:
                                        control_valve_pressure_drop = 0.7
                                elif config.pressure_selection == 'bar':
                                    if control_valve_pressure_drop < 0.686:
                                        control_valve_pressure_drop = 0.686  # 0.7 kg/cm² → 0.686 bar
                                elif config.pressure_selection == 'MPa':
                                    if control_valve_pressure_drop < 0.0686:
                                        control_valve_pressure_drop = 0.0686  # 0.7 kg/cm² → 0.0686 MPa
                               
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
                    # NPSHa = (route[i]['P_in'] - (route[i]['vapor_pressure'] - (1.01325 if config.pressure_selection == 'bar' else 1.033))) / (route[i]['specific_gravity']*1000) * (10197 if config.pressure_selection == 'bar' else 10000)  + static_head
                    NPSHa = (route[i]['P_in'] - (route[i]['vapor_pressure'] - (1.01325 if config.pressure_selection == 'bar' else 1.033 if config.pressure_selection == 'kg/cm2' else 10.1325))) / (route[i]['specific_gravity'] * 1000) * (10197 if config.pressure_selection == 'bar' else 10000 if config.pressure_selection == 'kg/cm2' else 101970) + static_head
                    route[i]['NPSHa'] = NPSHa
                    # route[i]['differential_head'] = route[i]['differential_pressure'] * (10.197 if config.pressure_selection == 'bar' else 10.000) / route[i]['specific_gravity']
                    route[i]['differential_head'] = route[i]['differential_pressure'] * (10.197 if config.pressure_selection == 'bar' else 10.000 if config.pressure_selection == 'kg/cm2' else 101.97) / route[i]['specific_gravity']

                    route[i]['capacity'] =  route[i-1]['flowrate']
                # print (route[i])       
    return grouped_routes   
                   
def cal_static_head (routes):
    caled_staticP_and_deltaP_lines =[]
    for route in routes :
        for i, target in enumerate(route) :
            if route[i]['type'] == "liquid_line" : # 여기서 line의 Static head 계산됨.
                route[i]['EL_in'] =  route[i-1]['elevation']
                route[i]['EL_out'] =  route[i+1]['elevation']
                # route[i]['static_pressure'] = (route[i+1]['elevation'] - route[i-1]['elevation']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000) # p=ρh/10,000
                route[i]['static_pressure'] = (route[i+1]['elevation'] - route[i-1]['elevation']) * route[i]['density'] / (10197 if config.pressure_selection == 'bar' else 10000 if config.pressure_selection == 'kg/cm2' else 101970)
                
                flowrate = route[i]['flowrate']
                density = route[i]['density']
                viscosity = route[i]['viscosity']
                pipe_size_ID = route[i]['pipe_size_ID']                
                roughness = route[i]['roughness']
                equivalent_length = route[i]['equivalent_length']                        
              
                # print (route[i])
                # pressure_loss_kg_cm2, velocity, reynolds_number
                route[i]['delta_P'], route[i]['velocity'], route[i]['reynolds'] = liquid_pressure_loss(flowrate, density, viscosity, pipe_size_ID, roughness, equivalent_length)
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
    seen_pairs = set()  # (tag, id) 쌍 저장
    # pressure_selection에 따라 단위 설정
    # unit = {
    #     'pressure': 'bar' if config.pressure_selection == 'bar' else 'kg/cm2',
    #     'gauge': 'bar.g' if config.pressure_selection == 'bar' else 'kg/cm2.g',
    #     'absolute': 'bar.A' if config.pressure_selection == 'bar' else 'kg/cm2.A'
    # }
    unit = {
        'pressure': (
            'bar' if config.pressure_selection == 'bar' else
            'MPa' if config.pressure_selection == 'MPa' else
            'kg/cm2'
        ),
        'gauge': (
            'bar.g' if config.pressure_selection == 'bar' else
            'MPa.g' if config.pressure_selection == 'MPa' else
            'kg/cm2.g'
        ),
        'absolute': (
            'bar.A' if config.pressure_selection == 'bar' else
            'MPa.A' if config.pressure_selection == 'MPa' else
            'kg/cm2.A'
        )
    }
       
    for routes in final_grouped_routes:
        for route in routes:
            for obj in route:
                if obj['type'] in ["variable_pump", "fixed_pump"]:
                    tag = obj.get('A_tag_no')
                    pump_id = obj.get('ID')  # id도 함께 고려
                    if (tag, pump_id) not in seen_pairs:
                        seen_pairs.add((tag, pump_id))
                        # seen_tags.add(tag)
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
                if item['type'] in ["liquid_line", "vapor_line", "two_phase_line", "user_line"] :
                    temp.append(f'[{item["A_tag_no"]}]')    
                else :    
                    # temp.append(item['A_tag_no'])
                    pass
                if i == len(loop)-1 : #end
                    deviation = item['P_in'] - item['P_out']
                    # temp.append(f"deviation : {deviation:.3f} [{'bar' if config.pressure_selection == 'bar' else 'kg/cm2'}]")
                    temp.append(f"deviation : {deviation:.3f} " f"[{'bar' if config.pressure_selection == 'bar' else 'MPa' if config.pressure_selection == 'MPa' else 'kg/cm2'}]")
                   
            temp_join = f"     " + " \u2192 ".join(str(item) for item in temp) # 오른쪽 화살표
            temp_text += temp_join +"\n"
    return temp_text        