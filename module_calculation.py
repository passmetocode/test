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
    pressure_loss_kg_cm2 =  friction_factor * (pipe_length / pipe_diameter) * (velocity**2 / (2*9.806) ) * (fluid_density/10000)
    pressure_loss_bar = pressure_loss_kg_cm2 * 0.980665  # Convert kg/cm² to bar
    return pressure_loss_bar if config.pressure_selection =='bar' else pressure_loss_kg_cm2, velocity, reynolds_number

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
    if config.pressure_selection == 'bar':
        P_in = P_in *1.01972 # Convert bar to kg/cm².g  bar로 입력한 경우.
    p1 = P_in
    # Convert flow rate from kg/h to kg/s
    flow_rate = flow_rate / 3600   
    p1 = (p1 + 1.03323) * 98.0665 # kg/cm2.g를 환산 kPa   
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
    p2_bar = p2_kg_cm2 * 0.980665  # Convert kg/cm² to bar
    if config.pressure_selection == 'bar':
        pressure_loss_bar = P_in - p2_bar
    else:
        pressure_loss_kg_cm2 = P_in - p2_kg_cm2
    # pressure_loss_bar = pressure_loss_kg_cm2 * 0.980665  # Convert kg/cm² to bar
    return pressure_loss_bar if config.pressure_selection =='bar' else pressure_loss_kg_cm2, fluid_density, velocity, reynolds_number, P_in, Ma1, p2_bar if config.pressure_selection =='bar' else p2_kg_cm2, Ma2
    
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
        P_out = P_out *1.01972 # Convert bar to kg/cm².g  bar로 입력한 경우.
    # Convert flow rate from kg/h to kg/s
    p2 = P_out
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
    p1_bar = p1_kg_cm2 * 0.980665  # Convert kg/cm² to bar
    if config.pressure_selection == 'bar':
        pressure_loss_bar = p1_bar - P_out
    else:
        pressure_loss_kg_cm2 = p1_kg_cm2 - P_out
    # pressure_loss_bar = pressure_loss_kg_cm2 * 0.980665  # Convert kg/cm² to bar
    return pressure_loss_bar if config.pressure_selection =='bar' else pressure_loss_kg_cm2, fluid_density, velocity, reynolds_number, p1_bar if config.pressure_selection =='bar' else p1_kg_cm2, Ma1, P_out, Ma2

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
    pressure_loss_bar = pressure_loss_kg_cm2 * 0.980665  # Convert kg/cm² to bar    
    return pressure_loss_bar if config.pressure_selection =='bar' else pressure_loss_kg_cm2, fluid_density, velocity, reynolds_number

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
