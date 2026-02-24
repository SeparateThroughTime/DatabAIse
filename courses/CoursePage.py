from nicegui import ui, app
import sqlite3

import CssStyles
import DatabAIse


def get_page(request):
    sql_string = app.storage.user["sql_string"]
    course_template_string = app.storage.user["course_template_string"]
    ui.timer(0.1, lambda: start_prompt(sql_string, course_template_string), once=True)


async def start_prompt(sql_string, course_template_string):
    sql_statements = await DatabAIse.course_create_sql_statements(sql_string, course_template_string)
    exercise_string = await DatabAIse.course_create_exercise(sql_statements)
    ui.restructured_text(exercise_string).classes(CssStyles.text)
