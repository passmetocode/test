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

def keyfile_info() -> bool:
    date_json_path = get_date_json_path()
    if os.path.exists(date_json_path):
        try:
            with open(date_json_path, "r", encoding="utf-8") as f:
                key_data = json.load(f)
                config.device_usb = key_data.get("device_usb")
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

def is_usb_serial_connected(target_serial: str) -> bool:
    try:
        result = subprocess.check_output(
            'wmic path Win32_USBHub get DeviceID',
            shell=True
        )
        lines = result.decode(errors='ignore').splitlines()
        for line in lines:
            if target_serial.lower() in line.strip().lower():
                return True
        return False
    except Exception:
        return False

# def get_current_volume_name() -> str | None:
#     drive_letter = os.path.splitdrive(BASE_DIR)[0].replace(":", "")
#     try:
#         result = subprocess.check_output(
#             'wmic logicaldisk get DeviceID, VolumeName',
#             shell=True
#         ).decode(errors='ignore')

#         for line in result.splitlines():
#             if line.strip().startswith(drive_letter + ":"):
#                 parts = line.strip().split()
#                 if len(parts) >= 2:
#                     return parts[1]
#     except Exception as e:
#         # print("볼륨 이름 조회 실패:", e)
#         config.user = 'abnormal_user'
#     return None

def determine_user_status():
    # 0단계: USB 인지 UUID 인지 확인
    if config.device_usb is not None and config.device_uuid is None: # usb 설치 사용자
        config.keyfile_type = 'usb'
        if not is_usb_serial_connected(config.device_usb):
            config.user = 'no_usb'
            return
        # # 2단계: 실행 드라이브 볼륨 이름 확인
        # current_volume = get_current_volume_name()
        # if current_volume is None or current_volume.strip().lower() != config.user_name : # "hydro" 대신 usb volume을 user name 으로 재활용 
        #     config.user = 'not_usb_location'
        #     return
        
    elif config.device_usb is None and config.device_uuid is not None: # uuid 설치 사용자
        config.keyfile_type = 'uuid' 
        # 1단계: UUID 확인
        current_uuid = get_windows_uuid()
        if current_uuid is None or current_uuid.strip().lower() != config.device_uuid.strip().lower():
            if current_uuid and current_uuid.strip().lower() == 'guest':
                config.user = 'guest'
            else:
                config.user = 'no_device_match'
            return
    elif config.device_usb is not None and config.device_uuid is not None: # usb uuid 모두 설치 사용자
        config.keyfile_type = 'usb'
        if not is_usb_serial_connected(config.device_usb):
            config.user = 'no_usb'
            return
        # # 2단계: 실행 드라이브 볼륨 이름 확인
        # current_volume = get_current_volume_name()
        # print(current_volume, config.user_name)
        # if current_volume is None or current_volume.strip().lower() != config.user_name : # "hydro" 대신 usb volume을 user name 으로 재활용 
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
            "keyfile_type": config.keyfile_type,
            "user": config.user,
            "start_date": config.start_date.strftime("%Y-%m-%d"),
            "expired_date": config.expired_date.strftime("%Y-%m-%d"),
            "current_date": config.current_date.strftime("%Y-%m-%d"),
            "uuid": current_uuid
        }
    else:
        return {
            "keyfile_type": config.keyfile_type,            
            "user": config.user,
            "uuid": current_uuid
        }

def main_exec():
    if keyfile_info():
        determine_user_status()
        user_payload = get_user_status_payload()
        print(json.dumps(user_payload))
    else:
        print(json.dumps({"user": "no_wifi"}))
# main_exec()
    
    