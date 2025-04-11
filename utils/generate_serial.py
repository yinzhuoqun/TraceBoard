#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: yinzhuoqun
@site: http://zhuoqun.info/
@email: yin@zhuoqun.info
@time: 2025/4/9 17:15
"""

import platform
# import psutil
# pip install pypiwin32
import win32com.client
import hashlib
import uuid


def get_system_info():
    # 获取CPU核心数（通过WMI）
    def get_cpu_cores():
        wmi = win32com.client.GetObject("winmgmts:")
        processors = wmi.ExecQuery("SELECT NumberOfCores, NumberOfLogicalProcessors FROM Win32_Processor")
        physical = total = 0
        for cpu in processors:
            physical += int(cpu.NumberOfCores)
            total += int(cpu.NumberOfLogicalProcessors)
        return physical, total

    physical_cores, total_cores = get_cpu_cores()
    info = {
        'system': platform.system(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        # 'physical_cores': psutil.cpu_count(logical=False),
        # 'total_cores': psutil.cpu_count(logical=True),
        'physical_cores': physical_cores,
        'total_cores': total_cores,
        'disk_serial': None,
        'mac_address': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                 for elements in range(0, 8 * 6, 8)][::-1]).upper()
    }

    # 尝试获取磁盘序列号
    try:
        if platform.system() == 'Windows':
            # pip install wmi
            import wmi
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                info['disk_serial'] = disk.SerialNumber.replace(" ", "")
                break
        elif platform.system() == 'Linux':
            # Linux下获取磁盘序列号的方法
            pass
    except Exception as e:
        print(f"WMI查询失败: {e}")

    return info


def generate_serial():
    info = get_system_info()
    combined = ''.join([str(v) for v in info.values() if v])
    serial = hashlib.sha256(combined.encode()).hexdigest().upper()
    return '-'.join([serial[i:i + 5] for i in range(0, 25, 5)])


if __name__ == '__main__':
    try:
        print("跨平台序列号:", generate_serial())
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(str(e))
        input("按回车退出...")  # 防止窗口立即关闭
