#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龍族報告索引自動生成器
掃描 ~/Desktop/龍族報告 結構，產出 索引.md 總目錄。
由 cron 每週日呼叫，保持索引不過時。
"""
import os, datetime

BASE = os.path.expanduser('~/Desktop/龍族報告')

STRUCT = {
    '01_專案': '進行中的開發專案（Exosome面泌體、TwoTone電商、MotoEye_HUD、DragonCommerce等）',
    '02_素材': '視覺資產、Logo、圖片、工具（ffmpeg等）',
    '03_作業': '日常作業：會議/SOP/報告/備份/監控/APK安裝檔',
    '04_資源': '學習筆記、數據、Market_Data',
    '99_封存': '歷史封存（舊備份、歷史紀錄、LineBot復原等）',
    '股票': '每日股市投資報告（華爾特8:40生成）+ 即時股價監控資料',
    '電商投資': '跨境電商/天貓/宗教禮品等投資相關文件',
    '龍族生態系': '成員資料、組織圖、戰略儀表板、identity_restore',
    '合作方案': '商業合作利潤模型等',
    '程式類': '各種 App 原型與腳本（理財顧問/代駕/股價監控）',
    'travel_assistant_app': '旅遊助手 App 核心邏輯（core.py/test_core.py）',
    'admin': '管理後台雛形（index.html/admin.js/firebase.js）',
    'Monitoring': '系統資源監控日誌',
    'Monitoring_logs': '監控日誌副本（舊）',
    'logs': '各種日誌',
    'Business-Plans': '商業計畫與專案進度（舊）',
    '_scripts': '內部腳本',
}

QUICK = [
    ('旅遊伴伴 APK', '03_作業/APK安裝檔/TravelHelper_debug.apk'),
    ('測試 App APK', '03_作業/APK安裝檔/HelloDragon_debug.apk'),
    ('每日股市報告', '股票/每日股市投資報告_YYYYMMDD.md'),
    ('龍族成員模型配對', '龍族成員模型配對建議_20260604.md'),
    ('Exosome 主副本', '01_專案/Exosome_Project/'),
    ('TwoTone 電商', '01_專案/TwoTone_Project/'),
    ('同步檢查點', 'SYNC_CHECKPOINT.md'),
    ('本索引', '索引.md'),
]

sub_desc = {
    'APK安裝檔': '編譯好的 APK（旅遊伴伴/測試App），直接安裝用',
    '備份': '身份快照/配置備份（含 hermes_config_backup，不進git）',
    '每日報告': '每日進度報告',
    '報告': '專案報告/建置報告/MotoEye紀錄',
    '標準作業流程': 'SOP 文件',
    '監控': '系統監控腳本與日誌',
    '監控備份': '監控備份',
    '會議': '會議記錄',
    '腳本': 'watchdog/監控腳本',
}

def main():
    top = sorted([d for d in os.listdir(BASE) if os.path.isdir(os.path.join(BASE, d))])
    files_top = sorted([f for f in os.listdir(BASE) if os.path.isfile(os.path.join(BASE, f))])
    sub03 = sorted([d for d in os.listdir(os.path.join(BASE,'03_作業')) if os.path.isdir(os.path.join(BASE,'03_作業',d))]) if os.path.isdir(os.path.join(BASE,'03_作業')) else []

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    L = []
    L.append('# 龍族報告 索引（INDEX）')
    L.append('')
    L.append(f'> 最後更新：{now}（由桃樂絲自動生成 / 每週日 cron 更新）')
    L.append('> 用途：檔案越來越多時，從此索引快速定位，不需一層層鑽。')
    L.append('')
    L.append('## 一、標準結構導覽（核心五大類）')
    L.append('')
    for d in ['01_專案','02_素材','03_作業','04_資源','99_封存']:
        L.append(f'- **{d}/** — {STRUCT.get(d,"")}')
    L.append('')
    L.append('## 二、業務資料夾（中文，維持原樣）')
    L.append('')
    for d in ['股票','電商投資','龍族生態系','合作方案','程式類','travel_assistant_app','admin']:
        L.append(f'- **{d}/** — {STRUCT.get(d,"")}')
    L.append('')
    L.append('## 三、舊副本 / 待整理（英文或重複，建議擇日歸檔）')
    L.append('')
    for d in ['04_ARCHIVES','04_REPORTS','05_DAILY_REPORTS','Monitoring','Monitoring_logs','logs','Business-Plans']:
        if d in top:
            L.append(f'- **{d}/** — {STRUCT.get(d,"（舊副本，待合併）")}')
    L.append('')
    L.append('## 四、重要檔案速查')
    L.append('')
    for name, path in QUICK:
        L.append(f'- {name}：`{path}`')
    L.append('')
    L.append('## 五、03_作業 子層細項')
    L.append('')
    for d in sub03:
        L.append(f'- **03_作業/{d}/** — {sub_desc.get(d,"")}')
    L.append('')
    L.append('## 六、待歸檔（散落根目錄，建議整理）')
    L.append('')
    loose_real = [f for f in files_top if f not in ('README.md','SYNC_CHECKPOINT.md','索引.md','.gitignore','requirements.txt','Procfile','.DS_Store','.heartbeat.log','.sync_checkpoint.md')]
    for f in loose_real:
        try:
            size = os.path.getsize(os.path.join(BASE,f))
            size_s = f'{size/1024/1024/1024:.1f}GB' if size>1024**3 else f'{size/1024/1024:.1f}MB' if size>1024**2 else f'{size/1024:.0f}KB'
        except: size_s='?'
        L.append(f'- `{f}` ({size_s})')
    L.append('')
    L.append('## 七、命名規範（給未來新增檔案參考）')
    L.append('')
    L.append('- 報告類：`每日股市投資報告_YYYYMMDD.md`、`DAILY_REPORT_YYYY-MM-DD.md`')
    L.append('- 任務書：`任務書_負責人_主題.md`')
    L.append('- 會議：`會議_YYYYMMDD_主題.md`')
    L.append('- APK：`XXXXX_debug.apk` 放 `03_作業/APK安裝檔/`')
    L.append('- 索引更新：新增重要資料夾/檔案時請同步更新本檔')
    L.append('')
    L.append('---')
    L.append('本索引由桃樂絲維護，每週日自動更新。')

    out = os.path.join(BASE, '索引.md')
    with open(out, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(L))
    print(f'索引已更新：{out}（{len(L)} 行，{now}）')

if __name__ == '__main__':
    main()
