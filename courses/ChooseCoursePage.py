from nicegui import ui, app

import CssStyles
import DatabAIse


def on_course_x(course_template_string):
    print("KursX")
    app.storage.user["course_template_string"] = course_template_string
    ui.navigate.to("/Kurs")


def get_page():
    ui.button("Kurs 1: Projektion", on_click=lambda: on_course_x(DatabAIse.course_template_1)).classes(CssStyles.button)
    ui.button("Kurs 2: Selektion", on_click=lambda: on_course_x(DatabAIse.course_template_2)).classes(CssStyles.button)
    ui.button("Kurs 3: Sortierung", on_click=lambda: on_course_x(DatabAIse.course_template_3)).classes(CssStyles.button)
    ui.button("Kurs 4: Aggregatsfunktionen", on_click=lambda: on_course_x(DatabAIse.course_template_4)).classes(CssStyles.button)
    ui.button("Kurs 5: Join", on_click=lambda: on_course_x(DatabAIse.course_template_5)).classes(CssStyles.button)