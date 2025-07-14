import ntplib
import json
from datetime import datetime
from time import ctime
import os, sys
import subprocess
import config  # config.py 파일이 같은 폴더에 있어야 함

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_date_json_path():
    return os.path.join(BASE_DIR, "keyfile.json")

def key_info() -> bool:
    date_json_path = get_date_json_path()
    if os.path.exists(date_json_path):
        try:
            with open(date_json_path, "r", encoding="utf-8") as f:
                key_data = json.load(f)
                config.device_uuid = key_data.get("device_uuid")
                config.start_date = datetime.strptime(key_data.get("start_date"), "%Y-%m-%d").date()
                config.expired_date = datetime.strptime(key_data.get("expired_date"), "%Y-%m-%d").date()
        except Exception:
            config.user = 'abnormal_user'
            return False
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org', version=3)
        ntp_time = ctime(response.tx_time)
        ntp_dt = datetime.strptime(ntp_time, "%a %b %d %H:%M:%S %Y")
        config.current_date = ntp_dt.date()
        config.current_time = ntp_dt.strftime("%H:%M:%S")
    except Exception:
        config.user = 'no_wifi'
        return False
    return True

def get_windows_uuid() -> str | None:
    try:
        result = subprocess.check_output(
            'wmic csproduct get UUID',
            shell=True
        ).decode(errors='ignore').splitlines()
        uuid_lines = [line.strip() for line in result if line.strip() and "UUID" not in line]
        if uuid_lines:
            return uuid_lines[0]
    except Exception:
        pass
    return None

def determine_user_status():
    # 1단계: UUID 확인
    current_uuid = get_windows_uuid()
    if current_uuid is None or current_uuid.strip().lower() != config.device_uuid.strip().lower():
        if current_uuid and current_uuid.strip().lower() == 'guest':
            config.user = 'guest'
        else:
            config.user = 'no_device_match'
        return

    # # 2단계: 실행 드라이브 볼륨 이름 확인
    # current_volume = get_current_volume_name()
    # if current_volume is None or current_volume.strip().lower() != config.user_name.strip().lower():
    #     config.user = 'not_usb_location'
    #     return

    # 3단계: 날짜 확인
    try:
        if config.current_date < config.start_date or config.current_date > config.expired_date:
            config.user = 'expired_user'
        else:
            config.user = 'normal_user'
    except Exception:
        config.user = 'abnormal_user'

def get_user_status_payload():
    current_uuid = get_windows_uuid()
    # config.user = 'normal_user' # 임시로 설정, 무저건 통과
    if config.user == 'normal_user':
        return {
            "user": config.user,
            "start_date": config.start_date.strftime("%Y-%m-%d"),
            "expired_date": config.expired_date.strftime("%Y-%m-%d"),
            "current_date": config.current_date.strftime("%Y-%m-%d"),
            "uuid": current_uuid
        }
    else:
        return {
            "user": config.user,
            "uuid": current_uuid
        }

def main_exec():
    if key_info():
        determine_user_status()
        user_payload = get_user_status_payload()
        print(json.dumps(user_payload))
    else:
        print(json.dumps({"user": "no_wifi"}))
