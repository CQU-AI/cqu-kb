import sys

from cqu_kb.config.config import config, Config
from cqu_kb.utils import check_user, log, check_output_path
from cqu_kb.version import __version__
from cqu_kb.core import get_cal, get_payload

from cqujwc import Student


def main():
    username, password = check_user()
    check_output_path()

    student = Student(
        username=username,
        password=password,
        server=0,
        proxies=None
    )

    cal = get_cal(
        student.post(
            url="/znpk/Pri_StuSel_rpt.aspx",
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            data=get_payload(student)
        ).content
    )

    with open(config["output"]["path"], 'wb') as f:
        f.write(cal.to_ical())

    log(f'课表已经保存到{config["output"]["path"]}')


def console_main():
    import argparse

    def parse_args() -> argparse.Namespace:
        """Parse the command line arguments for the `cqu jwc` binary.

        :return: Namespace with parsed arguments.
        """
        parser = argparse.ArgumentParser(prog="kb", description="第三方 重庆大学 课表导出工具", )

        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"CQU_kb {__version__}",
            help="显示版本号",
        )
        parser.add_argument(
            "-c",
            "--config_path",
            help="查询配置文件路径",
            action="store_true",
        )
        parser.add_argument(
            "-r", "--reset", help="重置配置项", action="store_true",
        )
        parser.add_argument(
            "-u",
            "--username",
            help="学号",
            type=int,
            default=config["user_info"]["username"],
        )
        parser.add_argument(
            "-p",
            "--password",
            help="密码",
            type=str,
            default=config["user_info"]["password"],
        )
        parser.add_argument(
            "-o",
            "--output",
            help="课表输出路径",
            type=str,
            default=config['output']['path'],
        )
        return parser.parse_args()

    args = parse_args()
    if args.reset:
        Config.reset()
        log("已重置配置文件")
    if args.config_path:
        log(f"配置文件位于 {Config.path}\n")
        sys.exit()

    config.dump()

    main()


if __name__ == '__main__':
    main()
