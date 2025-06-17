def stream_mapping(only_lines, pressure_selection='kg/cm2'):
    # 압력 단위 설정
    unit = 'bar' if pressure_selection == 'bar' else 'kg/cm2'
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
        'roughness [ft]',
        'equiv. length [m]',
        'reynolds num [-]',
        'velocity [m/sec]',
        f'static head [{unit}]',
        f'inlet press. [{unit_g}]',
        f'outlet press. [{unit_g}]',
        f'press. drop [{unit}]',
        f'ΔP [{unit_100m}]'
    ]

    key_map = {
        'phase': 'phase',
        'line size [inch]': 'pipe_size_ID',
        'mass flowrate [kg/hr]': 'flowrate',
        'volume flowrate [m3/hr]': 'vol_flowrate',
        'density [kg/m3]': 'density',
        'temperature [deg.C]': lambda r: 20,
        'viscosity [cP]': 'viscosity',
        'roughness [ft]': lambda r: r['roughness'],
        'equiv. length [m]': 'equivalent_length',
        'reynolds num [-]': 'reynolds',
        'velocity [m/sec]': 'velocity',
        f'static head [{unit}]': 'static_pressure',
        f'inlet press. [{unit_g}]': 'P_in',
        f'outlet press. [{unit_g}]': 'P_out',
        f'press. drop [{unit}]': 'pressure_drop',
        f'ΔP [{unit_100m}]': 'pressure_drop_100m',
    }

    round_map = {
        'line size [inch]': 3,
        'mass flowrate [kg/hr]': 1,
        'volume flowrate [m3/hr]': 0,
        'density [kg/m3]': 3,
        'temperature [deg.C]': 1,
        'viscosity [cP]': 3,
        'roughness [ft]': 5,
        'equiv. length [m]': 1,
        'reynolds num [-]': 0,
        'velocity [m/sec]': 2,
        f'static head [{unit}]': 2,
        f'inlet press. [{unit_g}]': 2,
        f'outlet press. [{unit_g}]': 2,
        f'press. drop [{unit}]': 2,
        f'ΔP [{unit_100m}]': 2,
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
    # 기존 정보
    index = [
        # 'stream no',
        'inlet P',
        'outlet P',
        'ΔP [kg/cm2]'
    ]

    # 키 매핑 (혹은 함수 매핑)
    key_map = {
        # 'stream no' : 'A_tag_no',
        'inlet P': 'P_in',
        'outlet P': 'P_out',
        'ΔP [kg/cm2]': 'pressure_drop',
    }

    # 소수점 자리수 매핑
    round_map = {
        'inlet P': 2,
        'outlet P': 2,
        'ΔP [kg/cm2]': 2,
    }

    # 결과 생성
    data = {}
    for object_valve in only_valves:
        tag = object_valve["A_tag_no"]
        row = []

        for key in index:
            source = key_map[key]
            value = source(object_valve) if callable(source) else object_valve.get(source, "")
            if isinstance(value, (int, float)):
                value = round(value, round_map.get(key, 2))  # 각 키에 대해 지정된 소수점 자리수로 반올림
            row.append(value)

        data[tag] = row
    return data
