import os, sys
import json
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import ntplib
from time import ctime
import subprocess
import config  # config.py 파일이 같은 폴더에 있어야 함


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
        import ntplib
        from time import ctime

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

import tkinter.messagebox as msgbox
import psutil

def show_warning_and_terminate():
    msgbox.showwarning("⚠️ Unauthorized Access", 
        "This session will be terminated due to missing or expired USB Key.\n"
        "Please check your USB security device and restart the application.")

    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            print (proc.info['name'].lower())
            if 'hydro' or 'electron' in proc.info['name'].lower():
                print(f"Killing {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def determine_user_status():
    # 0단계: USB 인지 UUID 인지 확인
    if config.device_usb is not None : # usb 설치 사용자
        config.keyfile_type = 'usb'
        if not is_usb_serial_connected(config.device_usb):
            config.user = 'no_usb'
            # show_warning_and_terminate()
            return
        
    # 3단계: 날짜 확인
    try:
        if config.current_date < config.start_date or config.current_date > config.expired_date:
            config.user = 'expired_user'
            show_warning_and_terminate()
        else:
            config.user = 'normal_user'

    except Exception:
        config.user = 'abnormal_user'
        # show_warning_and_terminate()

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
    
    