from datetime import datetime, timedelta
from urllib import parse

import pytz
from bs4 import BeautifulSoup as BS
from icalendar import Calendar, Event

from cqu_kb.config import config


def get_payload(student):
    """
    This function prepares the payload to be sent in HTTP POST method. There are three main fields in the payload. The
    only thing that should be paid attention to is "Sel_XNXQ" field, which denotes the years（学年） and terms（学期）.

    :param student: an instance of Student from cqu-jxgl
    :return: payload to be used in HTTP POST
    """
    # First Get. Won't get any information but a cookie.
    response = student.get("/znpk/Pri_StuSel.aspx")
    soup = BS(response.content, features="html.parser")
    return parse.urlencode({
        "Sel_XNXQ": soup.find("option")['value'],
        "rad": "on",
        "px": "1",
    })


def get_cal(page_content):
    soup = BS(page_content, features="html.parser")
    tables = soup.find_all(class_="page_table")

    courses_info = []
    for i in range(len(tables) // 2):
        table = tables[i * 2 + 1]
        rows = table.find('tbody').find_all('tr')
        cols_num = len(rows[0].find_all('td'))
        for row in rows:
            course_info = {}
            cols = row.find_all('td')
            course_info.update({'course_name': cols[1].text.split(']')[-1] + ("" if cols_num == 13 else "（实验）")})
            course_info.update({'teacher': cols[
                -4 if cols_num == 13 else -5
            ].text})
            course_info.update({'weeks': cols[-3].text})
            course_info.update({'time': cols[-2].text.replace('节]', '')})
            course_info.update({'location': cols[-1].text})
            courses_info.append(course_info)
    for i in range(len(courses_info)):
        if courses_info[i]['course_name'] == '' or courses_info[i]['course_name'] == '（实验）':
            courses_info[i]['course_name'] = courses_info[i - 1]['course_name']

    chinese_to_numbers = {
        '一': 0,
        '二': 1,
        '三': 2,
        '四': 3,
        '五': 4,
        '六': 5,
        '日': 6
    }

    coursenum_to_time = {
        '1': (timedelta(hours=8, minutes=30), timedelta(hours=9, minutes=15)),
        '2': (timedelta(hours=9, minutes=25), timedelta(hours=10, minutes=10)),
        '3': (timedelta(hours=10, minutes=30), timedelta(hours=11, minutes=15)),
        '4': (timedelta(hours=11, minutes=25), timedelta(hours=12, minutes=10)),
        '5': (timedelta(hours=13, minutes=30), timedelta(hours=14, minutes=15)),
        '6': (timedelta(hours=14, minutes=25), timedelta(hours=15, minutes=10)),
        '7': (timedelta(hours=15, minutes=20), timedelta(hours=16, minutes=5)),
        '8': (timedelta(hours=16, minutes=25), timedelta(hours=17, minutes=10)),
        '9': (timedelta(hours=17, minutes=20), timedelta(hours=18, minutes=5)),
        '10': (timedelta(hours=19, minutes=0), timedelta(hours=19, minutes=45)),
        '11': (timedelta(hours=19, minutes=55), timedelta(hours=20, minutes=40)),
        '12': (timedelta(hours=20, minutes=50), timedelta(hours=21, minutes=35)),
        '13': (timedelta(hours=21, minutes=45), timedelta(hours=22, minutes=30)),
    }

    term_start_time = datetime(
        year=int(config["term_start_time"]["year"]),
        month=int(config["term_start_time"]["month"]),
        day=int(config["term_start_time"]["day"]),
        tzinfo=pytz.timezone('Asia/Shanghai')
    )

    events = []

    for course in courses_info:
        week_nums = []
        week_segs = course['weeks'].split(',')
        for seg in week_segs:
            delimiter = [int(i) for i in seg.split('-')]
            start = delimiter[0]
            end = delimiter[1] if len(delimiter) == 2 else start
            for i in range(start, end + 1):
                week_nums.append(i)
        day = chinese_to_numbers[course['time'].split('[')[0]]
        seg = course['time'].split('[')[1].split('-')
        if len(seg) == 2:
            inweek_delta_start = timedelta(days=day) + coursenum_to_time[seg[0]][0]
            inweek_delta_end = timedelta(days=day) + coursenum_to_time[seg[1]][1]
            for week_num in week_nums:
                event_start_datetime = term_start_time + (week_num - 1) * timedelta(days=7) + inweek_delta_start
                event_end_datetime = term_start_time + (week_num - 1) * timedelta(days=7) + inweek_delta_end
                event = Event()
                event.add('summary', '[{}]{}'.format(course['teacher'], course['course_name']))
                event.add('location', course['location'])
                event.add('dtstart', event_start_datetime)
                event.add('dtend', event_end_datetime)
                events.append(event)

    cal = Calendar()
    cal.add('prodid', f'-//重庆大学课表//{config["user_info"]["username"]}//Powered By cqu-kb//')
    cal.add('version', '2.0')
    for event in events:
        cal.add_component(event)
    return cal
