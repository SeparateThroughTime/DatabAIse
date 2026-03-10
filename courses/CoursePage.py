import json
import sqlite3
import time

import pandas

from nicegui import ui, app

import CssStyles
import DatabAIse


def get_page():
    app.storage.user["db_json"] = DatabAIse.sql_to_json(app.storage.user["sql_string"])

    database = sqlite3.connect(":memory:")
    for query in app.storage.user["sql_string"].splitlines()[2:]:
        try:
            database.execute(query)
        except Exception as e:
            raise Exception("SQL Error for '" + query + "':", e)
    database.commit()

    with ui.card():
        with ui.column():
            topic_markdown = ui.markdown(app.storage.user["course_name"])
            app.storage.user["story_textfield"] = ui.restructured_text("Warte auf KI-Antwort")
            app.storage.user["database_tables"] = []

            with ui.row():
                for table in app.storage.user["db_json"]["database"]["tables"]:
                    app.storage.user["database_tables"].append(ui.table(columns=[{'name': "name", 'label': "Spalte", 'field': "name"},
                                                                                 {'name': "type", 'label': "Typ", 'field': "type"},
                                                                                 {'name': "primary", 'label': "Primärschlüssel", 'field': "primary"}],
                                                                        rows=table["columns"]))

            app.storage.user["exercise_textfield"] = ui.restructured_text("Warte auf KI-Antwort")
            app.storage.user["sql_input"] = ui.textarea(on_change=on_sql_input_change)
            app.storage.user["run_button"] = ui.button("Warte auf KI-Antwort")
            app.storage.user["result_table"] = ui.table(rows=[{}], columns=[{}])
            app.storage.user["result_table"].visible = False
            app.storage.user["result_feedback_label"] = ui.label()
            app.storage.user["next_button"] = ui.button("Warte auf KI-Antwort")

    # Occasionally the Page gets in an endless reload loop. The cause could be a reload on connection loss
    # when the AI takes too long. No replication possible...
    if "course_loaded_time" in app.storage.user:
        if time.time() - app.storage.user["course_loaded_time"] < 20:
            load_failsafe_course_data()

    ui.timer(0.2, refresh_course_loaded_time)
    ui.timer(0.21, lambda: start_prompt(database), once=True)


def load_failsafe_course_data():
    app.storage.user["story_textfield"].content = "Hintergrundgeschichte\n" + app.storage.user["exercise_json"]["0"]

    if str(app.storage.user["exercise_counter"] + 1) not in app.storage.user["exercise_json"]["0"]:
        app.storage.user["next_button"].on("click", finished_exercise)
        app.storage.user["next_button"].text = "Kurs abschließen"

    if "result_table_visible" in app.storage.user:
        app.storage.user["result_table"].visible = app.storage.user["result_table_visible"]
        if app.storage.user["result_table_visible"]:
            app.storage.user["result_feedback_label"].text = app.storage.user["result_feedback_label_text"]
            app.storage.user["result_feedback_label"]
    else:
        app.storage.user["result_table"].visible = False

    app.storage.user["exercise_textfield"].content = app.storage.user["exercise_json"][str(app.storage.user["exercise_counter"])]
    app.storage.user["sql_input"].value = app.storage.user["sql_input_value"]

    app.storage.user["run_button"].text = "Antwort überprüfen"
    app.storage.user["run_button"].on("click", run_sql)

    app.storage.user["next_button"].text = "Nächste Aufgabe"
    app.storage.user["next_button"].on("click", next_exercise)


async def start_prompt(database):
    solutions_string = await DatabAIse.course_create_sql_statements(app.storage.user["db_json"], app.storage.user["course_template_string"])
    app.storage.user["solutions_json"] = json.loads(solutions_string)
    exercise_string = await DatabAIse.course_create_exercise(solutions_string)
    app.storage.user["exercise_json"] = json.loads(exercise_string)
    print("exercise json:", app.storage.user["exercise_json"])

    app.storage.user["story_textfield"].content = "Hintergrundgeschichte\n" + app.storage.user["exercise_json"]["0"]

    app.storage.user["exercise_counter"] = 0
    next_exercise()

    app.storage.user["run_button"].text = "Antwort überprüfen"
    app.storage.user["run_button"].on("click", lambda: run_sql(database))

    app.storage.user["next_button"].text = "Nächste Aufgabe"
    app.storage.user["next_button"].on("click", next_exercise)


def next_exercise():
    app.storage.user["exercise_counter"] = app.storage.user["exercise_counter"] + 1
    if str(app.storage.user["exercise_counter"] + 1) not in app.storage.user["exercise_json"]:
        app.storage.user["next_button"].on("click", finished_exercise)
        app.storage.user["next_button"].text = "Kurs abschließen"

    if str(app.storage.user["exercise_counter"]) not in app.storage.user["exercise_json"]:
        raise Exception("Exercise " + str(app.storage.user["exercise_counter"]) + " does not exist in:\n" + str(app.storage.user["exercise_json"]))

    app.storage.user["result_table"].visible = False
    app.storage.user["exercise_textfield"].content = app.storage.user["exercise_json"][str(app.storage.user["exercise_counter"])]
    app.storage.user["sql_input"].value = ""




def finished_exercise():
    print("TODO")


def run_sql(database):
    correct_query = app.storage.user["exercise_json"][str(app.storage.user["exercise_counter[0]"])]["statement"]
    correct_result = pandas.read_sql_query(correct_query, database)

    try:
        user_result = pandas.read_sql_query(app.storage.user["sql_input"].value, database)
    except pandas.errors.DatabaseError as e:
        app.storage.user["result_feedback_label_text"] = str(e)
        app.storage.user["result_feedback_label_classes"] = CssStyles.err_msg
        app.storage.user["result_table_visible"] = False
    else:
        app.storage.user["result_table_columns"] = [{'name': col, 'label': col, 'field': col} for col in user_result]
        app.storage.user["result_table"].columns = app.storage.user["result_table_columns"]
        app.storage.user["result_table_rows"] = user_result.to_dict('records')
        app.storage.user["result_table"].rows = app.storage.user["result_table_rows"]
        if correct_result.equals(user_result):
            app.storage.user["result_feedback_label_text"] = "Deine Antwort ist richtig!"
            app.storage.user["result_feedback_label_classes"] = CssStyles.success_msg
        else:
            app.storage.user["result_feedback_label_text"] = ("Dein Ergebnis stimmt noch nicht mit den Lösungen überein.\n"
                                                              "Überprüfe, ob du einen Fehler gemacht hast. Falls du trotzdem glaubst, "
                                                              "dass deine Eingabe korrekt ist, frage bei deiner Lehrkraft nach. Da "
                                                              "die Aufgaben KI-generiert sind, könnte auch die Lösung falsch sein.")
            app.storage.user["result_feedback_label_classes"] = CssStyles.wrong_msg
        app.storage.user["result_table_visible"] = True

    app.storage.user["result_feedback_label"].text = app.storage.user["result_feedback_label_text"]
    app.storage.user["result_feedback_label"]
    app.storage.user["result_table"].visible = app.storage.user["result_table_visible"]


def refresh_course_loaded_time():
    app.storage.user["course_loaded_time"] = time.time()


def on_sql_input_change():
    app.storage.user["sql_input_value"] = app.storage.user["sql_input"].value