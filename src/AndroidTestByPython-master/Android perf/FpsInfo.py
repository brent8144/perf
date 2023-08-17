#!/usr/bin/env python
# coding:utf-8
"""
Name : FpsInfo.py
Author  :
Contect : 
Time    : 2020/7/21 14:26
Desc:
"""


class FpsInfo(object):
    def __init__(self, time, total_frames, fps, pkg_name, window_name, jankys_ary, jankys_more_than_16,
                 jankys_more_than_166,cpukel,memory,cpu_usage,sys_cpu,_flow_d,_flow_u,temperature,battery,drawcall,device_id,device_os,device_model):
        # device model
        self.device_model = device_model
        # device id
        self.device_id = device_id
        # device os
        self.device_os = device_os
        # 獲取fps時間
        self.time = time
        # 2s内取到總幀數
        self.total_frames = total_frames
        # fps
        self.fps = fps
        # 應用程式包名
        self.pkg_name = pkg_name
        # 窗口名
        self.window_name = window_name
        # 掉幀具體時間
        self.jankys_ary = jankys_ary
        # 掉幀數 > 16.67ms
        self.jankys_more_than_16 = jankys_more_than_16
        # 卡頓次數 > 166.7ms
        self.jankys_more_than_166 = jankys_more_than_166
        # cpu核心數目
        self.cpukel = cpukel
        # memory
        self.memory = memory
        # cpu
        self.cpu_usage = cpu_usage
        # sys_cpu
        self.sys_cpu = sys_cpu
        # wifi 下載流量
        self._flow_d = _flow_d
        # wifi 上傳流量
        self._flow_u = _flow_u
        # 溫度
        self.temperature = temperature
        # 剩餘電量
        self.battery = battery
        # drawcall
        self.drawcall = drawcall
   