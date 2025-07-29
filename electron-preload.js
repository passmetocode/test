const {
    contextBridge,
    ipcRenderer
} = require("electron");

let reqId = 1;
let reqInfo = {};
let fileChangedListeners = {};

ipcRenderer.on('mainResp', (event, resp) => 
{
	var callbacks = reqInfo[resp.reqId];
	
	if (resp.error)
	{
		callbacks.error(resp.msg, resp.e);
	}
	else
	{
		callbacks.callback(resp.data);
	}
	
	delete reqInfo[resp.reqId];
});

ipcRenderer.on('fileChanged', (event, resp) => 
{
	var listener = fileChangedListeners[resp.path];
	
	if (listener)
	{
		listener(resp.curr, resp.prev);
	}
});

contextBridge.exposeInMainWorld(
    'electron', {
        request: (msg, callback, error) => 
		{
			msg.reqId = reqId++;
			reqInfo[msg.reqId] = {callback: callback, error: error};

			//TODO Maybe a special function for this better than this hack?
			//File watch special case where the callback is called multiple times
			if (msg.action == 'watchFile')
			{
				fileChangedListeners[msg.path] = msg.listener;
				delete msg.listener;
			}

			ipcRenderer.send('rendererReq', msg);
        },
		registerMsgListener: function(action, callback)
		{
			ipcRenderer.on(action, function(event, args)
			{
				callback(args);
			});
		},
		sendMessage: function(action, args)
		{
			ipcRenderer.send(action, args);
		},
		listenOnce: function(action, callback)
		{
			ipcRenderer.once(action, function(event, args)
			{
				callback(args);
			});
		}
    }
);

contextBridge.exposeInMainWorld(
    'process', {
		type: process.type,
		versions: process.versions
	}
);
// // 기존 exposeInMainWorld가 있다면 여기에 추가
// contextBridge.exposeInMainWorld('electronAPI', {
//   runHydro: (filePath) => ipcRenderer.invoke('run-hydro', args)
// });
// 기존 exposeInMainWorld가 있다면 여기에 추가
// contextBridge.exposeInMainWorld('electronAPI', {
//   runHydro: async (filePath, currentPageName, userOption) => {
//     try {
//       const result = await ipcRenderer.invoke('run-hydro', filePath, currentPageName, userOption);
//       // 여기서 alert 제거. result를 그대로 리턴만 함
//       return result;
//     } catch (error) {
//       return `❌ Error occurred: ${error}`;
//     }
//   }
// });
contextBridge.exposeInMainWorld('electronAPI', {
  runHydro: async (filePath, currentPageName, userOption) => {
    try {
      return await ipcRenderer.invoke('run-hydro', filePath, currentPageName, userOption);
    } catch (error) {
      return `❌ Error occurred: ${error}`;
    }
  },

  // ✅ USB 체크용 API 추가
  checkUsbKey: async () => {
    try {
      return await ipcRenderer.invoke('check-usb-key');
    } catch (error) {
      return `❌ USB check error: ${error}`;
    }
  },

// ✅ Edit Stream data API (send 방식)
editStreamData: (filePath, currentPageName) => {
  ipcRenderer.send('edit-stream-data', filePath, currentPageName);
}
});
