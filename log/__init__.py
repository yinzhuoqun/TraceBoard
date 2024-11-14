#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time        : 2024/11/15 0:58 
@Author      : SiYuan 
@Email       : 863909694@qq.com 
@File        : TraceBoard-__init__.py.py 
@Description : 
"""
import logging

# 配置日志记录
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# 在 FastAPI 应用中记录日志
logger.info("FastAPI app is starting.")

if __name__ == '__main__':
    pass
