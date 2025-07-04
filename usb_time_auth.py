import ntplib
import json
from datetime import datetime
from time import ctime
import os
import subprocess
import config  # config.py 파일이 같은 폴더에 있어야 함

def update_time_info():
    previous_ntp_date = None
    previous_ntp_time = None
    if os.path.exists("date.json"):
        try:
            with open("date.json", "r", encoding="utf-8") as f:
                previous_data = json.load(f)
                previous_ntp_date = previous_data.get("NTP_date")
                previous_ntp_time = previous_data.get("NTP_time")
        except Exception as e:
            print("이전 date.json 파일을 읽는 중 오류 발생:", e)

    data = {
        "NTP_date": previous_ntp_date,
        "NTP_time": previous_ntp_time,
        "Local_date": None,
        "Local_time": None
    }

    local_dt = datetime.now()
    data["Local_date"] = local_dt.strftime("%Y-%m-%d")
    data["Local_time"] = local_dt.strftime("%H:%M:%S")

    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org', version=3)
        ntp_time = ctime(response.tx_time)
        ntp_dt = datetime.strptime(ntp_time, "%a %b %d %H:%M:%S %Y")
        data["NTP_date"] = ntp_dt.strftime("%Y-%m-%d")
        data["NTP_time"] = ntp_dt.strftime("%H:%M:%S")
    except Exception as e:
        print("NTP 시각을 가져오지 못했습니다:", e)

    with open("date.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return data

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

def determine_user_status(time_data):
    if not is_usb_serial_connected(config.usb_key):
        config.user = 'guest'
        return

    ntp_date = time_data.get("NTP_date")
    local_date = time_data.get("Local_date")

    if ntp_date != local_date:
        config.user = 'abnormal_user'
        return

    try:
        ntp_dt = datetime.strptime(ntp_date, "%Y-%m-%d").date()        
        local_dt = datetime.strptime(local_date, "%Y-%m-%d").date()
        start_dt = datetime.strptime(config.start_date, "%Y-%m-%d").date()
        expired_dt = datetime.strptime(config.expired_date, "%Y-%m-%d").date()

        if ntp_dt < start_dt or abs((ntp_dt - local_dt).total_seconds()) >= 48 * 3600:
            config.user = 'abnormal_user'
        elif ntp_dt > expired_dt:
            config.user = 'expired_user'
        else:
            config.user = 'normal_user'
    except Exception as e:
        print("날짜 비교 중 오류 발생:", e)
        config.user = 'abnormal_user'

def main_exec():
    time_data = update_time_info()
    determine_user_status(time_data)
    print(config.user)

# if __name__ == "__main__":
#     main()
