![android_perf.py]
![FpsListenserImpl.py]
![ios_perf.py]
![db_set.py]

# brent_yang 20230206

#####  Android 效能測試

0. Android 效能測試放置在以下位置。
    perf_test\src\AndroidTestByPython-master\Android_perf

1. 設定 DB 連接資訊 (FpsListenserImpl.py)。
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
2. 執行程式，即可進行效能測試 (android_perf.py) 。

##### IOS 效能測試

0. IOS 效能測試放置在以下位置。
    perf_test\src\py-ios-device-main\iOS_perf

1. 設定 DB 連接資訊(db_set.py)。
```python
    # db 連結相關設定
    host='xxx.x.x.x',
    port=1234,
    user='user_id',
    passwd='password',
    db='db_name',
    charset='utf8'
```
2. 設定要測試 app 的 bundle id(ios_perf.py)。
```python
    # bundle id 設定
    # 测试iOS应用包名 com.google.chrome.ios  com.pushtest2.hy  com.google.ios.youtube    com.pushtest1.lv    com.apple.mobilesafari  com.apple.mobilesafari
    app_bundle_id = "com.google.chrome.ios" 
```
3. 執行程式，即可進行效能測試 (ios_perf.py)。"# perf" 
