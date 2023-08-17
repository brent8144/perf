from calendar import c
import os
import queue
import re
import subprocess
import threading
import time
from math import floor
from typing import Any

import pymysql

from FpsInfo import FpsInfo
from FpsListenserImpl import FpsListenserImpl
from FpsListener import IFpsListener

class FPSMonitor(object):
    def __init__(self, sn):
        self.frequency = 5  # 取樣頻率
        self.device = sn
        self.fpscollector = FpsCollector(self.device, self.frequency)

    def set_listener(self, listener):
        self.fpscollector.set_listener(listener)
    
    # 取得設備device id 
    def get_deviceid():
        adb_id = "adb devices"
        output_id = subprocess.check_output(adb_id).split()
        ss_id =str(output_id)
        deviceid=ss_id.split("'attached', b'")[1].split("',")[0]
        #print("deviceid = ",deviceid)
        return deviceid
    
    def start(self, start_time):
        self.start_time = start_time
        if self.fpscollector.package_name is None:
            print("手機螢幕沒開，或USB未連接")
            return
        print('FPS monitor has start!')
        self.fpscollector.start(start_time)

    #brent_yang_create
    
    def stop(self):
        '''結束FPSMonitor
        '''
        if self.fpscollector.package_name is None: 
            print("手機螢幕沒開，或USB未連接")
            return
        self.fpscollector.stop()
        print('FPS monitor has stop!')

    def save(self):
        pass

    def parse(self, file_path):
        '''
        :param str file_path: 要解析数据文件的路径
        '''
        pass

    def get_fps_collector(self):
        '''
        保存time fps jank的列表
        :return: fps收集器
        :rtype: SurfaceStatsCollector
        '''#brent_yang_create
        return self.fpscollector

class FpsCollector(object):

    '''Collects surface stats for a SurfaceView from the output of SurfaceFlinger
    '''
    def __init__(self, device, frequency):
        self.device = device
        self.frequency = frequency
        self.jank_threshold = 16.7  # 内部的時間以毫秒为單位
        self.last_timestamp = 0  # 上次最後一幀的時間
        self.data_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.get_focus_window()
        self.listener = None

    def start(self, start_time):
        '''打開SurfaceStatsCollector
        '''
        self._clear_fps_data()
        self.collector_thread = threading.Thread(target=self._collector_thread)
        self.collector_thread.start()
        self.calculator_thread = threading.Thread(target=self._calculator_thread, args=(start_time,))
        self.calculator_thread.start()

    def stop(self):
        '''結束SurfaceStatsCollector
        '''
        if self.collector_thread:
            self.stop_event.set()

            self.collector_thread.join()

            self.collector_thread = None

    def set_listener(self, listener):
        self.listener = listener
        
    '''
    # 取的手機資訊
    def get_phoneidfo(self):
        adb = "adb shell dumpsys battery"
        output = subprocess.check_output(adb).split()
        ss =str(output)
        temp=ss.split("temperature:', b'")[1].split("',")[0]
        battery =ss.split("level:', b'")[1].split("',")[0]
        temperature = int(temp)/10
    '''

    # 取得當前視窗應用
    def get_focus_window(self):
        '''通過adb shell dumpsys activity | findstr "mResume"
        '''        
        cmd = "adb -s " + self.device + " shell dumpsys activity | findstr mResume"
        #print(cmd)
        windowInfo = os.popen(cmd)
        windowInfo = str(windowInfo.readline())
        #print(windowInfo)
        if windowInfo is "":
            self.package_name = None
            self.focus_window = None
            return
        packageNameinfo = windowInfo.split(" ")[7]
        packageName = packageNameinfo.split("/")[0]
        if "/." in packageNameinfo:
            windowName = packageName + "/" + packageName + "." + packageNameinfo.split("/.")[1]
        else:
            windowName = packageNameinfo
        self.package_name = packageName
        self.focus_window = windowName        

    def _calculate_results(self, timestamps):

        # 取得設備相關資訊
        adb_id = "adb devices"
        output_id = subprocess.check_output(adb_id).split()
        ss_id =str(output_id)
        device_ida=ss_id.split("'attached', b'")[1].split("',")[0]
        device_id = str(device_ida)
        # model
        adb_model = "adb shell getprop ro.vendor.oplus.market.name"
        output_model = subprocess.check_output(adb_model).split()
        ss_model = str(output_model)
        device_model=ss_model.translate({ord(letter): None for letter in "[b',]"})
        # os
        adb_os = "adb shell getprop ro.build.version.release"
        output_os = subprocess.check_output(adb_os).split()
        ss_os = str(output_os)
        device_os1=ss_os.split("[b'")[1].split("']")[0]
        device_os = "Android "+device_os1
        
        # fps、jank、big_jank計算
        """Returns a list of SurfaceStatsCollector.Result.
        FPS  丢帧率  卡顿次数  总帧数
        """
        frame_count = len(timestamps)
        jank_list, caton,vsyncOverTimes = self._calculate_janky(timestamps)
        fps_org = frame_count * 60 / (frame_count + vsyncOverTimes)
        fps = round(fps_org,3)
        
        # 取得memory
        cmd = "adb -s " +  self.device +" shell  dumpsys  meminfo %s" % (self.package_name)
        output = subprocess.check_output(cmd).split()
        s_men = ".".join([x.decode() for x in output]) # 转换为string)
        #擷取TOTAL.後的字串
        memory_a = int(re.findall("TOTAL.(\d+)*", s_men, re.S)[0])
        memory = round((memory_a/1024),3)

        # 取得temperature
        adb = "adb shell dumpsys battery"
        output = subprocess.check_output(adb).split()
        ss =str(output)
        temp=ss.split("temperature:', b'")[1].split("',")[0]
        battery =ss.split("level:', b'")[1].split("',")[0]
        temperature = int(temp)/10
        #print("temperature :",temperature)
        
        # 取得應用的pid
        #adb =  adb -s YLE64LRS49ZLWCKN shell pidof com.heytap.browser 
        #adb = "adb -s " + self.device + " shell dumpsys meminfo " + self.package_name
        adb = "adb -s " + self.device + " shell pidof " + self.package_name
        output = subprocess.check_output(adb).split()
        ss =str(output)
        apppid=ss.split("'b'")[0].split("',")[0]
        #print("app pid :",apppid)
        '''
        # 取得GPU使用率
        adb = "adb -s " + self.device + " shell cat /sys/class/kgsl/kgsl-3d0/gpubusy " + self.package_name
        output = subprocess.check_output(adb).split()
        ss =str(output)
        gpu_start = ss.split("'pid', b'")[1].split("',")[0]
        gpu_end = ss.split("'pid', b'")[1].split("',")[0]
        gpu = (int(gpu_start)/int(gpu_end)) * 100
        print("gpu :",gpu)
        '''
        # 取得cpu核心數
        adb = "adb -s " + self.device + " shell cat /proc/cpuinfo"
        output = subprocess.check_output(adb).split()
        sitem = ".".join([x.decode() for x in output])  # 转换为string
        cpukel = len(re.findall("processor", sitem))

        # 取得cpu使用率
        def totalCpuTime(self):
            user=nice=system=idle=iowait=irq=softirq= 0
            '''
            user:从系统启动开始累计到当前时刻，处于用户态的运行时间，不包含 nice值为负进程。
            nice:从系统启动开始累计到当前时刻，nice值为负的进程所占用的CPU时间
            system 从系统启动开始累计到当前时刻，处于核心态的运行时间
            idle 从系统启动开始累计到当前时刻，除IO等待时间以外的其它等待时间
            iowait 从系统启动开始累计到当前时刻，IO等待时间(since 2.5.41)
            hard irq 从系统启动开始累计到当前时刻，硬中断时间(since 2.6.0-test4)
            softirq 从系统启动开始累计到当前时刻，软中断时间(since 2.6.0-test4)
            stealstolen  这是时间花在其他的操作系统在虚拟环境中运行时（since 2.6.11）
            guest 这是运行时间guest 用户Linux内核的操作系统的控制下的一个虚拟CPU（since 2.6.24）
            '''
            cmd = "adb -s " + self.device +" shell cat /proc/stat"
            #cmd = "adb shell "cat /proc/stat | grep ^cpu""
            #print("cmd :",cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            res = output.split()
            for info in res:
                if info.decode() == "cpu":
                    user = res[1].decode()
                    nice = res[2].decode()
                    system = res[3].decode()
                    idle = res[4].decode()
                    iowait = res[5].decode()
                    irq = res[6].decode()
                    softirq = res[7].decode()  
          
            totaltime = int(user) + int(nice) + int(system) + int(idle) + int(iowait) + int(irq) + int(softirq)
            return totaltime
        
        #--------------------------------------------------
        def sysCpuTime(self):
            idle= 0
            cmd = "adb -s " + self.device +" shell cat /proc/stat"
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            res = output.split()
            for info in res:
                if info.decode() == "cpu":
                    idle = res[4].decode()
                    
                    systime = int(idle)
                    return systime
        
        #--------------------------------------------------
        def processCpuTime(self):
            '''
            pid     进程号
            utime   该任务在用户态运行的时间，单位为jiffies
            stime   该任务在核心态运行的时间，单位为jiffies
            cutime  所有已死线程在用户态运行的时间，单位为jiffies
            cstime  所有已死在核心态运行的时间，单位为jiffies
            '''
            cmd = "adb -s " + self.device +" shell cat /proc/stat"
            #print(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            res = output.split()
            #print("res :",res)
            utime = res[13].decode()
            stime = res[14].decode()
            cutime = res[15].decode()
            cstime = res[16].decode()
            '''
            print("utime="+utime)
            print("stime="+stime)
            print("cutime="+cutime)
            print("cstime="+cstime)
            '''
            processtime = int(utime) + int(stime) + int(cutime) + int(cstime)
            return processtime
        
        #--------------------------------------------------
        '''
        计算某进程的cpu使用率
        100*( processCpuTime2 – processCpuTime1) / (totalCpuTime2 – totalCpuTime1)*cpu核心數 (按100%计算，如果是多核情况下还需乘以cpu的个数);
        cpukel cpu几核
        pid 进程id
        '''
        processCpuTime1 = processCpuTime(self)
        time.sleep(1)
        processCpuTime2 = processCpuTime(self)
        processCpuTime3 = processCpuTime2 - processCpuTime1

        sysCpuTime1 = sysCpuTime(self)
        time.sleep(1)
        sysCpuTime2 = sysCpuTime(self)
        sysCpuTime3 = sysCpuTime2 - sysCpuTime1

        totalCpuTime1 = totalCpuTime(self)
        time.sleep(1)
        totalCpuTime2 = totalCpuTime(self)
        totalCpuTime3 = (totalCpuTime2 - totalCpuTime1) * cpukel

        # 應用的cpu使用率
        cpu = 100 * (processCpuTime3) / (totalCpuTime3) * cpukel
        cpu_usage = round(cpu,3)
        # 系統cpu使用率
        #totalcpu = 100 * (totalCpuTime3-sysCpuTime3) / totalCpuTime3
        syscpu = 100*((totalCpuTime2-sysCpuTime2)-(totalCpuTime1-sysCpuTime1))/(totalCpuTime2 - totalCpuTime1)
        sys_cpu = round(syscpu + cpu,3)

        #--------------------------------------------------
        # wifi,gprs流量
        cmd = "adb -s " + self.device + " shell cat /proc/" + apppid + "/net/dev"
        #print(cmd)
        _flow_down = [[]]
        _flow_upload = [[]]
        _flow = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.readlines()
        for item in _flow:
            if item.split()[0].decode() == "wlan0:":  # wifi
                # 0 上传流量，1 下载流量
                _flow_down[0].append(int(item.split()[1].decode()))
                _flow_upload[0].append(int(item.split()[9].decode()))
                _flow_down = str(_flow_down)
                _flow_upload = str(_flow_upload)
                _flow_d=_flow_down.split("[[")[1].split("]]")[0]
                _flow_u=_flow_upload.split("[[")[1].split("]]")[0]
                break
            if item.split()[0].decode() == "rmnet0:":  # gprs
                _flow_down[0].append(int(item.split()[1].decode()))
                _flow_upload[0].append(int(item.split()[9].decode()))
                _flow_down = str(_flow_down)
                _flow_upload = str(_flow_upload)
                _flow_d=_flow_down.split("[[")[1].split("]]")[0]
                _flow_u=_flow_upload.split("[[")[1].split("]]")[0]
                break
 
        #--------------------------------------------------
        # 取得Drawcall
        # 取得cpu正在運行的工作頻率(kHz)
        adb = "adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
        output = subprocess.check_output(adb).split()
        ss =str(output)
        CPU_Frame =ss.split("[b'")[1].split("'")[0]
        # 取得cpu最高的工作頻率(kHz)
        adbmax = "adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"
        outputmax = subprocess.check_output(adbmax).split()
        max =str(outputmax)
        CPU_Frame_Max =max.split("[b'")[1].split("'")[0]

        # DrawCall = 25K * CPU_Frame(GHz) * CPU_Percentage(百分比) / Framerate(希望的fps)
        CPUFrame = float(CPU_Frame)*0.000001 # 將kHz換算成GHz
        CPU_Percentage = float(CPU_Frame)/float(CPU_Frame_Max) # 正在運行的cpu頻率/cpu最高的工作頻率
        Framerate = 60
        draw_call = (25000*CPUFrame*CPU_Percentage/Framerate)/self.frequency
        drawcall = round(draw_call,0)
   
        #--------------------------------------------------
        # 回傳效能資訊
        return fps, jank_list, caton, cpukel, memory, cpu_usage, sys_cpu, _flow_d, _flow_u, temperature, battery, drawcall,device_id,device_os,device_model

    def _calculate_janky(self, timestamps):
        # 统计丢帧卡顿 ，和需要垂直同步次数
        jank_list = []
        caton = 0
        vsyncOverTimes = 0
        for timestamp in timestamps:
            if timestamp > self.jank_threshold:
                # 超过16.67ms
                jank_list.append(timestamp)
                if timestamp % self.jank_threshold == 0:
                    vsyncOverTimes += ((timestamp / self.jank_threshold) - 1)
                else:
                    vsyncOverTimes += floor(timestamp / self.jank_threshold)
            if timestamp > self.jank_threshold * 10:
                # 超过jank 的 10倍，166.7ms 明显卡的帧,用户会觉得卡顿
                # 超過jank 的 4倍，66.8ms
                caton += 1 
        '''
        # 發生卡頓時，進行截圖
        if caton != 0:
            print("發生卡頓情況，截圖中...請稍後!")
            filename = time.strftime('screenshot_android_%Y_%m_%d_%H%M%S.png', time.gmtime())
            cmd1 = "adb shell screencap -p /sdcard/" + filename
            os.system(cmd1)
            cmd2 = "adb pull /sdcard/" + filename
            os.system(cmd2)
            print("截圖完畢！")
            #os.system("pause")
        '''

        return jank_list, caton,vsyncOverTimes

    def _calculator_thread(self, start_time):
        '''處理surfaceflinger數據
        '''
        while True:
            try:
                data = self.data_queue.get()
                if isinstance(data, str) and data == 'Stop':
                    break
                refresh_time = int(data[0])
                timestamps = data[1]
                fps, jank_list, caton,cpukel,memory,cpu_usage,sys_cpu,_flow_d,_flow_u,temperature,battery,drawcall,device_id,device_os,device_model = self._calculate_results(timestamps)
                fps_info = FpsInfo(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(refresh_time)), len(timestamps),
                                   fps,self.package_name, self.focus_window, jank_list, len(jank_list), caton,cpukel,memory,cpu_usage,sys_cpu,_flow_d,_flow_u,temperature,battery,drawcall,device_id,device_os,device_model)
                self.listener.report_fps_info(fps_info)
            except Exception as  e:
                print(e)
                print("計算fps數據異常")
                self.data_queue.put('Stop')
                if self.calculator_thread:
                   self.stop_event.set()
                   self.calculator_thread = None
                return

    def _collector_thread(self):
        '''收集FPS數據
        shell dumpsys gfxinfo 《 window》 framestats
        '''
        last_refresh_time = 0
        while not self.stop_event.is_set():
            # 此處進行抓取，並將數據存放在data_quue裏
            try:
                before = time.time()
                self.get_focus_window()
                new_timestamps, now_refresh_time = self._get_fps_data()
                # 檢查是否獲取數據成功
                if now_refresh_time is None or new_timestamps is None:
                    # 清除數據後，沒做介面操作，所以會拿不到數據，因此跳過，我們擷取下一次的數據
                    continue
                # 大于则证明有帧信息刷新，无则不需要更新信息
                if self.last_timestamp > last_refresh_time:
                    last_refresh_time = self.last_timestamp
                    # print(last_refresh_time)
                    self.data_queue.put((now_refresh_time, new_timestamps))
                time_consume = time.time() - before
                delta_inter = self.frequency - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as  e:
                print("獲取fps數據異常")
                print(e)
                self.data_queue.put('Stop')
                if self.collector_thread:
                    self.stop_event.set()
                    self.collector_thread = None
                return
        if self.stop_event.is_set():
            self.data_queue.put('Stop')

    def _clear_fps_data(self):
        os.popen("adb -s " + self.device + " shell dumpsys gfxinfo " + self.package_name + " reset")
        # 清除fps數據
        print("已經清除FPS數據，請3秒後開始滑動界面")
        time.sleep(2)

    def _get_fps_data(self):
        """
        isHaveFoundWindow  當前活動窗口的app
        total_frames 總幀數
        timestamps  每幀的訊息
        :rtype:
        :return:
        """
        results = os.popen("adb -s " + self.device + " shell dumpsys gfxinfo " + self.package_name + " framestats")
        phone_time = os.popen("adb -s " + self.device + " shell date +%s")
        phone_time = phone_time.readlines()[0]
        # print(phone_time)
        timestamps = []
        each_frame_timestamps = []
        isHaveFoundWindow = False
        PROFILEDATA_line = 0
        # 行数代表当前窗口总帧数，列数是每帧耗时详细信息
        # 只獲取當前窗口的資訊
        for line in results.readlines():
            #print("test" + line)
            if "Window" in line and self.focus_window in line:
                isHaveFoundWindow = True
                # print("focus Window is :" + line)
                continue
            if isHaveFoundWindow and "---PROFILEDATA---" in line:
                PROFILEDATA_line += 1
                #print(PROFILEDATA_line)
                continue
            if isHaveFoundWindow and "Flags,IntendedVsync," in line:
                continue
            if isHaveFoundWindow and PROFILEDATA_line is 1:
                # 此處代表的是當前活動窗口
                # 我們取PROFILEDATA中間的數據 最多128幀，還可能包含之前重複的幀，所以我們間隔1.5s就取一次數據
                fields = []
                fields = line.split(",")
                each_frame_timestamp = [float(fields[1]), float(fields[13])]
                each_frame_timestamps.append(each_frame_timestamp)
                continue
            if PROFILEDATA_line >= 2:
                break
        # 除去重複的幀，通過每幀的起始時間去判斷是否重覆
        for timestamp in each_frame_timestamps:
            if timestamp[0] > self.last_timestamp:
                timestamps.append((timestamp[1] - timestamp[0]) / 1000000)
                self.last_timestamp = timestamp[0]

        return timestamps, int(phone_time)

    def run_adb(cmd):
        return os.popen(cmd)

if __name__ == '__main__':

    # 設備device id 
    sn = FPSMonitor.get_deviceid()
    monitor = FPSMonitor(sn)

    lisenter = FpsListenserImpl()
    monitor.set_listener(lisenter)

    # 測試時間 單位:秒
    monitor.start(time.time())
    time.sleep(1800)
    monitor.stop()

#!/usr/bin/env python