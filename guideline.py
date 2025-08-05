# Guide Spec 기반 기본 기준 추천값
default_criteria_by_phase = {
    "liquid": {
        "velocity_min": 0.3,
        "velocity_max": 3.0,     # 일반적으로 1.0~3.0 m/s 범위
        "dp_min": 0.3,
        "dp_max": 0.6            # kg/cm²/100m 기준 환산
    },
    "vapor": {
        "velocity_min": 10.0,
        "velocity_max": 30.0,    # Hydrocarbon vapor 기준
        "dp_min": 2.0,
        "dp_max": 5.0
    },
    "2 phase": {
        "velocity_min": 10.0,
        "velocity_max": 25.0,    # Reboiler return 등 기준
        "dp_min": 0.8,
        "dp_max": 1.5
    },
    "steam": {
        "velocity_min": 20.0,
        "velocity_max": 50.0,    # Saturated/superheated steam 기준
        "dp_min": 1.0,
        "dp_max": 3.0
    },
    "water": {
        "velocity_min": 1.0,
        "velocity_max": 3.0,     # Return to pump 기준
        "dp_min": 0.3,
        "dp_max": 0.6
    }
}
