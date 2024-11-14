#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time        : 2024/11/15 1:09
@Author      : SiYuan
@Email       : 863909694@qq.com
@File        : TraceBoard-keyboard.py
@Description :
"""
import requests
from pynput.keyboard import Key
from pynput import keyboard
import datetime

# 用于追踪已按下的键
pressed_keys = set()


# 插入按键信息到数据库
def insert_key_event(key_name: str, virtual_key_code: int):
    # 获取当前时间戳
    timestamp = datetime.datetime.now()
    print(key_name, virtual_key_code)
    # API URL
    url = "http://127.0.0.1:21315/key_events"

    # 要发送的数据
    data = {
        "key_name": key_name,  # 按键名称
        "virtual_key_code": virtual_key_code  # 虚拟按键码
    }

    # 发送 POST 请求
    response = requests.post(url, json=data)

    # 打印响应内容
    if response.status_code == 200:
        print("请求成功！响应数据:")
        print(response.json())  # 打印响应 JSON 数据
    else:
        print(f"请求失败! 状态码: {response.status_code}")
        print(response.text)


# 键盘按下事件处理函数
def on_press(key):
    try:
        if isinstance(key, Key):
            vk = key.value.vk
        else:
            vk = key.vk
        key_name = '-'
        # 只在按键没有被记录时记录它
        if vk not in pressed_keys:
            insert_key_event(key_name, vk)
            pressed_keys.add(vk)  # 记录按下的按键
    except Exception as e:
        print(f"Error: {e}")


# 键盘释放事件处理函数
def on_release(key):
    try:
        if isinstance(key, Key):
            vk = key.value.vk
        else:
            vk = key.vk
        # 按键释放时移除按键
        if vk in pressed_keys:
            pressed_keys.remove(vk)
    except Exception as e:
        print(f"Error: {e}")


def start_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == '__main__':
    start_listener()
