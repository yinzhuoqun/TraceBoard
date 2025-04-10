#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time        : 2024/11/15 1:09
@Author      : SiYuan
@Email       : 863909694@qq.com
@File        : TraceBoard-keyboard.py
@Description :
"""

import datetime
import requests
from pynput.keyboard import Key, Listener as KeyboardListener

from utils.get_ini_value import Config

config = Config("config.ini").read_config()

server_host = config.get("server_host")
server_port = config.get("server_port")

# 全局变量
pressed_keys = set()


# 插入按键信息到数据库
def insert_key_event(key_name: str, virtual_key_code: int):
    timestamp = datetime.datetime.now()
    url = f"http://127.0.0.1:{server_port}/key_events"
    data = {
        "key_name": key_name,
        "virtual_key_code": virtual_key_code
    }
    try:
        response = requests.post(url, json=data, timeout=5)  # 设置超时时间为5秒
        if response.status_code == 200:
            print(f"请求成功！响应数据：{response.json()}")
        else:
            print(f"请求失败! 状态码: {response.status_code}, 响应内容: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")


# 获取按键的虚拟键码
def get_virtual_key_code(key):
    if isinstance(key, Key):
        return key.value.vk
    return key.vk


# 键盘按下事件处理函数
def on_press(key):
    try:
        vk = get_virtual_key_code(key)
        key_name = str(key).replace("'", "") if not isinstance(key, Key) else key.name
        if vk not in pressed_keys:
            insert_key_event(key_name, vk)
            pressed_keys.add(vk)  # 记录按下的按键
    except Exception as e:
        print(f"Error in on_press: {e}")


# 键盘释放事件处理函数
def on_release(key):
    try:
        vk = get_virtual_key_code(key)
        if vk in pressed_keys:
            pressed_keys.remove(vk)  # 移除释放的按键
    except Exception as e:
        print(f"Error in on_release: {e}")


# 启动监听器
def start_listener():
    with KeyboardListener(on_press=on_press, on_release=on_release) as keyboard_listener:
        keyboard_listener.join()


if __name__ == '__main__':
    start_listener()
