# cqu-kb

[![cqu-tool-bucket](https://img.shields.io/badge/CQU-%E9%87%8D%E5%BA%86%E5%A4%A7%E5%AD%A6%E5%85%A8%E5%AE%B6%E6%A1%B6%E8%AE%A1%E5%88%92-blue)](https://github.com/topics/cqu-tool-bucket)
![Liscence](https://img.shields.io/github/license/CQU-AI/cqu-kb)
[![pypi](https://img.shields.io/pypi/v/cqu-kb)](https://pypi.org/project/cqu-kb/)
![download](https://pepy.tech/badge/cqu-kb)
![Upload Python Package](https://github.com/CQU-AI/cqu-kb/workflows/Upload%20Python%20Package/badge.svg)

cqu-kb 是一个基于python3的，导出重庆大学课程表的第三方工具。


## 1. 安装和使用

本项目有两种使用方式，直接订阅和自行安装配置。

### 1.1. 订阅使用

访问`http://cal.loopy.tech/{你的学号}/{教务网密码}`即可下载你的课程表日历文件，同时也可直接在日历软件中订阅该地址。

例如，如果你的学号是`20170006`,教务网密码为`qazwsx`，则你的课程表就在`http://cal.loopy.tech/20170006/qazwsx`


### 1.2. 安装使用

1. 安装Python
2. 安装cqu-cj：`pip install cqu-kb`
3. 在命令行中输入`cqu-kb`即可开始运行
4. 首次运行，需要输入学号和教务网密码
5. 运行成功后，课表将被保存到桌面的`课表.ics`文件中。
6. 将`课表.ics`导入你的日历软件

帐号和密码会存储在你的电脑上，如需清除记录，可使用`cqu-kb -r`

## 2. 声明

1. 本程序开放源代码，可自行检查是否窃取你的信息。
2. 本程序不存储用户的帐号，密码。
3. 本程序不存储任何人的课表，所有的数据来自于重庆大学教务网。
4. 本程序依赖于`CQU-JWC`