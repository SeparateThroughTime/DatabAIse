import justpy
import sqlite3
import DatabAIse


def get_page(request):
    webpage = justpy.WebPage()

    # sql_string = DatabAIse.session_data[request.session_id]["sql_string"]
    sql_string = DatabAIse.test_sql
    course_template_string = DatabAIse.course_template_1
    exercise_string = DatabAIse.course_generation_prompt(sql_string, course_template_string)
    print(exercise_string)

    return webpage