#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time        : 2024/11/15 1:05
@Author      : SiYuan
@Email       : 863909694@qq.com
@File        : TraceBoard-app.py
@Description :
"""

import os
import sys
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, time

from utils.generate_serial import generate_serial

# 设备编码
mac_serial = generate_serial()

# SQLAlchemy 数据库设置
DATABASE_URL = "sqlite:///./key_events.db"  # SQLite 数据库路径

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 基类
Base = declarative_base()


# 定义按键事件记录表模型
class KeyEvent(Base):
    __tablename__ = "key_events"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, index=True)
    virtual_key_code = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class MacSerial(Base):
    __tablename__ = "mac_serial"

    id = Column(Integer, primary_key=True, index=True)
    serial = Column(String, index=True, unique=True)
    nickname = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


# 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

# 创建 SessionLocal 作为数据库会话的创建器
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

try:
    # 动态获取静态文件目录路径
    static_dir = os.path.join(sys._MEIPASS, "static") if getattr(sys, 'frozen', False) else "static"
    # 挂载静态文件目录，用于提供 HTML 和其他静态文件
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
except:
    # 动态获取静态文件目录路径
    static_dir = os.path.join(sys._MEIPASS, 'server', "static") if getattr(sys, 'frozen', False) else "./server/static"
    # 挂载静态文件目录，用于提供 HTML 和其他静态文件
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 返回 HTML 页面
@app.get("/", response_class=HTMLResponse)
async def read_dashboard():
    with open(os.path.join(static_dir, 'index.html'), "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200, )


# 定义按键统计数据模型
class KeyCount(BaseModel):
    key_name: str
    count: int
    virtual_key_code: int


# 获取所有按键统计数据
@app.get("/key_counts")
def get_key_counts():
    # 创建一个新的数据库会话
    db = SessionLocal()
    try:
        # 查询数据库获取按键统计数据
        results_total = db.query(KeyEvent.key_name, KeyEvent.virtual_key_code, func.count(KeyEvent.virtual_key_code)) \
            .group_by(KeyEvent.virtual_key_code).all()

        today_midnight = datetime.combine(datetime.today(), time.min)
        today_count_data = db.query(KeyEvent.virtual_key_code, func.count(KeyEvent.virtual_key_code)) \
            .filter(KeyEvent.timestamp >= today_midnight).group_by(KeyEvent.virtual_key_code).all()

        today_count_data = {str(row[0]): row[1] for row in today_count_data}
        # print(today_count_data)
        today_count = sum(today_count_data.values())
        # print(today_count)
        result_total_list = [{"key_name": row[0], "count": row[2], 'virtual_key_code': row[1],
                              "today_count": today_count_data.get(str(row[1]), 0)
                              }
                             for row in results_total]
        # print(result_total_list)
        result_total_list.sort(key=lambda x: x['today_count'], reverse=True)

        new_serial = db.query(MacSerial).filter(MacSerial.serial == mac_serial).first()
        nickname = new_serial.nickname if new_serial else "佚名"
        # 额外增加的顶层字段
        extra_data = {
            "status": "200",
            "message": "successfully",
            "nickname": nickname,
            "macSerial": mac_serial,
            "todayCount": today_count,
            "data": result_total_list  # 原列表数据保持不变
        }
        return extra_data
    except Exception as e:
        print(f"Error retrieving key counts: {str(e)}")
        return {
            "status": "error",
            "message": f"Error retrieving key counts: {str(e)}",
            "data": {}  # 错误时返回空列表
        }
    finally:
        db.close()


# 定义用于插入按键事件的请求模型
class KeyEventCreate(BaseModel):
    key_name: str
    virtual_key_code: int


# 插入按键事件数据
@app.post("/key_events", response_model=KeyEventCreate)
def create_key_event(key_event: KeyEventCreate):
    db = SessionLocal()
    try:
        # 创建一个新的 KeyEvent 实体
        new_event = KeyEvent(
            key_name=key_event.key_name,
            virtual_key_code=key_event.virtual_key_code,
            timestamp=datetime.now()
        )

        # 将新的事件插入到数据库
        db.add(new_event)
        db.commit()  # 提交事务
        db.refresh(new_event)  # 刷新以获取生成的 ID 等信息

        return new_event  # 返回插入的数据
    except Exception as e:
        db.rollback()  # 如果发生错误，回滚事务
        raise HTTPException(status_code=400, detail=f"Error inserting data: {str(e)}")
    finally:
        db.close()


# 定义用于保存用户昵称的请求模型
class MacSerialCreate(BaseModel):
    nickname: str


@app.post("/save_nickname")
async def save_nickname(save_nickname: MacSerialCreate):
    db = SessionLocal()
    try:
        new_serial = db.query(MacSerial).filter(MacSerial.serial == mac_serial).first()
        if not new_serial:
            # 创建一个新的 MacSerial 实体
            new_serial = MacSerial(
                nickname=save_nickname.nickname,
                serial=mac_serial,
                timestamp=datetime.now()
            )
            # 将新的事件插入到数据库
            db.add(new_serial)
        else:
            new_serial.nickname = save_nickname.nickname

        db.commit()  # 提交事务
        db.refresh(new_serial)  # 刷新以获取生成的 ID 等信息
        return {"nickname": save_nickname.nickname, "serial": mac_serial}  # 返回插入的数据
    except Exception as e:
        db.rollback()  # 如果发生错误，回滚事务
        raise HTTPException(status_code=400, detail=f"Error inserting data1: {str(e)}")
    finally:
        db.close()


# 如果是直接运行此脚本，可以进行一些初始化的操作，但 FastAPI 不需要在此处运行。
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=21315)
