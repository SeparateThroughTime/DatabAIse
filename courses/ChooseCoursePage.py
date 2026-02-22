import justpy

import CssStyles
import DatabAIse
from DatabAIse import session_data


def on_course_1(self, msg):
    print("Kurs1")
    on_course_x(msg, DatabAIse.course_template_4)


def on_course_2(self, msg):
    self.on_course_x(msg, DatabAIse.course_template_2)


def on_course_3(self, msg):
    self.on_course_x(msg, DatabAIse.course_template_3)


def on_course_4(self, msg):
    self.on_course_x(msg, DatabAIse.course_template_4)


def on_course_5(self, msg):
    on_course_x(msg, DatabAIse.course_template_5)


def on_course_x(msg, course_template_string):
    print("KursX")
    DatabAIse.session_data[msg.session_id]["course_template_string"] = course_template_string
    msg.page.redirect = "/Kurs"

def get_page(request):
    webpage = justpy.WebPage()

    course_1_button = justpy.Input(value="Kurs 1: Projektion", a=webpage, classes=CssStyles.button, type="submit", name="course_1", click=on_course_1)
    course_2_button = justpy.Input(value="Kurs 2: Selektion", a=webpage, classes=CssStyles.button, type="submit", name="course_2", click=on_course_2)
    course_3_button = justpy.Input(value="Kurs 3: Sortierung", a=webpage, classes=CssStyles.button, type="submit", name="course_3", click=on_course_3)
    course_4_button = justpy.Input(value="Kurs 4: Aggregatsfunktionen", a=webpage, classes=CssStyles.button, type="submit", name="course_4", click=on_course_4)
    course_5_button = justpy.Input(value="Kurs 5: Join", a=webpage, classes=CssStyles.button, type="submit", name="course_5", click=on_course_5)
    return webpage

def create_prompt(database, course_template):
    prompt = "{" + database + "}{" + course_template + "}"