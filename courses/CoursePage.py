import json
import sqlite3

import pandas

from nicegui import ui, app

import CssStyles
import DatabAIse


def get_page():
    sql_string = app.storage.user["sql_string"]
    db_json = DatabAIse.sql_to_json(sql_string)
    course_name = app.storage.user["course_name"]
    topic = db_json["database"]["topic"]
    print(sql_string)
    sql_list = sql_string.splitlines()[2:]
    course_template_string = app.storage.user["course_template_string"]

    database = sqlite3.connect(":memory:")
    for query in sql_list:
        try:
            database.execute(query)
        except Exception as e:
            raise Exception("SQL Error for '" + query + "':", e)
    database.commit()

    with ui.card().classes(CssStyles.card):
        with ui.column().classes(CssStyles.column):
            topic_markdown = ui.markdown(course_name).classes(CssStyles.markdown)
            story_textfield = ui.restructured_text("Warte auf KI-Antwort").classes(CssStyles.text)
            database_tables = []

            with ui.row().classes(CssStyles.row):
                for table in db_json["database"]["tables"]:
                    database_tables.append(ui.table(columns=[{'name': "name", 'label': "Spalte", 'field': "name"},
                                                            {'name': "type", 'label': "Typ", 'field': "type"},
                                                            {'name': "primary", 'label': "Primärschlüssel", 'field': "primary"}],
                                                    rows=table["columns"]).classes(CssStyles.table))

            exercise_textfield = ui.restructured_text("Warte auf KI-Antwort").classes(CssStyles.exercise)
            sql_input = ui.textarea().classes(CssStyles.input)
            run_button = ui.button("Warte auf KI-Antwort").classes(CssStyles.button)
            result_table = ui.table(rows=[{}], columns=[{}]).classes(CssStyles.table)
            result_table.visible = False
            result_feedback_label = ui.label().classes(CssStyles.label)
            next_button = ui.button("Warte auf KI-Antwort").classes(CssStyles.button)

    ui.timer(0.1, lambda: start_prompt(db_json, course_template_string, story_textfield, exercise_textfield, sql_input, run_button, next_button, result_table, database, result_feedback_label, database_tables), once=True)


async def start_prompt(db_json, course_template_string, story_textfield, exercise_textfield, sql_input, run_button, next_button, result_table, database, result_feedback_label, database_tables):
    sql_statements = await DatabAIse.course_create_sql_statements(db_json, course_template_string)
    sql_statements_json = json.loads(sql_statements)
    exercise_string = await DatabAIse.course_create_exercise(sql_statements)
    exercise_json = json.loads(exercise_string)
    print("exercise json:", exercise_json)

    story_textfield.content = "Hintergrundgeschichte\n" + exercise_json["0"]

    # this is a list so it is mutable, so next_exercise can alter the value. Ugly but works
    exercise_counter = [0]
    next_exercise(exercise_json, exercise_textfield, exercise_counter, next_button, result_table, sql_input)

    run_button.text = "Antwort überprüfen"
    run_button.on("click", lambda: run_sql(sql_statements_json, exercise_counter, sql_input, result_table, database, result_feedback_label))

    next_button.text = "Nächste Aufgabe"
    next_button.on("click", lambda: next_exercise(exercise_json, exercise_textfield, exercise_counter, next_button, result_table, sql_input))


def next_exercise(exercise_json, exercise_textfield, exercise_counter, next_button, result_table, sql_input):
    exercise_counter[0] = exercise_counter[0] + 1
    if str(exercise_counter[0] + 1) not in exercise_json:
        next_button.on("click", finished_exercise)
        next_button.text = "Kurs abschließen"

    if str(exercise_counter[0]) not in exercise_json:
        raise Exception("Exercise " + exercise_counter[0] + " does not exist in:\n" + str(exercise_json))

    result_table.visible = False
    exercise_textfield.content = exercise_json[str(exercise_counter[0])]
    sql_input.value = ""




def finished_exercise():
    print("TODO")


def run_sql(correct_queries_json, exercise_counter, sql_input, result_table, database, result_feedback_label):
    correct_query = correct_queries_json[str(exercise_counter[0])]["statement"]
    print("Correct Query:\n", correct_query)
    # correct_result = database.execute(correct_query)
    correct_result = pandas.read_sql_query(correct_query, database)
    # correct_dataframe = pandas.DataFrame(correct_result)
    print("Correct Result:\n", correct_result.to_string)

    try:
        # user_result = database.execute(sql_input.value)
        user_result = pandas.read_sql_query(sql_input.value, database)
    except pandas.errors.DatabaseError as e:
        result_feedback_label.text = str(e)
        result_feedback_label.classes(CssStyles.err_msg)
    else:
        # user_dataframe = pandas.DataFrame(user_result)
        print("User Result:\n", user_result.to_string())
        result_table.columns = [{'name': col, 'label': col, 'field': col} for col in user_result]
        result_table.rows = user_result.to_dict('records')
        if correct_result.equals(user_result):
            result_feedback_label.text = "Deine Antwort ist richtig!"
            result_feedback_label.classes(CssStyles.success_msg)
        else:
            result_feedback_label.text = ("Dein Ergebnis stimmt noch nicht mit den Lösungen überein.\n"
                                          "Überprüfe, ob du einen Fehler gemacht hast. Falls du trotzdem glaubst, "
                                          "dass deine Eingabe korrekt ist, frage bei deiner Lehrkraft nach. Da "
                                          "die Aufgaben KI-generiert sind, könnte auch die Lösung falsch sein.")
            result_feedback_label.classes(CssStyles.wrong_msg)

    result_table.visible = True