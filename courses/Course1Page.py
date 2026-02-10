import justpy
import sqlite3
import DatabAIse


def get_page(request):
    webpage = justpy.WebPage()

    sql_string = DatabAIse.session_data[request.session_id]["sql_string"]
    course_template_string = DatabAIse.session_data[request.session_id]["course_template_string"]
    exercise_string = DatabAIse.course_generation_prompt(sql_string, course_template_string)
    justpy.P(text=exercise_string, a=webpage)

    return webpage