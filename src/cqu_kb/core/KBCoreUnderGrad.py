from urllib import parse

from bs4 import BeautifulSoup as BS
from cqu_jxgl import Student

from cqu_kb.core.KBCore import KBCore


class KBCoreUnderGrad(KBCore):
    def _get_payload(self, student):
        """
        This function prepares the payload to be sent in HTTP POST method. There are three main fields in the payload. The
        only thing that should be paid attention to is "Sel_XNXQ" field, which denotes the years（学年） and terms（学期）.

        :param student: an instance of Student from cqu-jxgl
        :return: payload to be used in HTTP POST
        """
        # First Get. Won't get any information but a cookie.
        response = student.get("/znpk/Pri_StuSel.aspx")
        soup = BS(response.content, features="html.parser")
        return parse.urlencode(
            {
                "Sel_XNXQ": soup.find("option")["value"],
                "rad": "on",
                "px": "1",
            }
        )

    def main(self):
        student = Student(username=self.username, password=self.password)

        student.login()
        page_content = student.post(
            url="/znpk/Pri_StuSel_rpt.aspx",
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            data=self._get_payload(student),
        ).content
        course_info = self.get_course_info(page_content)
        return self.get_cal(course_info)

    def get_course_info(self, page_content):
        soup = BS(page_content.decode("gbk"), features="html.parser")
        tables = soup.find_all(class_="page_table")

        courses_info = []
        for i in range(len(tables) // 2):
            table = tables[i * 2 + 1]
            rows = table.find("tbody").find_all("tr")
            cols_num = len(rows[0].find_all("td"))
            for row in rows:
                course_info = {}
                cols = row.find_all("td")
                course_info.update(
                    {
                        "course_name": cols[1].text.split("]")[-1]
                        + ("" if cols_num == 13 else "（实验）")
                    }
                )
                course_info.update({"teacher": cols[-4 if cols_num == 13 else -5].text})
                course_info.update({"weeks": cols[-3].text})
                course_info.update({"time": cols[-2].text.replace("节]", "")})
                course_info.update({"location": cols[-1].text})
                courses_info.append(course_info)
        for i in range(len(courses_info)):
            if (
                courses_info[i]["course_name"] == ""
                or courses_info[i]["course_name"] == "（实验）"
            ):
                courses_info[i]["course_name"] = courses_info[i - 1]["course_name"]
        return courses_info
