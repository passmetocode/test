import os, sys
import json
import base64
from datetime import datetime
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

def get_ntp_date_smart():
    local_date = datetime.now().date()

    # 캐시 확인
    cached_date = None
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            cached_date = datetime.strptime(cache.get("last_ntp_date"), "%Y-%m-%d").date()
        except:
            pass

    # 날짜가 다르면 무조건 NTP 요청
    if cached_date != local_date:
        try:
            client = ntplib.NTPClient()
            response = client.request('pool.ntp.org', version=3, timeout=1.5)
            ntp_date = datetime.fromtimestamp(response.tx_time).date()

            # 캐시 갱신
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"last_ntp_date": ntp_date.strftime("%Y-%m-%d")}, f)

            return ntp_date
        except:
            return None

    # 날짜가 같으면 1/10 확률로 NTP 요청
    if random.randint(1, 5) == 1:
        try:
            client = ntplib.NTPClient()
            response = client.request('pool.ntp.org', version=3, timeout=1.5)
            ntp_date = datetime.fromtimestamp(response.tx_time).date()

            # 캐시 갱신
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"last_ntp_date": ntp_date.strftime("%Y-%m-%d")}, f)

            return ntp_date
        except:
            return None

    # 캐시된 날짜 사용
    return cached_date


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
        # client = ntplib.NTPClient()
        # response = client.request('pool.ntp.org', version=3)
        # ntp_time = ctime(response.tx_time)
        # ntp_dt = datetime.strptime(ntp_time, "%a %b %d %H:%M:%S %Y")
        # config.current_date = ntp_dt.date()
        # config.current_time = ntp_dt.strftime("%H:%M:%S")
        
        config.current_date = get_ntp_date_smart()
    except Exception:
        config.user = 'no_wifi'
        return False

    return True

# def is_usb_serial_connected(target_serial: str) -> bool:
#     try:
#         result = subprocess.check_output(
#             'wmic path Win32_USBHub get DeviceID',
#             shell=True
#         )
#         lines = result.decode(errors='ignore').splitlines()
#         for line in lines:
#             if target_serial.lower() in line.strip().lower():
#                 return True
#         return False
#     except Exception:
#         return False
# import subprocess


# def is_running_from_target_usb(target_serial: str) -> bool:
#     exe_path = os.path.abspath(sys.argv[0])
#     drive_letter = os.path.splitdrive(exe_path)[0] + "\\"

#     try:
#         drive_type = win32file.GetDriveType(drive_letter)
#         if drive_type != win32file.DRIVE_REMOVABLE:
#             return False
#         # 연결된 USB 장치 목록 확인
#         result = subprocess.check_output(
#             'wmic path Win32_USBHub get DeviceID',
#             shell=True
#         ).decode(errors='ignore').splitlines()

#         for line in result:
#             if target_serial.lower() in line.strip().lower():
#                 return True
#     except Exception:
#         pass

#     return False

## USB 연결 상태 확인 
def is_usb_serial_connected(target_serial: str) -> bool:
    try:
        # PowerShell 명령어 실행
        cmd = [
            'powershell',
            '-Command',
            'Get-WmiObject Win32_USBHub | Select-Object -ExpandProperty DeviceID'
        ]
        result = subprocess.check_output(cmd, shell=True)
        lines = result.decode(errors='ignore').splitlines()

        # 시리얼 번호 비교
        for line in lines:
            if target_serial.lower() in line.strip().lower():
                return True
        return False
    except Exception as e:
        print(f"[USB 체크 오류] {e}")
        return False

# USB에서 실행 중인지 확인
def is_running_from_target_usb(target_serial: str) -> bool:
    exe_path = os.path.abspath(sys.argv[0])
    drive_letter = os.path.splitdrive(exe_path)[0] + "\\"

    try:
        # 실행 드라이브가 USB인지 확인
        drive_type = win32file.GetDriveType(drive_letter)
        if drive_type != win32file.DRIVE_REMOVABLE:
            return False

        # PowerShell로 USB 시리얼 확인
        cmd = [
            'powershell',
            '-Command',
            'Get-WmiObject Win32_USBHub | Select-Object -ExpandProperty DeviceID'
        ]
        result = subprocess.check_output(cmd, shell=True)
        lines = result.decode(errors='ignore').splitlines()

        for line in lines:
            if target_serial.lower() in line.strip().lower():
                return True
    except Exception as e:
        print(f"[USB 실행 체크 오류] {e}")

    return False

def show_warning_and_terminate(reason: str):
    messages = {
        "no_usb": "USB 보안 장치가 연결되어 있지 않습니다.\nUSB를 연결한 후 다시 실행해주세요.",
        "wrong_drive": "프로그램이 등록된 USB 장치에서 실행되지 않았습니다.\nUSB에서 직접 실행해주세요.",
        "expired_user": "사용 기간이 만료되었습니다.\n관리자에게 문의해주세요.",
        "abnormal_user": "인증 정보를 확인할 수 없습니다.\nkeyfile이 손상되었거나 잘못된 환경입니다.",
        "no_wifi": "인터넷 연결이 필요합니다.\n네트워크 상태를 확인해주세요."
    }

    msg = messages.get(reason, "알 수 없는 오류로 인해 프로그램을 종료합니다.")
    msgbox.showwarning("⚠️ Unauthorized Access", msg)

    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if 'hydro' in proc.info['name'].lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        

# .py로 실행 중이면 개발 모드, .exe로 실행 중이면 배포 모드
DEVELOPMENT_MODE = not getattr(sys, 'frozen', False)

def determine_user_status():
    if config.device_usb is not None:
        config.keyfile_type = 'usb'
        if not is_usb_serial_connected(config.device_usb):
            config.user = 'no_usb'
            show_warning_and_terminate("no_usb")
            return
        if not is_running_from_target_usb(config.device_usb) and not DEVELOPMENT_MODE:
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



def get_user_status_payload():
    if config.user == 'normal_user':
        return {
            "keyfile_type": config.keyfile_type,
            "user": config.user,
            "start_date": config.start_date.strftime("%Y-%m-%d"),
            "expired_date": config.expired_date.strftime("%Y-%m-%d"),
            "current_date": config.current_date.strftime("%Y-%m-%d")
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
    
    