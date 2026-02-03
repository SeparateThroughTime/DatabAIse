import justpy

import CssStyles
import DatabAIse
from DatabAIse import session_data


def on_course_1(self, msg):
    msg.page.redirect = "/Projektion"


def on_course_2(self, msg):
    msg.page.redirect = "/Selektion"


def get_page(request):
    webpage = justpy.WebPage()

    course_1_button = justpy.Input(value="Kurs 1: Projektion", a=webpage, classes=CssStyles.button, type="submit", name="course_1", click=on_course_1)
    course_2_button = justpy.Input(value="Kurs 2: Selektion", a=webpage, classes=CssStyles.button, type="submit", name="course_2", click=on_course_2)
    return webpage

def create_prompt(database, course_template):
    prompt = "{" + database + "}{" + course_template + "}"