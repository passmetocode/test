# -*- coding: utf-8 -*-

import sys
import os, io
import main_sequence, config

# 표준 출력에 UTF-8 인코딩 강제 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def validate_launch():
    if '--from-drawio' not in sys.argv:
        print("❌ 인증 실패: drawio에서 실행되지 않음")
        sys.exit(1)

    token_index = sys.argv.index('--from-drawio') + 1
    token = sys.argv[token_index] if token_index < len(sys.argv) else None

    if token != 'secure-token-123':
        print("❌ 인증 실패: 토큰 불일치")
        sys.exit(1)

    print("✅ 인증 성공")
    sys.exit(0)

def run_calculation():
    # 기존 계산 로직 수행
    config.file_path = sys.argv[1].strip('"')
    config.current_page = sys.argv[2]
    config.option = sys.argv[3]

    if not os.path.exists(config.file_path):
        print(f"❌ 파일 없음: {config.file_path}")
        sys.exit(1)

    main_sequence.calculation_sequence(config.file_path, running_status)

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
    if '--from-drawio' in sys.argv:
        validate_launch()
    else:
        running_status = MessageAccumulator()
        run_calculation()

    
# 실행경로 위치에 잘 맞추고, 파일을 불러들이는 코드
# python hydrocal.py "C:\Dev\Hydrocal\hydro_template.hydro" hydro ip

# pyinstaller --onefile --noconsole hydrocal.py

# drawio의 plugin 부분을 미리 적어둔거임. 잊지 말라고.
# Draw.loadPlugin(function(ui) {
  
#   // 1. 액션 정의
#   ui.actions.addAction('new_synchronize', function() {
#     var cc = ui.getCurrentFile();
    
#     // Python 파일 실행 (child_process 사용)
#     const { exec } = require('child_process');
#     const pythonPath = 'C:\\Users\\excel\\AppData\\Local\\Programs\\Python\\Python39\\python.exe';  // 여기 Python 경로 수정
#     const scriptPath = 'C:\\drawio-desktop\\hydro.py';
#     const drawioPath = 'C:\\drawio-desktop\\sample.drawio';

#     exec(`"${pythonPath}" "${scriptPath}" "${drawioPath}"`, (error, stdout, stderr) => {
#       if (error) {
#         alert(`❌ 실행 중 오류 발생: ${error.message}`);
#         return;
#       }
#       if (stderr) {
#         alert(`⚠️ 경고: ${stderr}`);
#         return;
#       }
#       alert(`🔄 Synchronize 실행 완료!\n결과: ${stdout}`);
#     });

#     // 기존 동기화 실행
#     ui.actions.get("synchronize").funct();
#   });

#   // 2. 메뉴에 추가
#   var menu = ui.menus.get('yangs');
#   var oldFunct = menu.funct;

#   menu.funct = function(menu, parent) {
#     oldFunct.apply(this, arguments);
#     ui.menus.addMenuItems(menu, ['-', 'new_synchronize'], parent);
#   };

# });





