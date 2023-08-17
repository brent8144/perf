# Performance with iOS and Android Tool

- [Performance with iOS and Android Tool](#kkgame-slot-regression-testing-tool)
  - [Summary](#summary)
  - [Quick Start](#quick-start)
    - [安裝 Python Modules](#安裝-python-modules)
  - [Android 效能測試](#Andorid-效能測試)
      - [Step.0 Android 效能測試位置](#step0-Android-效能測試位置)
      - [Step.1 設定 Android DB 資訊](#step1-設定-Android-DB-資訊)
      - [Step.2 執行程式](#step2-執行程式)
  - [iOS 效能測試](#iOS-效能測試)
      - [Step.0 iOS 效能測試位置](#step0-iOS-效能測試位置)
      - [Step.1 設定 iOS DB 資訊](#step1-設定-iOS-DB-資訊)
      - [Step.2 設定 app 的 bundle id](#step2-設定-app-的-bundle-id)
      - [Step.3 執行程式](#step3-執行程式)
  - [Project Layout](#project-layout)
  - [Documentations](#documentations)
  - [References](#references)

--- 

## Summary

利用 Python 抓取 iOS 及 Android 的效能資訊，再利用 MySQL 及 Grafana 將數據結果視覺化呈現  

---

## Quick Start

### 安裝 Python Modules

首次下載該專案時，可以執行該指令安裝該專案所需使用到的第三方模組

```shell
make install_requirements
```

---
##  Android 效能測試

#### Step.0 Android 效能測試位置
perf_test\src\AndroidTestByPython-master\Android_perf

#### Step.1 設定 Android DB資訊 
設定 DB 連接資訊 `FpsListenserImpl.py`

```python
    # 連接資料庫
        connect = pymysql.Connect(
        host='xxx.x.x.x',
        port=1234,
        user='user_id',
        passwd='password',
        db='db_name',
        charset='utf8'
        )
```
#### Step.2 執行程式
執行程式，即可進行效能測試 `android_perf.py`

---

##  IOS 效能測試

#### Step.0 iOS 效能測試位置
perf_test\src\py-ios-device-main\iOS_perf

#### Step.1 設定 iOS DB資訊  
設定 DB 連接資訊 `db_set.py`

```python
    # db 連結相關設定
    host='xxx.x.x.x',
    port=1234,
    user='user_id',
    passwd='password',
    db='db_name',
    charset='utf8'
```

#### Step.2 設定 app 的 bundle id
設定要測試 app 的 bundle id `ios_perf.py`

```python
    # bundle id 設定
    # 测试iOS应用包名 com.google.chrome.ios  com.pushtest2.hy  com.google.ios.youtube    com.pushtest1.lv    com.apple.mobilesafari  com.apple.mobilesafari
    app_bundle_id = "com.google.chrome.ios" 
```
#### Step.3 執行程式 
執行程式，即可進行效能測試 `ios_perf.py`

---

## Project Layout

```text
KKGame Slot Regression Testing Tool
 ├─ DB/                  # MySQL DB Table Layout
 ├─ Grafana_dashboard/   # Grafana_dashboard
 ├─ .gitignore           #
 ├─ src                  # 效能測試程式
 ├─ ..                   #
 ├─ README.md            # 
 ├─ requirements.txt     # 該專案所依賴的 python 第三方模組列表
 ├─ 相關語法.txt          # 相關語法及指令
```

---

## Documentations

施工中 ...

---

## References

施工中 ...
