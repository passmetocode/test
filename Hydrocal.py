# -*- coding: utf-8 -*-

import sys
import os, io, subprocess
import hydro.main_sequence as main_sequence, config, usb_auth

# 표준 출력에 UTF-8 인코딩 강제 설정 얼변
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
   
def run_calculation():
    # 기존 계산 로직 수행
    config.file_path = sys.argv[1].strip('"')
    config.current_page = sys.argv[2]
    config.device_usb = sys.argv[3]


    if not os.path.exists(config.file_path):
        print(f"❌ 파일 없음: {config.file_path}")
        sys.exit(1)
    if config.device_usb == usb_auth.generate_daily_token():  # '2025-09-09' 형식
        print(config.device_usb)
    print(config.device_usb)    
    #     # USB가 연결되어 있는지 확인
    #     if not any(config.device_usb.lower() in dev for dev in usb_devices):
    #         print(f"❌ Unauthorized user: no usb")
    #         sys.exit(1)
    
    try:
        main_sequence.calculation_sequence(config.file_path, running_status)
    except Exception as e:
        print(f"⚠️ 예외 발생: {e}")
        sys.exit(1)
    return

class MessageAccumulator:
    def __init__(self):
        self.messages = []

    def add_message(self, message: str):
        self.messages.append(message)

    def get_combined_message(self) -> str:
        return ''.join(self.messages)

    def clear_messages(self):
        self.messages = []

if __name__ == "__main__":
    # ✅ JS에서 USB 확인 용도로 호출한 경우
    if '--usb-check' in sys.argv:
        usb_auth.main_exec()
    else:
        running_status = MessageAccumulator()
        run_calculation()

    
# 실행경로 위치에 잘 맞추고, 파일을 불러들이는 코드
# python hydrocal.py "C:\Dev\Hydrocal\hydro_template.hydro" hydro ip

# pyinstaller --onefile --noconsole hydrocal.py
# pyinstaller --onedir --noconsole hydrocal.py
# pyinstaller hydrocal.spec
# pyinstaller --onefile edit_stream_data.py
# npx electron-builder --win portable
# npm run dist
# drawio의 plugin 부분을 미리 적어둔거임. 잊지 말라고.
# Draw.loadPlugin(function(ui) {
  
