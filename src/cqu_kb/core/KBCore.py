import uuid
from abc import abstractmethod, ABC
from datetime import datetime, timedelta

import pytz
from icalendar import Calendar, Event
from icalendar import Timezone, vDDDTypes

from cqu_kb.config import config


class KBCore(ABC):
    def __init__(self, username, password):
        self.password = password
        self.username = username

    @abstractmethod
    def _get_payload(self, **kwargs):
        pass

    @abstractmethod
    def main(self):
        pass

    @abstractmethod
    def get_course_info(self, page_content):
        pass

    @staticmethod
    def _add_datetime(component, name, time):
        vdatetime = vDDDTypes(time)
        if "VALUE" in vdatetime.params and "TZID" in vdatetime.params:
            vdatetime.params.pop("VALUE")
        component.add(name, vdatetime)

    def get_cal(self, course_info):
        chinese_to_numbers = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6}

        coursenum_to_time = {
            "1": (timedelta(hours=8, minutes=30), timedelta(hours=9, minutes=15)),
            "2": (timedelta(hours=9, minutes=25), timedelta(hours=10, minutes=10)),
            "3": (timedelta(hours=10, minutes=30), timedelta(hours=11, minutes=15)),
            "4": (timedelta(hours=11, minutes=25), timedelta(hours=12, minutes=10)),
            "5": (timedelta(hours=13, minutes=30), timedelta(hours=14, minutes=15)),
            "6": (timedelta(hours=14, minutes=25), timedelta(hours=15, minutes=10)),
            "7": (timedelta(hours=15, minutes=20), timedelta(hours=16, minutes=5)),
            "8": (timedelta(hours=16, minutes=25), timedelta(hours=17, minutes=10)),
            "9": (timedelta(hours=17, minutes=20), timedelta(hours=18, minutes=5)),
            "10": (timedelta(hours=19, minutes=0), timedelta(hours=19, minutes=45)),
            "11": (timedelta(hours=19, minutes=55), timedelta(hours=20, minutes=40)),
            "12": (timedelta(hours=20, minutes=50), timedelta(hours=21, minutes=35)),
            "13": (timedelta(hours=21, minutes=45), timedelta(hours=22, minutes=30)),
        }

        term_start_time = datetime(
            year=int(config["term_start_time"]["year"]),
            month=int(config["term_start_time"]["month"]),
            day=int(config["term_start_time"]["day"]),
            tzinfo=pytz.timezone("Asia/Shanghai"),
        )

        events = []

        for course in course_info:
            week_nums = []
            week_segs = course["weeks"].split(",")
            for seg in week_segs:
                delimiter = [int(i) for i in seg.split("-")]
                start = delimiter[0]
                end = delimiter[1] if len(delimiter) == 2 else start
                for i in range(start, end + 1):
                    week_nums.append(i)
            if not course["time"].split("[")[0].isdigit():
                day = chinese_to_numbers[course["time"].split("[")[0]]
            else:
                day = int(course["time"].split("[")[0])
            seg = course["time"].split("[")[1].split("-")
            if len(seg) == 2:
                inweek_delta_start = timedelta(days=day) + coursenum_to_time[seg[0]][0]
                inweek_delta_end = timedelta(days=day) + coursenum_to_time[seg[1]][1]
                for week_num in week_nums:
                    event_start_datetime = (
                        term_start_time
                        + (week_num - 1) * timedelta(days=7)
                        + inweek_delta_start
                    )
                    event_end_datetime = (
                        term_start_time
                        + (week_num - 1) * timedelta(days=7)
                        + inweek_delta_end
                    )
                    event = Event()
                    event.add(
                        "summary",
                        "[{}]{}".format(course["teacher"], course["course_name"]),
                    )
                    event.add("location", course["location"])
                    self._add_datetime(event, "dtstart", event_start_datetime)
                    self._add_datetime(event, "dtend", event_end_datetime)
                    # Fix #2: 添加 dtstamp 与 uid 属性
                    event.add("dtstamp", datetime.utcnow())
                    namespace = uuid.UUID(
                        bytes=int(event_start_datetime.timestamp()).to_bytes(
                            length=8, byteorder="big"
                        )
                        + int(event_end_datetime.timestamp()).to_bytes(
                            length=8, byteorder="big"
                        )
                    )
                    event.add(
                        "uid",
                        uuid.uuid3(
                            namespace, f"{course['course_name']}-{course['teacher']}"
                        ),
                    )

                    events.append(event)

        cal = Calendar()
        cal.add(
            "prodid",
            f'-//重庆大学课表//{config["user_info"]["username"]}//Powered By cqu-kb//',
        )
        cal.add("version", "2.0")
        cal.add_component(
            Timezone.from_ical(
                "BEGIN:VTIMEZONE\n"
                "TZID:Asia/Shanghai\n"
                "X-LIC-LOCATION:Asia/Shanghai\n"
                "BEGIN:STANDARD\n"
                "TZNAME:CST\n"
                "DTSTART:16010101T000000\n"
                "TZOFFSETFROM:+0800\n"
                "TZOFFSETTO:+0800\n"
                "END:STANDARD\n"
                "END:VTIMEZONE\n"
            )
        )
        for event in events:
            cal.add_component(event)
        return cal
