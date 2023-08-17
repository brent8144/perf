"""
@Date    : 2021-09-07
@Author  : liyachao
"""
import datetime
import json
import os
import subprocess
import time
from unittest import result
import webbrowser

import pymysql.cursors
import tidevice
from ios_device import py_ios_device
from tidevice import Device
from tidevice._proto import MODELS

import config

# 獲取設備device id
cmd  = "pyidevice devices"
output = subprocess.check_output(cmd).split()
ss =str(output)
device_id=ss.split("serial:")[1].split(",'")[0]

# 獲取設備app包名，指令: tidevice applist
# bundle id 設定
# 測試app包名
app_bundle_id = "com.google.chrome.ios" 
sleeptime = 1800 #測試時間(s)


# 獲取並印出設備資訊
def get_device_info(name):
    device = tidevice.Device(device_id)  # iOS设备
    value = device.get_value()
    
    for attr in ('DeviceName', 'ProductVersion', 'ProductType',
                 'ModelNumber', 'SerialNumber', 'PhoneNumber',
                 'CPUArchitecture', 'ProductName', 'ProtocolVersion',
                 'RegionInfo', 'TimeIntervalSince1970', 'TimeZone',
                 'UniqueDeviceID', 'WiFiAddress', 'BluetoothAddress',
                 'BasebandVersion'):
        if attr == name:
            if value.get(attr):
                return str(value.get(attr)).replace(" ", "")
    if name == "MarketName":
        return MODELS.get(value['ProductType']).replace(" ", "")
    return None
#印出設備資訊
tidevice_obj = tidevice.Device(device_id)  # iOS设备            
ss=str(device_id)#转成str
MarketName = get_device_info("MarketName")
start_time = datetime.datetime.now().strftime("%m%d_%H%M")
run_id = get_device_info("MarketName") + datetime.datetime.now().strftime("_%m%d_%H%M")
DeviceName =  get_device_info("DeviceName")
ProductVersion = get_device_info("ProductVersion")
ProductType =  get_device_info("ProductType")
ModelNumber =  get_device_info("ModelNumber")
SerialNumber = get_device_info("SerialNumber")
PhoneNumber = get_device_info("PhoneNumber")
CPUArchitecture = get_device_info("CPUArchitecture")
ProductName = get_device_info("ProductName")
ProtocolVersion = get_device_info("ProtocolVersion")
RegionInfo = get_device_info("RegionInfo")
TimeIntervalSince1970 = get_device_info("TimeIntervalSince1970")
TimeZone = get_device_info("TimeZone")
UniqueDeviceID = get_device_info("UniqueDeviceID")
WiFiAddress = get_device_info("WiFiAddress")
BluetoothAddress = get_device_info("BluetoothAddress")
BasebandVersion = get_device_info("BasebandVersion")
#brent_yang_create
print("------------------------------------")
print("Start : ",time.ctime())
print("------------------------------------\n")

print("-----------設備資訊-----------")
print("Time :",start_time)
print("MarketName :",MarketName)
print("DeviceName :",DeviceName)
print("ProductVersion :",ProductVersion)
print("ProductType :",ProductType)
print("ModelNumber :",ModelNumber)
print("SerialNumber :",SerialNumber)
print("PhoneNumber :",PhoneNumber)
print("CPUArchitecture :",CPUArchitecture)
print("ProductName :",ProductName)
print("ProtocolVersion :",ProtocolVersion)
print("RegionInfo :",RegionInfo)
print("TimeIntervalSince1970 :",TimeIntervalSince1970)
print("TimeZone :",TimeZone)
print("UniqueDeviceID :",UniqueDeviceID)
print("WiFiAddress :",WiFiAddress)
print("BluetoothAddress :",BluetoothAddress)
print("BasebandVersion :",BasebandVersion)
print("-------------------------------\n")
print("------------APP資訊------------")
print("APP包名 :",app_bundle_id)
print("-------------------------------")

# 数据存数据库连接数据库
connect = pymysql.Connect(
host=config.host,
port=config.port,
user=config.user,
passwd=config.passwd,
db=config.db,
charset=config.charset
)
# 获取游标
cursor = connect.cursor()
sql = "INSERT INTO my_phone (start_time,MarketName,DeviceName,ProductVersion,UniqueDeviceID,app_bundle_id,ProductName)VALUES('"+start_time+"','"+MarketName+"','"+DeviceName+"','"+ProductVersion+"','"+UniqueDeviceID+"','"+app_bundle_id+"','"+ProductName+"')"
cursor.execute(sql)
connect.commit()
# 关闭连接
cursor.close()
connect.close()


def callback_fps(res):
    print('***************FPS打印',res,"\n")
    # fps数据
    ss=str(res)
    fps_test=ss.split("'FPS':")[1].split(".")[0]
    jank_test=ss.split("'jank':")[1].split(",")[0]
    big_jank=ss.split("'big_jank':")[1].split(",")[0]
    stutter=ss.split("'stutter':")[1][0:5].split("}")[0]
    time_fps=ss.split("'currentTime': '")[1].split(".")[0]

    # 数据存数据库连接数据库
    connect = pymysql.Connect(
    host=config.host,
    port=config.port,
    user=config.user,
    passwd=config.passwd,
    db=config.db,
    charset=config.charset
    )
    # 获取游标
    cursor = connect.cursor()
    sql = "INSERT INTO my_fps (fps,jank,big_jank,stutter,time_fps,run_id) VALUES('"+fps_test+"','"+jank_test+"','"+big_jank+"','"+stutter+"','"+time_fps+"','"+run_id+"')"
    cursor.execute(sql)
    connect.commit()
    # 关闭连接
    cursor.close()
    connect.close()
    
    '''
    # 發生卡頓時(jank!=0)，進行截圖
    jankint = int(jank_test)
    if jankint !=  0 :
        filename = time.strftime('screenshot_ios_%Y_%m_%d_%H%M%S.png', time.gmtime())
        #filename = "/xxxx/xxx/screenshot.jpg"
        Device(device_id).screenshot().convert("RGB").save(filename)
        print("screenshot:",filename)
    '''

def test_get_myZtest():
    #channel = py_ios_device.start_get_gpu(callback=callback_gpu)
    channel2 = py_ios_device.start_get_fps(callback=callback_fps)
    #channel3 = py_ios_device.start_get_network(callback=callback_network)
    t = tidevice.Device(device_id)#iOS设备
    perf = tidevice.Performance(t,perfs=list(tidevice.DataType))
    def callback(_type: tidevice.DataType, value: dict):
        # 獲取cpu資訊
        if _type.value == "cpu":
            print('CPU打印',value)
            ss=str(value)#转成str
            use_cpu=ss.split("'value':")[1][0:6].split("}")[0]
            sys_cpu=ss.split("'sys_value':")[1][0:7].split("}")[0]
            count_cpu=ss.split("'count':")[1].split("}")[0]
            time_cpu=ss.split("'timestamp': ")[1].split(",")[0]

            # 数据存数据库连接数据库
            connect = pymysql.Connect(
            host=config.host,
            port=config.port,
            user=config.user,
            passwd=config.passwd,
            db=config.db,
            charset=config.charset
            )
            # 获取游标
            cursor = connect.cursor()
            time_cpu = time_cpu[:10]
            timeArray_cpu = time.localtime(int(time_cpu))
            final_cpu_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray_cpu)
            sql = "INSERT INTO my_cpu (use_cpu,sys_cpu,count_cpu,time_cpu,run_id) VALUES('"+use_cpu+"','"+sys_cpu+"','"+count_cpu+"','"+final_cpu_time+"','"+run_id+"')"
            cursor.execute(sql)
            connect.commit()
            # 关闭连接
            cursor.close()
            connect.close()

        # 獲取memory資訊
        if _type.value == "memory":
            print('Memory打印',value)
            ss=str(value)
            memory=ss.split("'value':")[1][0:6].split("}")[0]
            time_memory=ss.split("'timestamp': ")[1].split(",")[0]
            # 数据存数据库连接数据库
            connect = pymysql.Connect(
            host=config.host,
            port=config.port,
            user=config.user,
            passwd=config.passwd,
            db=config.db,
            charset=config.charset
            )
            # 获取游标
            cursor = connect.cursor()
            time_memory = time_memory[:10]
            timeArray_memory = time.localtime(int(time_memory))
            final_memory_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray_memory)
            sql = "INSERT INTO my_memory (memory,time_memory,run_id) VALUES('"+memory+"','"+final_memory_time+"','"+run_id+"')"
            cursor.execute(sql)
            connect.commit()
            # 关闭连接
            cursor.close()
            connect.close()

        # 獲取gpu資訊
        if _type.value == "gpu":
            print('GPU打印',value) 
            ss=str(value)#转数据类型
            gpu_Device=ss.split("'device':")[1].split(",")[0]
            gpu_Renderer=ss.split("'renderer':")[1].split(",")[0]
            gpu_Tiler=ss.split("'tiler':")[1].split(",")[0]
            time_gpu=ss.split("'timestamp': ")[1].split(",")[0]

            '''
            # Drawcall計算
            # DrawCall = 25K * CPU_Frame(GHz) * CPU_Percentage(百分比) / Framerate(希望的fps)
            CPUFrame = 10*0.000001 # 將kHz換算成GHz
            CPU_Percentage = float(sys_cpu)*100 # 正在運行的cpu頻率/cpu最高的工作頻率
            Framerate = 60
            draw_call = 25000 * CPUFrame * CPU_Percentage/Framerate
            drawcall = str(draw_call)
            '''#BRENTyang_create

            # 数据存数据库连接数据库
            connect = pymysql.Connect(
            host=config.host,
            port=config.port,
            user=config.user,
            passwd=config.passwd,
            db=config.db,
            charset=config.charset  
            )
            # 获取游标
            cursor = connect.cursor()
            time_gpu = time_gpu[:10]
            timeArray_gpu = time.localtime(int(time_gpu))
            final_gpu_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray_gpu)
            sql = "INSERT INTO my_gpu (gpu_Device,gpu_Renderer,gpu_Tiler,time_gpu,run_id) VALUES('"+gpu_Device+"','"+gpu_Renderer+"','"+gpu_Tiler+"','"+final_gpu_time+"','"+run_id+"')"
            cursor.execute(sql)
            connect.commit()
            #print('GPU成功插入', cursor.rowcount, '条数据')
            # 关闭连接
            cursor.close()
            connect.close()
        
        # 獲取network資訊
        if _type.value == "network":
            print('Network打印',value) 
            ss=str(value)#转数据类型
            network_downFlow=ss.split(" 'RxBytes': ")[1].split(", ")[0]
            network_upFlow=ss.split(" 'TxBytes': ")[1].split(",")[0]
            time_network=ss.split(" 'timestamp': ")[1].split("}")[0]
            
            # 数据存数据库连接数据库
            connect = pymysql.Connect(
            host=config.host,
            port=config.port,
            user=config.user,
            passwd=config.passwd,
            db=config.db,
            charset=config.charset
            )
            # 获取游标
            cursor = connect.cursor()
            time_network = time_network[:10]
            timeArray_network = time.localtime(int(time_network))
            final_network_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray_network)
            sql = "INSERT INTO my_network (network_downFlow,network_upFlow,time_network,run_id) VALUES('"+network_downFlow+"','"+network_upFlow+"','"+final_network_time+"','"+run_id+"')"
            cursor.execute(sql)
            connect.commit()
            # 关闭连接
            cursor.close()
            connect.close()
            
    def new_func(time_cpu):
        time_cpu_test = time_cpu
        return time_cpu_test

    perf.start(app_bundle_id, callback=callback)
    time.sleep(sleeptime) #测试时长
    
    print("-------------------------------")
    print("End : ",time.ctime())
    print("-------------------------------")
    perf.stop()

    #py_ios_device.stop_get_gpu(channel)
    py_ios_device.stop_get_fps(channel2)
    #channel.stop()
    channel2.stop()

def open_grafana():
    grafana_dashboard_url = "http://localhost:3000/d/JVeltfr7k/ios_perf_test?orgId=1&from=now-30m&to=now"
    webbrowser.open(grafana_dashboard_url)
    time.sleep(10)
    
if __name__ == "__main__":
    test_get_myZtest()
    time.sleep(3)

    open_grafana()