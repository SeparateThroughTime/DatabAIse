"""Module for displaying and managing the courses

.. attention::

    Occasionally the Page gets in an endless reload loop. The cause could be a reload on connection loss
    when the AI takes too long. Further investigation necessary.
"""

import json
import sqlite3
import pandas
from nicegui import ui, app, events

import CssStyles
import DatabAIse


def get_page() -> None:
    """Function to build the page"""

    database = sqlite3.connect(":memory:")
    for query in app.storage.user["sql_string"].splitlines()[2:]:
        try:
            database.execute(query)
        except Exception as e:
            raise Exception("SQL Error for '" + query + "':", e)
    database.commit()

    with ui.card().style(CssStyles.maincard_style):
        with ui.column().classes("items-start", remove="items-center"):
            choose_course_button = ui.button("Zurück zu Kurswahl", on_click=lambda: ui.navigate.to("/a/Kurswahl"))

        with ui.column():
            topic_markdown = ui.markdown(app.storage.user["course_name"])
            with ui.card().classes(CssStyles.subcard_classes):
                with ui.column():
                    ui.markdown("Hintergrundgeschichte").classes("text-h5")
                    story_textfield = ui.restructured_text("Warte auf KI-Antwort")


            with ui.card().classes(CssStyles.subcard_classes):
                with ui.column():
                    ui.markdown("Aufgabe").classes("text-h5")
                    exercise_textfield = ui.restructured_text("Warte auf KI-Antwort")

                    def on_sql_input_change() -> None:
                        app.storage.user["sql_input_value"] = sql_input.value
                    sql_input = ui.textarea(on_change=on_sql_input_change)

                    run_button = ui.button("Warte auf KI-Antwort")
                    result_table = ui.table(rows=[{}], columns=[{}])
                    result_table.visible = False
                    result_feedback_label = ui.label()
                    next_button = ui.button("Warte auf KI-Antwort")

            with ui.card():
                with ui.column():
                    ui.markdown("Tabellen der Datenbank").classes("text-h5")
                    with ui.row():
                        database_tables = []
                        for table in app.storage.user["db_json"]["database"]["tables"]:
                            with ui.expansion(table["name"]):
                                database_tables.append(ui.table(columns=[{'name': "name", 'label': "Spalte", 'field': "name"},
                                                                         {'name': "type", 'label': "Typ", 'field': "type"},
                                                                         {'name': "primary", 'label': "Primärschlüssel", 'field': "primary"}],
                                                                rows=table["columns"]))


    def finished_course() -> None:
        """Triggered from the next_button after the last exercise to return to ChooseCoursePage."""

        ui.navigate.to("/Kurswahl")


    def run_sql() -> None:
        """Triggered from the run_button to run sql query.

        User query is executed on database. If it runs an error the error will
        be shown to the user. If the execution succeeds, the result will be
        compared to the result of the sample solution and the user gets a
        feedback whether there answer is correct.
        """

        correct_query = app.storage.user["solutions_json"][str(app.storage.user["exercise_counter"])]["statement"]
        correct_result = pandas.read_sql_query(correct_query, database)

        try:
            user_result = pandas.read_sql_query(sql_input.value, database)
        except pandas.errors.DatabaseError as e:
            app.storage.user["result_feedback_label_text"] = str(e)
            app.storage.user["result_feedback_label_classes"] = CssStyles.err_msg
            app.storage.user["result_table_visible"] = False
        else:
            app.storage.user["result_table_columns"] = [{'name': col, 'label': col, 'field': col} for col in user_result]
            result_table.columns = app.storage.user["result_table_columns"]
            app.storage.user["result_table_rows"] = user_result.to_dict('records')
            result_table.rows = app.storage.user["result_table_rows"]
            if correct_result.equals(user_result):
                app.storage.user["result_feedback_label_text"] = "Deine Antwort ist richtig!"
                app.storage.user["result_feedback_label_classes"] = CssStyles.success_msg_classes
            else:
                app.storage.user["result_feedback_label_text"] = ("Dein Ergebnis stimmt noch nicht mit den Lösungen überein.\n"
                                                                  "Überprüfe, ob du einen Fehler gemacht hast. Falls du trotzdem glaubst, "
                                                                  "dass deine Eingabe korrekt ist, frage bei deiner Lehrkraft nach. Da "
                                                                  "die Aufgaben KI-generiert sind, könnte auch die Lösung falsch sein.")
                app.storage.user["result_feedback_label_classes"] = CssStyles.wrong_msg_classes
            app.storage.user["result_table_visible"] = True

        result_feedback_label.text = app.storage.user["result_feedback_label_text"]
        result_feedback_label._classes.clear()
        result_feedback_label.classes(app.storage.user["result_feedback_label_classes"])
        app.storage.user["result_feedback_visible"] = True
        result_feedback_label.visible = app.storage.user["result_feedback_visible"]
        result_table.visible = app.storage.user["result_table_visible"]


    def next_exercise() -> None:
        """Triggered from the next_button to display next exercise."""

        app.storage.user["exercise_counter"] = app.storage.user["exercise_counter"] + 1
        if str(app.storage.user["exercise_counter"] + 1) not in app.storage.user["exercise_json"]:
            next_button.on("click", finished_course)
            next_button.text = "Kurs abschließen"

        if str(app.storage.user["exercise_counter"]) not in app.storage.user["exercise_json"]:
            #raise Exception("Exercise " + str(app.storage.user["exercise_counter"]) + " does not exist in:\n" + str(app.storage.user["exercise_json"]))
            return

        result_table.visible = False
        result_feedback_label.visible = False
        exercise_textfield.content = app.storage.user["exercise_json"][str(app.storage.user["exercise_counter"])]
        sql_input.value = ""


    async def start_prompt() -> None:
        """Start prompt and update page afterward."""

        solutions_string = await DatabAIse.course_create_sql_statements(app.storage.user["db_json"], app.storage.user["course_template_string"])
        app.storage.user["solutions_json"] = json.loads(solutions_string)
        exercise_string = await DatabAIse.course_create_exercise(solutions_string)
        app.storage.user["exercise_json"] = json.loads(exercise_string)

        story_textfield.content = app.storage.user["exercise_json"]["0"]

        app.storage.user["exercise_counter"] = 0

        next_exercise()

        run_button.text = "Antwort überprüfen"


        run_button.on("click", run_sql)

        next_button.text = "Nächste Aufgabe"
        next_button.on("click", next_exercise)
    ui.timer(0.21, start_prompt, once=True)

    def handle_key(e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            run_sql()
    ui.keyboard(on_key=handle_key)