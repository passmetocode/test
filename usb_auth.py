import os, sys
import json
import base64
from datetime import datetime
# import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import random
import ntplib
from time import ctime
import subprocess
import config  # config.py 파일이 같은 폴더에 있어야 함
import tkinter.messagebox as msgbox
import psutil
import win32file
import hashlib

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 비밀번호와 파일 경로
PASSWORD = "happy4ever@hydro.world"
ENC_KEYFILE_PATH = os.path.join(BASE_DIR, "keyfile.enc")  # 합본 파일


def derive_key(password: str, salt: bytes) -> bytes:
    """PBKDF2로 키 생성"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=120000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def decrypt_keyfile():
    """
    keyfile.enc 파일 복호화 후 JSON 딕셔너리 반환
    파일 구조: [salt 16B] + [암호문]
    """
    if not os.path.exists(ENC_KEYFILE_PATH):
        return None

    with open(ENC_KEYFILE_PATH, "rb") as f:
        data = f.read()

    if len(data) < 17:
        return None  # 최소 salt+암호문 구조 미달

    salt = data[:16]
    token = data[16:]

    key = derive_key(PASSWORD, salt)
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(token).decode("utf-8")
    return json.loads(decrypted_data)

CACHE_FILE = os.path.join(BASE_DIR, "ntp_cache.json")

def keyfile_info() -> bool:
    # 1) keyfile 복호화 및 config 세팅
    try:
        key_data = decrypt_keyfile()
        if not key_data:
            config.user = 'abnormal_user'
            return False

        config.device_usb = key_data.get("device_usb")
        # config.device_uuid = key_data.get("device_uuid")
        config.start_date = datetime.strptime(key_data.get("start_date"), "%Y-%m-%d").date()
        config.expired_date = datetime.strptime(key_data.get("expired_date"), "%Y-%m-%d").date()
    except Exception:
        config.user = 'abnormal_user'
        return False

    # 2) NTP 시간 받아서 config 세팅
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org', version=3)
        ntp_time = ctime(response.tx_time)
        ntp_dt = datetime.strptime(ntp_time, "%a %b %d %H:%M:%S %Y")
        config.current_date = ntp_dt.date()
        # config.current_time = ntp_dt.strftime("%H:%M:%S")
        
        # config.current_date = get_ntp_date_smart()
    except Exception:
        config.user = 'no_wifi'
        return False

    return True

## USB 연결 상태 확인 
# def is_usb_serial_connected(target_serial: str) -> bool:
#     try:
#         # PowerShell 명령어 실행
#         cmd = [
#             'powershell',
#             '-Command',
#             'Get-WmiObject Win32_USBHub | Select-Object -ExpandProperty DeviceID'
#         ]
#         result = subprocess.check_output(cmd, shell=True)
#         lines = result.decode(errors='ignore').splitlines()

#         # 시리얼 번호 비교
#         for line in lines:
#             if target_serial.lower() in line.strip().lower():
#                 return True
#         return False
#     except Exception as e:
#         print(f"[USB 체크 오류] {e}")
#         return False

def show_warning_and_terminate(reason: str):
    messages = {
        "no_usb": "USB 보안 장치가 연결되어 있지 않습니다.\nUSB를 연결한 후 다시 실행해주세요.",
        "wrong_drive": "프로그램이 등록된 USB 장치에서 실행되지 않았습니다.\nUSB에서 직접 실행해주세요.",
        "expired_user": "사용 기간이 만료되었습니다.\n관리자에게 문의해주세요.",
        "abnormal_user": "인증 정보를 확인할 수 없습니다.\nkeyfile이 손상되었거나 잘못된 환경입니다.",
        "no_wifi": "인터넷 연결이 필요합니다.\n네트워크 상태를 확인해주세요."
    }

    # 우선 프로세스 종료
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if 'hydro' in proc.info['name'].lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 종료 후 경고 메시지 띄우기
    msg = messages.get(reason, "알 수 없는 오류로 인해 프로그램을 종료합니다.")
    msgbox.showwarning("⚠️ Unauthorized Access", msg)

def get_usb_device_ids():
    """USB DeviceID 리스트 반환 (PowerShell 실행은 한 번만)"""
    try:
        cmd = [
            'powershell',
            '-Command',
            'Get-WmiObject Win32_USBHub | Select-Object -ExpandProperty DeviceID'
        ]
        result = subprocess.check_output(cmd, shell=True)
        return [line.strip().lower() for line in result.decode(errors='ignore').splitlines() if line.strip()]
    except Exception as e:
        print(f"[USB 리스트 가져오기 오류] {e}")
        return []

# # .py로 실행 중이면 개발 모드, .exe로 실행 중이면 배포 모드
DEVELOPMENT_MODE = not getattr(sys, 'frozen', False)
def determine_user_status():
    if config.device_usb is not None:
        config.keyfile_type = 'usb'
        # 개발모드일 때는 USB 검사 스킵
        if not DEVELOPMENT_MODE:
            usb_devices = get_usb_device_ids()

            # USB가 연결되어 있는지 확인
            if not any(config.device_usb.lower() in dev for dev in usb_devices):
                config.user = 'no_usb'
                show_warning_and_terminate("no_usb")
                return

            # 실행 드라이브가 USB인지 확인
            exe_path = os.path.abspath(sys.argv[0])
            drive_letter = os.path.splitdrive(exe_path)[0] + "\\"
            drive_type = win32file.GetDriveType(drive_letter)

            if drive_type != win32file.DRIVE_REMOVABLE:
                config.user = 'wrong_drive'
                show_warning_and_terminate("wrong_drive")
                return

            # 실행 중인 USB가 target_usb인지 확인
            if not any(config.device_usb.lower() in dev for dev in usb_devices):
                config.user = 'wrong_drive'
                show_warning_and_terminate("wrong_drive")
                return

    try:
        if config.current_date < config.start_date or config.current_date > config.expired_date:
            config.user = 'expired_user'
            show_warning_and_terminate("expired_user")
        else:
            config.user = 'normal_user'
    except Exception:
        config.user = 'abnormal_user'
        show_warning_and_terminate("abnormal_user")

def generate_daily_token():
    now = datetime.now()
    today = now.date()  # '2025-09-09' 형식
    raw = f"{today}"
    token = hashlib.sha256(raw.encode()).hexdigest()
    return token

def get_user_status_payload():
    if config.user == 'normal_user':

        return {
            "keyfile_type": config.keyfile_type,
            "user": config.user,
            "start_date": config.start_date.strftime("%Y-%m-%d"),
            "expired_date": config.expired_date.strftime("%Y-%m-%d"),
            "current_date": config.current_date.strftime("%Y-%m-%d"),
            "key_value" : generate_daily_token()
        }
    else:
        return {
            "keyfile_type": config.keyfile_type,
            "user": config.user
        }

def main_exec():
    if keyfile_info():
        determine_user_status()
        user_payload = get_user_status_payload()
        print(json.dumps(user_payload))
    else:
        print(json.dumps({"user": "no_wifi"}))
# main_exec()
    
    