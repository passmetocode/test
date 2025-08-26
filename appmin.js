// window.checkUsbKeyQuick = function () {
//     window.electronAPI.checkUsbKey().then((result) => {
//         const userType = typeof result === 'object' ? result.user : result;
//         switch (userType) {
//             case "no_usb": // ❌ USB 키 없음 → 차단
//                 ui.isLicensed = false;
//                 blockEditor(
//                     "🔌 No USB key detected. Please insert the correct USB key to continue. <br><br>🔌 USB 키가 감지되지 않았습니다. 계속하려면 올바른 USB 키를 삽입하세요.",
//                     function () { ui.initCustomTimeLimit?.();  // ⏱️ 시간 제한 시작
//                     }
//                 );
//                 break;           
//         }
//     } ,1000);
// };
window.checkUsbKeyQuick = function (retryCount = 3, delay = 1000) {
    let attempts = 0;

    function tryCheck() {
        window.electronAPI.checkUsbKey().then((result) => {
            const userType = typeof result === 'object' ? result.user : result;
            if (userType === "no_usb" && attempts < retryCount) {
                attempts++;
                setTimeout(tryCheck, delay); // 재시도
            } else if (userType === "no_usb") {
                ui.isLicensed = false;
                blockEditor(
                    "🔌 No USB key detected. Please insert the correct USB key to continue.<br><br>🔌 USB 키가 감지되지 않았습니다. 계속하려면 올바른 USB 키를 삽입하세요.",
                    function () {
                        ui.initCustomTimeLimit?.();
                    }
                );
            }
        });
    }

    setTimeout(tryCheck, delay); // 첫 시도
};
// 공통 함수: Calculation 동작 처리 hydro_yangs
