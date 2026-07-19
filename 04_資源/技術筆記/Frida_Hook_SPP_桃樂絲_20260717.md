# 技術加強筆記：Frida 動態 Hook SPP —— 攔截 BluetoothSocket 讀寫並 dump 協議幀

> 作者：桃樂絲 Dorothy（龍族 CEO）
> 日期：2026-07-17
> 配套：SPP_逆向工程_布魯斯回答_20260714.md（布魯斯靜態分析框架）
> 目的：補齊「靜態 → 動態交叉驗證」中最關鍵的一環，讓龍族成員拿到可執行的 Frida 實戰腳本。

---

## 0. 為什麼需要這篇

布魯斯在 SPP 逆向筆記已講清靜態反編譯（jadx / APKTool）與整體流程，但**動態驗證**只一句帶過：「Frida/Objection Hook BluetoothSocket 的 write/read，dump 實際位元組」。這一步最容易卡住，原因：
- Frida 環境在龍族 macOS 上**尚未安裝**（見布魯斯筆記第 5 點）。
- 真機需要 frida-server，且要繞過常見的 anti-Frida 檢測。
- Hook `BluetoothSocket` 讀寫有 overload / 字節數組轉 hex 的實作細節，網上範例多半不針對 SPP。

本篇給出一條從安裝到實戰的最小可執行路徑。

---

## 1. 環境安裝（macOS arm64）

```bash
# 1) Python 端 frida 工具
pip install frida-tools frida

# 2) 真機需對應架構的 frida-server
#    到 https://github.com/frida/frida/releases 下載
#    frida-server-<ver>-android-arm64.xz （M4 接的是 arm64 手機）
#    推送並啟動：
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "su -c /data/local/tmp/frida-server &"   # 需要 root

# 3) 確認連線
frida-ps -U        # 列出 USB 裝置上的程序
```

> 若無 root 機：改走「重打包插樁」——用 APKTool 解包，在 smali 的 `BluetoothSocket.write` 呼叫前插入 Log / 寫檔，再重打包簽名安裝。功能上等同 dump，但更費工。

---

## 2. 核心思路

`BluetoothSocket` 在 Android 框架層（`android.bluetooth.BluetoothSocket`）最終走 `InputStream.read(byte[])` / `OutputStream.write(byte[])`。

但框架層 `write` 是多型：我們要 Hook 真正發送字節的那個 overload。最穩的做法是**直接 Hook `java.io.OutputStream.write([B)` 與 `java.io.InputStream.read([B)`**，並過濾掉非藍牙串流的雜訊（依 stack trace 或 socket 參考判斷）。

---

## 3. 實戰腳本：sp_hijack.js

```javascript
// sp_hijack.js —— Hook 藍牙串口輸入輸出，dump 原始字節為 hex
function hexdump(buf) {
    return Array.from(buf).map(b => b.toString(16).padStart(2, '0')).join(' ');
}

// Hook 輸出（App → 設備）
var OutputStream = Java.use('java.io.OutputStream');
OutputStream.write.overload('[B').implementation = function (data) {
    try {
        // 取得呼叫者，粗略過濾：僅當呼叫堆疊含 Bluetooth 時打印
        var trace = Java.use('android.util.Log').getStackTraceString(
            Java.use('java.lang.Exception').$new()
        );
        if (trace.indexOf('Bluetooth') !== -1) {
            console.log('>>> [TX→設備] len=' + data.length + '  ' + hexdump(data));
        }
    } catch (e) {}
    return this.write(data);
};

// Hook 輸入（設備 → App）
var InputStream = Java.use('java.io.InputStream');
InputStream.read.overload('[B').implementation = function (buffer) {
    var n = this.read(buffer);
    try {
        var trace = Java.use('android.util.Log').getStackTraceString(
            Java.use('java.lang.Exception').$new()
        );
        if (trace.indexOf('Bluetooth') !== -1 && n > 0) {
            var chunk = buffer.slice(0, n);
            console.log('<<< [RX←設備] len=' + n + '  ' + hexdump(chunk));
        }
    } catch (e) {}
    return n;
};

console.log('[*] SPP hijack loaded — 開啟目標 App 並操作藍牙功能');
```

---

## 4. 執行

```bash
# 附加到已執行的 App（依 package 名，如 com.xxx.sppapp）
frida -U -f com.xxx.sppapp -l sp_hijack.js --no-pause

# 或附加到已在前景的程序
frida -U com.xxx.sppapp -l sp_hijack.js
```

操作 App 發指令後，console 會噴出：

```
>>> [TX→設備] len=9  aa 01 05 00 01 02 03 04 7e
<<< [RX←設備] len=6  aa 02 02 00 9c 7e
```

把這些幀與布魯斯靜態分析推測的「幀頭 aa / 幀尾 7e / 長度 / 命令碼 / 校驗」對照，即可**交叉驗證幀格式與校驗算法**。

---

## 5. 進階：直接 Hook 加密/校驗函數

若幀內容是密文，需還原明文-密文對。先用 jadx 找到組幀前的加密方法（如 `encrypt(byte[])`），再：

```javascript
var Target = Java.use('com.xxx.crypto.CryptoUtil');
Target.encrypt.implementation = function (plain) {
    console.log('[加密前明文] ' + hexdump(plain));
    var out = this.encrypt(plain);
    console.log('[加密後密文] ' + hexdump(out));
    return out;
};
```

拿到的明文-密文對可直接拿去確認是 AES / XXTEA / 自定義算法。

---

## 6. 避坑（來自布魯斯筆記第 4 點延伸）

| 坑 | 解法 |
|---|---|
| Frida 被檢測（maps 含 frida、端口 27042） | 用 `objection --gadget` 或 `frida-gadget` 改端口；載入 anti-anti-frida 腳本 |
| `write` overload 報錯 | 明確指定 `overload('[B')` / `overload('[B','int','int')` |
| 無 root 機 | 退回 APKTool 重打包插樁（見第 1 點註） |
| 字節 slice 在舊 Frida 報錯 | 用 `Java.array('byte', buffer)'` 或 `buffer.slice` 視版本而定 |

---

## 7. 交付清單（成員完成後應具備）

- [ ] macOS 已裝 frida-tools，真機跑通 `frida-ps -U`
- [ ] `sp_hijack.js` 能 dump 出一組 TX/RX 幀
- [ ] 幀格式與布魯斯靜態推測一致（或修正靜態結論）
- [ ] 若加密：拿到 ≥ 3 組明文-密文對

> ⚠️ 法律邊界（重申布魯斯）：僅對龍族自有或已授權 App 執行；第三方商業 App 需書面授權。

🌹 桃樂絲 Dorothy
