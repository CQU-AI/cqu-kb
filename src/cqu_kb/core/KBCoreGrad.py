import re

from bs4 import BeautifulSoup as BS
from requests import Session

from cqu_kb.core.KBCore import KBCore


class KBCoreGrad(KBCore):
    def _get_payload(self):
        return {
            "userId": self.username,
            "password": self.password,
            "userType": "student",
            "imageField.x": "50",
            "imageField.y": "6",
        }

    def main(self):
        # 实例化 requests.Session 对象
        s = Session()

        # url 配置
        base_url = "http://mis.cqu.edu.cn/mis"
        login_url = base_url + "/login.jsp"
        select_course_url = base_url + "/student/plan/select_course.jsp"
        cal_base_url = base_url + "/curricula/show_stu.jsp?stuSerial="

        # 系统登录
        s.post(login_url, self._get_payload())

        # 获取 stuSerial 参数
        res = s.get(select_course_url)
        stu_serial = re.findall(r"stuSerial=(\d*)?", res.text)[0]

        # 获取课表 html
        cal_url = cal_base_url + stu_serial
        cal = s.get(cal_url)

        course_info = self.get_course_info(cal.text)
        return self.get_cal(course_info)

    def get_course_info(self, page_content):
        page_content = page_content.replace("<br/>", "[br]").replace("<br>", "[br]")

        soup = BS(page_content, features="html.parser")
        table = soup.find_all("table")[0]

        courses_info = []
        for line in table.find_all("tr")[2:]:
            for i, element in enumerate(line.find_all("td")[1:-1]):
                courses = tuple(filter(lambda x: x != "", element.text.split("[br]")))
                for j in range(len(courses) // 7):
                    courses_info.append(
                        {
                            "course_name": courses[j * 7 + 2][3:],
                            "teacher": courses[j * 7 + 5][3:],
                            "weeks": courses[j * 7 + 3][3:-1].replace(" ", ","),
                            "time": "{}[{}".format(
                                i, courses[j * 7 + 4][3:]
                            ),  # compromise with UnderGrad core
                            "location": courses[j * 7 + 6][3:],
                        }
                    )
        return courses_info
