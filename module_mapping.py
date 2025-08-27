def stream_mapping(only_lines, pressure_selection='kg/cm2'):
    # 압력 단위 설정
    # unit = 'bar' if pressure_selection == 'bar' else 'kg/cm2'
    unit = 'bar' if pressure_selection == 'bar' else 'MPa' if pressure_selection == 'MPa' else 'kg/cm2'
    unit_g = f'{unit}.g'
    unit_A = f'{unit}.A'
    unit_100m = f'{unit}/100m'

    # 기존 정보 (단위는 나중에 바뀜)
    index = [
        'phase',
        'line size [inch]',
        'mass flowrate [kg/hr]',
        'volume flowrate [m3/hr]',
        'density [kg/m3]',
        'temperature [deg.C]',
        'viscosity [cP]',
        'roughness [mm]',
        'straight length [m]',  # 추가된 항목
        'equiv. length [m]',
        'reynolds num [-]',
        f'inlet press. [{unit_g}]',
        f'static loss [{unit}]',
        f'pipe loss [{unit}]',
        f'outlet press. [{unit_g}]',
        'velocity [m/sec]',
        f'ΔP [{unit_100m}]',
        'criteria'  # 추가
    ]

    key_map = {
        'phase': 'phase',
        'line size [inch]': 'pipe_size_ID',
        'mass flowrate [kg/hr]': 'flowrate',
        'volume flowrate [m3/hr]': 'vol_flowrate',
        'density [kg/m3]': 'density',
        'temperature [deg.C]': lambda r: r['temperature'] if r.get('temperature') else '-',
        'viscosity [cP]': 'viscosity',
        'roughness [mm]': lambda r: float(r['roughness']) * 1000 if r.get('roughness') else '',
        'straight length [m]': 'straight_length',        
        'equiv. length [m]': 'equivalent_length',
        'reynolds num [-]': 'reynolds',
        f'inlet press. [{unit_g}]': 'P_in',
        f'static loss [{unit}]': 'static_pressure',
        f'pipe loss [{unit}]': 'pressure_drop',
        f'outlet press. [{unit_g}]': 'P_out',
        'velocity [m/sec]': 'velocity',
        f'ΔP [{unit_100m}]': 'pressure_drop_100m',
        'criteria' : 'criteria',  # 추가
    }

    round_map = {
        'line size [inch]': 3,
        'mass flowrate [kg/hr]': 1,
        'volume flowrate [m3/hr]': 0,
        'density [kg/m3]': 3,
        'temperature [deg.C]': 1,
        'viscosity [cP]': 3,
        'roughness [mm]': 5,
        'straight length [m]': 1,
        'equiv. length [m]': 1,
        'reynolds num [-]': 0,
        f'inlet press. [{unit_g}]': 3,
        f'static loss [{unit}]': 3,
        f'pipe loss [{unit}]': 3,
        f'outlet press. [{unit_g}]': 3,
        'velocity [m/sec]': 2,        
        f'ΔP [{unit_100m}]': 3,
      }

    data = {}
    for object_line in only_lines:
        tag = int(object_line["A_tag_no"])
        row = []

        for key in index:
            source = key_map[key]
            value = source(object_line) if callable(source) else object_line.get(source, "")
            if isinstance(value, (int, float)):
                value = round(value, round_map.get(key, 2))
            row.append(value)

        data[tag] = row
    return data


def valve_mapping(only_valves):
    index = [
        'inlet P',
        'outlet P',
        'ΔP [kg/cm2]'
    ]

    key_map = {
        'inlet P': 'P_in',
        'outlet P': 'P_out',
        'ΔP [kg/cm2]': 'pressure_drop',
    }

    round_map = {
        'inlet P': 2,
        'outlet P': 2,
        'ΔP [kg/cm2]': 2,
    }

    data = {}
    tag_count = {}  # 태그 중복 횟수 기록

    for object_valve in only_valves:
        base_tag = object_valve["A_tag_no"]
        count = tag_count.get(base_tag, 0)
        tag_count[base_tag] = count + 1

        # 공백 추가
        tag = base_tag + (" " * count)

        row = []
        for key in index:
            source = key_map[key]
            value = source(object_valve) if callable(source) else object_valve.get(source, "")
            if isinstance(value, (int, float)):
                value = round(value, round_map.get(key, 2))
            row.append(value)

        data[tag] = row

    return data

