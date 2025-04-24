# TraceBoard  一个统计键盘使用情况的小工具

## 功能介绍

可视化键盘按键使用情况

![img.png](doc/image/tracboard_use.gif)

## 下载与使用

Windows 用户可以直接 [点击下载](https://github.com/yinzhuoqun/TraceBoard/releases) 的 exe 可执行文件，直接双击就能运行。其他系统用户可以自行 编译/运行 源码

### python 环境

Python3

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行 main.py

```bash
python main.py
```

## 感谢

[键盘UI](https://yanyunfeng.com/article/41)

## 打包成 exe

#### 安装 pyinstaller

`pip install pyinstaller`

#### 打包的文件信息

`file_version_info.txt`

#### 打包命令

`pyinstaller --onefile --noconsole --add-data "server/static;server/static" --hidden-import=win32com --hidden-import=win32api --icon=./server/static/logo3.0.ico --name="TraceBoard" --version-file file_version_info.txt main.py`

## 加入排行榜
数据都是存在本地同项目下的 `key_events.db` 文件中，当天使用键盘的总数通过接口上传到公有服务加入排行榜排名

#### 排行榜接口信息
公有接口：http://zhuoqun.zone:5000/trace_board_data/

js 位置: server/static/index.js 的 get_rank_list() 的 joinRankUrl

