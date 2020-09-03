import re
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import requests

from cqu_kb.config.config import config
from cqu_kb.version import __version__

ERROR_COUNT = 0


def check_output_path():
    if config['output']['path'] is None:
        flag = False
        for i in ["Desktop", "桌面", "desktop"]:
            if (Path.home() / i).is_dir():
                flag = True
                break
        if flag:
            config['output']['path'] = Path.home() / i / "课表.ics"
        else:
            config['output']['path'] = Path("./课表.ics").absolute()


def exit():
    print("[{}]  遭遇不可抗的错误，程序完全退出".format(datetime.now()))
    sys.exit(1)


def log(msg, error=False, warning=False):
    global ERROR_COUNT
    if error:
        print("[{}]  {} - {}".format(datetime.now(), msg, ERROR_COUNT))
        if config["behavior"]["print_traceback"]:
            traceback.print_exc()
        time.sleep(min(2 ** ERROR_COUNT, config["behavior"]["exp_backoff_limit"]))
        ERROR_COUNT += 1
    elif warning:
        print("[{}]  {}".format(datetime.now(), msg))
    else:
        print("[{}]  {}".format(datetime.now(), msg))
        reset_error_count()


def reset_error_count():
    global ERROR_COUNT
    ERROR_COUNT = 0


def check_user():
    if (
            config["user_info"]["username"] is None
            or config["user_info"]["password"] is None
    ):
        print("未找到有效的帐号和密码，请输入你的帐号和密码，它们将被保存在你的电脑上以备下次使用")
        try:
            config["user_info"]["username"] = input("帐号>>>")
            config["user_info"]["password"] = input("密码>>>")
        except (KeyboardInterrupt, EOFError):
            log("需要输入你的帐号和密码，它们将被保存在你的电脑上以备下次使用")
            exit()
        config.dump()
    return config["user_info"]["username"], config["user_info"]["password"]


def check_update(project_name):
    content = requests.get(f"https://pypi.org/project/{project_name}/").content.decode()
    latest_version = re.findall(project_name + r" \d{1,2}\.\d{1,2}\.\d{1,2}", content)[
        0
    ].lstrip(project_name + " ")
    if latest_version.split(".") > __version__.split("."):
        log(
            f"{project_name}的最新版本为{latest_version}，当前安装的是{__version__}，建议使用`pip install {project_name} -U`来升级",
            warning=True,
        )
