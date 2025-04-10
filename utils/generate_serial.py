#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: yinzhuoqun
@site: http://zhuoqun.info/
@email: yin@zhuoqun.info
@time: 2025/4/9 17:15
"""

import platform
import psutil
import hashlib
import uuid


def get_system_info():
    info = {
        'system': platform.system(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'physical_cores': psutil.cpu_count(logical=False),
        'total_cores': psutil.cpu_count(logical=True),
        'disk_serial': None,
        'mac_address': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                 for elements in range(0, 8 * 6, 8)][::-1]).upper()
    }

    # 尝试获取磁盘序列号
    try:
        if platform.system() == 'Windows':
            import wmi
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                info['disk_serial'] = disk.SerialNumber.replace(" ", "")
                break
        elif platform.system() == 'Linux':
            # Linux下获取磁盘序列号的方法
            pass
    except:
        pass

    return info


def generate_serial():
    info = get_system_info()
    combined = ''.join([str(v) for v in info.values() if v])
    serial = hashlib.sha256(combined.encode()).hexdigest().upper()
    return '-'.join([serial[i:i + 5] for i in range(0, 25, 5)])


if __name__ == '__main__':
    print("跨平台序列号:", generate_serial())
