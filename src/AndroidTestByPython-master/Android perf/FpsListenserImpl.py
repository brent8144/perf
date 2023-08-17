import re
import subprocess
import time
import pymysql
from FpsListener import IFpsListener


class FpsListenserImpl(IFpsListener):
    def __init__(self):
        pass

    def report_fps_info(self, fps_info):
        print('\n')
        print("Device model: " + str(fps_info.device_model))
        print("Device id: " + str(fps_info.device_id))
        print("Device os: " + str(fps_info.device_os))
        print("當前進程：" + str(fps_info.pkg_name))
        print("當前窗口是：" + str(fps_info.window_name))
        print("當前手機窗口刷新時間：" + str(fps_info.time))
        print("當前窗口fps：" + str(fps_info.fps))
        print("當前2s獲取總幀數：" + str(fps_info.total_frames))
        print("當前窗口丢幀數(>16.67ms）：" + str(fps_info.jankys_more_than_16))
        print("當前窗口卡顿數(>166.7ms)：" + str(fps_info.jankys_more_than_166))
        print("CPU核心 :",str(fps_info.cpukel))
        print("應用的CPU使用率 :",str(fps_info.cpu_usage),"%")
        print("系統CPU使用率 :",str(fps_info.sys_cpu),"%")
        print("記憶體 :",str(fps_info.memory),"M")
        print("wifi下載流量 :",str(fps_info._flow_d))
        print("wifi上傳流量 :",str(fps_info._flow_u))
        print("溫度 :",str(fps_info.temperature),"°C")
        print("當前電量 :",str(fps_info.battery),"%")
        print("Drawcall ：" + str(fps_info.drawcall))
        print('\n')

        # 連接資料庫
        connect = pymysql.Connect(
        host='xxx.x.x.x',
        port=1234,
        user='user_id',
        passwd='password',
        db='db_name',
        charset='utf8'
        )
        # 寫入資料
        cursor = connect.cursor()
        sql = "INSERT INTO and_fps (jank,big_jank,frame_count,_fps,time_fps) VALUES('"+str(fps_info.jankys_more_than_16)+"','"+str(fps_info.jankys_more_than_166)+"','"+str(fps_info.total_frames)+"','"+str(fps_info.fps)+"','"+str(fps_info.time)+"')"
        sql_cpu = "INSERT INTO and_cpu (cpukel,use_cpu,sys_cpu,temperature,time_cpu) VALUES('"+str(fps_info.cpukel)+"','"+str(fps_info.cpu_usage)+"','"+str(fps_info.sys_cpu)+"','"+str(fps_info.temperature)+"','"+str(fps_info.time)+"')"
        sql_mem = "INSERT INTO and_memory (memory,time_memory) VALUES('"+str(fps_info.memory)+"','"+str(fps_info.time)+"')"
        sql_net = "INSERT INTO and_network (netflow_download,netflow_upload,time_net) VALUES('"+str(fps_info._flow_d)+"','"+str(fps_info._flow_u)+"','"+str(fps_info.time)+"')"
        sql_battery = "INSERT INTO and_battery (battery,time_battery) VALUES('"+str(fps_info.battery)+"','"+str(fps_info.time)+"')"
        sql_drawcall = "INSERT INTO and_drawcall (drawcall,time_drawcall) VALUES('"+str(fps_info.drawcall)+"','"+str(fps_info.time)+"')"
        sql_info = "INSERT INTO and_info (pkg_name,window_name,time_info,device_id,device_os,device_model) VALUES('"+str(fps_info.pkg_name)+"','"+str(fps_info.window_name)+"','"+str(fps_info.time)+"','"+str(fps_info.device_id)+"','"+str(fps_info.device_os)+"','"+str(fps_info.device_model)+"')"
        cursor.execute(sql)
        cursor.execute(sql_cpu)
        cursor.execute(sql_mem)
        cursor.execute(sql_net)
        cursor.execute(sql_battery)
        cursor.execute(sql_drawcall)
        cursor.execute(sql_info)
        connect.commit()
        # 關閉連接
        cursor.close()
        connect.close()
