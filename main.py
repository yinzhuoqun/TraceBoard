#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time        : 2024/11/13 23:16 
@Author      : SiYuan 
@Email       : 863909694@qq.com 
@File        : TraceBoard-main.py 
@Description : 
"""

import datetime
import os
import sqlite3
import sys
import logging

from pydantic import BaseModel
from pynput import keyboard
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import threading
import webbrowser
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

from pynput.keyboard import Key
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from uvicorn import Config, Server

# 配置日志记录
logging.basicConfig(filename="app.log",level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
# 在 FastAPI 应用中记录日志
logger.info("FastAPI app is starting.")
# 初始化数据库
# 初始化数据库连接
conn = sqlite3.connect("key_events.db", check_same_thread=False)
cursor = conn.cursor()

# 创建按键事件记录表（虚拟键码、按键名称、时间戳）
cursor.execute('''CREATE TABLE IF NOT EXISTS key_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_name TEXT NOT NULL,
                    virtual_key_code INTEGER NOT NULL,
                    timestamp DATETIME
                  )''')
conn.commit()


# 插入按键信息到数据库
def insert_key_event(key_name: str, virtual_key_code: int):
    # 获取当前时间戳
    timestamp = datetime.datetime.now()

    print(key_name, virtual_key_code)
    # 插入记录到数据库
    cursor.execute('''
        INSERT INTO key_events (key_name, virtual_key_code, timestamp)
        VALUES (?, ?, ?)
    ''', (key_name, virtual_key_code, timestamp))
    conn.commit()


# 键盘按下事件处理函数
def on_press(key):
    try:
        if isinstance(key, Key):
            vk = key.value.vk
        else:
            vk = key.vk
        key_name = '-'
        if vk == 160:
            key_name = 'left'
        elif vk == 161:
            key_name = 'right'
        insert_key_event(key_name, vk)
    except Exception as e:
        print(f"Error: {e}")


#
# 启动键盘监听
# listener = keyboard.Listener(on_press=on_press)
# listener.start()
def start_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


# FastAPI 应用
app = FastAPI()

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 动态获取静态文件目录路径
static_dir = os.path.join(sys._MEIPASS, "static") if getattr(sys, 'frozen', False) else "static"

# 挂载静态文件目录，用于提供 HTML 和其他静态文件
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 定义按键统计数据模型
class KeyCount(BaseModel):
    key_name: str
    count: int
    virtual_key_code: int


# 返回 HTML 页面
@app.get("/", response_class=HTMLResponse)
async def read_dashboard():
    with open(os.path.join(static_dir, 'index.html'), "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)


# 获取所有按键统计数据
@app.get("/key_counts", response_model=List[KeyCount])
def get_key_counts():
    cursor.execute(
        "SELECT key_name, count(virtual_key_code),virtual_key_code FROM key_events GROUP BY virtual_key_code")
    rows = cursor.fetchall()
    return [{"key_name": row[0], "count": row[1], 'virtual_key_code': row[2]} for row in rows]


# 启动键盘监听的同时运行FastAPI服务器
def start_api():
    # import uvicorn
    # uvicorn.run(app, host="127.0.0.1", port=21315)
    log_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {
            "file_handler": {
                "class": "logging.FileHandler",
                "filename": "app.log",
            },
        },
        "root": {
            "handlers": ["file_handler"],
            "level": "INFO",
        },
    }
    config = Config(app=app, host="127.0.0.1", port=21315, log_config=log_config)
    server = Server(config=config)
    server.run()

# 创建托盘图标图像
def create_image(width: int, height: int, color1, color2):
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        [(width // 4, height // 4), (width * 3 // 4, height * 3 // 4)], fill=color2
    )
    image = Image.open(os.path.join(static_dir, 'logo3.0.ico'))
    return image


# 托盘图标菜单
def setup_tray_icon():
    icon_image = create_image(64, 64, "black", "white")
    tray_icon = Icon("Keyboard Monitor", icon_image, menu=Menu(
        MenuItem("Open Dashboard", open_dashboard),
        MenuItem("Exit", exit_app)
    ))
    tray_icon.run()


# 打开前端 HTML 页面
def open_dashboard(icon, item):
    webbrowser.open("http://127.0.0.1:21315/")


# 退出程序
def exit_app(icon, item):
    icon.stop()
    conn.close()
    os._exit(0)


# 主线程启动
if __name__ == "__main__":
    # 启动键盘监听器和 API 服务器
    threading.Thread(target=start_listener).start()
    threading.Thread(target=start_api).start()
    webbrowser.open("http://127.0.0.1:21315/")
    # 设置托盘图标
    setup_tray_icon()
