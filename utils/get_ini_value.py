#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: yinzhuoqun
@site: http://zhuoqun.info/
@email: yin@zhuoqun.info
@time: 2025/4/9 17:52
"""

import configparser


class Config:
    def __init__(self, file_path='../config.ini'):
        self.file_path = file_path

    def read_config(self, section='local'):
        # 创建ConfigParser对象
        config = configparser.ConfigParser()
        config.read(self.file_path, encoding='utf-8')
        return {i[0]: i[1] for i in config.items(section)}


if __name__ == '__main__':
    config = Config().read_config()
    print(config)
