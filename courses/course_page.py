"""Module for displaying and managing the courses

.. attention::

    Occasionally the Page gets in an endless reload loop. The cause could be a reload on connection loss
    when the AI takes too long. Further investigation necessary.
"""
import logging
import sqlite3
from enum import Enum

import pandas
from nicegui import ui, app, events

from sqlite3 import Connection
from nicegui.elements.button import Button
from nicegui.elements.input import Input
from nicegui.elements.label import Label
from nicegui.elements.markdown import Markdown
from nicegui.elements.restructured_text import ReStructuredText
from nicegui.elements.table import Table

import gui_styles
import databaise
import logger_module
from base_models import DatabaseStructure3, CourseTemplate, Course
import pages

logger: logging.Logger = logger_module.create_logger("course_page")


class Proofreading(Enum):
    NO_PROOFREADING = 0
    CORRECT = 1
    WRONG = 2
    SYNTAX = 3


class CoursePage:
    """Class to build the page"""

    database_instance: Connection

    sql_string: str
    database_structure: DatabaseStructure3
    course: Course
    sample_solutions: CourseTemplate
    control_group: bool
    course_name: str

    choose_course_button: Button
    topic_markdown: Markdown
    story_textfield: ReStructuredText
    exercise_textfield: ReStructuredText
    sql_input: Input
    run_button: Button
    result_table: Table
    result_feedback_label: Label
    next_button: Button
    database_tables: list[Table]

    user_answers: list[tuple[str, Proofreading] | None]
    exercise_pointer: int


    def __init__(self, control_group: bool = False):
        logger.info("Start loading page.")
        self.control_group = control_group
        self.course_name = app.storage.user["course_name"]
        self.sql_string = app.storage.user["sql_string"]
        self.database_structure = DatabaseStructure3.model_validate_json(app.storage.user["database_build"])
        self.course_template \
            = CourseTemplate.model_validate_json(app.storage.user["course_template"])

        logger.debug(f"Creating virtual database with SQL file:\n{self.sql_string}")
        self.database_instance = sqlite3.connect(":memory:")
        for query in self.sql_string.splitlines()[2:]:
            try:
                self.database_instance.execute(query)
            except Exception as e:
                raise Exception("SQL Error for '" + query + "':", e)
        self.database_instance.commit()
        logger.info("Virtual database connected.")

        ui.keyboard(on_key=self.handle_key)
        with (ui.card().style(gui_styles.maincard_style)):
            with ui.column().classes("items-start", remove="items-center"):
                self.choose_course_button = ui.button("Zurück zu Kurswahl",
                        on_click=lambda: ui.navigate.to(pages.get_page_link("choose_course", control_group)))

            with ui.column():
                self.topic_markdown = ui.markdown(self.course_name)
                with ui.card().classes(gui_styles.subcard_classes):
                    with ui.column():
                        ui.markdown("Hintergrundgeschichte").classes("text-h5")
                        self.story_textfield = ui.restructured_text("Warte auf KI-Antwort")


                with ui.card().classes(gui_styles.subcard_classes):
                    with ui.column():
                        ui.markdown("Aufgabe").classes("text-h5")
                        self.exercise_textfield = ui.restructured_text("Warte auf KI-Antwort")

                        self.sql_input = ui.textarea(on_change=self.on_sql_input_change)

                        self.run_button = ui.button("Warte auf KI-Antwort")
                        self.result_table = ui.table(rows=[{}], columns=[{}])
                        self.result_table.set_visibility(False)
                        self.result_feedback_label = ui.label()
                        self.result_feedback_label.set_visibility(False)
                        self.next_button = ui.button("Warte auf KI-Antwort")

                with ui.card():
                    with ui.column():
                        ui.markdown("Tabellen der Datenbank").classes("text-h5")
                        with ui.row():
                            self.database_tables = []
                            self.database_structure \
                                = DatabaseStructure3.model_validate_json(app.storage.user["database_build"])
                            for table in self.database_structure.tables:
                                with ui.expansion(table.name):
                                    self.database_tables.append(ui.table(columns=[{'name': "name", 'label': "Spalte", 'field': "name"},
                                                                             {'name': "type", 'label': "Typ", 'field': "type"}],
                                                                    rows=[{"name": attribute.name, "type": attribute.type}
                                                                          for attribute in table.attributes]))

        if self.course_name in app.storage.user["courses"]:
            self.load_course_safe()
        else:
            ui.timer(0.1, self.generate_course, once=True)
        logger.info("Page built finished.")


    def finished_course(self) -> None:
        """Triggered from the next_button after the last exercise to return to ChooseCoursePage."""

        ui.navigate.to(pages.get_page_link("choose_course", self.control_group))


    def run_sql(self) -> None:
        """Triggered from the run_button to run sql query.

        User query is executed on database. If it runs an error the error will
        be shown to the user. If the execution succeeds, the result will be
        compared to the result of the sample solution and the user gets a
        feedback whether there answer is correct.
        """

        correct_query = self.sample_solutions.exercise_solutions[self.exercise_pointer].sql_query
        correct_result = pandas.read_sql_query(correct_query, self.database_instance)
        user_input = str(self.sql_input.value or "")

        try:
            user_result = pandas.read_sql_query(user_input, self.database_instance)
        except pandas.errors.DatabaseError as e:
            self.result_feedback_label.text = str(e)
            self.result_feedback_label._classes.clear()
            self.result_feedback_label.classes(gui_styles.err_msg)
            self.result_table.set_visibility(False)
            self.user_answers[self.exercise_pointer] = (user_input, Proofreading.SYNTAX)
        else:
            self.result_table.columns = [{'name': col, 'label': col, 'field': col} for col in user_result]
            self.result_table.rows = user_result.to_dict('records')
            if correct_result.equals(user_result):
                self.result_feedback_label.text = "Deine Antwort ist richtig!"
                self.result_feedback_label._classes.clear()
                self.result_feedback_label.classes(gui_styles.success_msg_classes)
                self.user_answers[self.exercise_pointer] = (user_input, Proofreading.CORRECT)
            else:
                self.result_feedback_label.text = ("Dein Ergebnis stimmt noch nicht mit den Lösungen überein.\n"
                                            "Überprüfe, ob du einen Fehler gemacht hast. Falls du trotzdem glaubst, "
                                            "dass deine Eingabe korrekt ist, frage bei deiner Lehrkraft nach. Da "
                                            "die Aufgaben KI-generiert sind, könnte auch die Lösung falsch sein.")
                self.result_feedback_label._classes.clear()
                self.result_feedback_label.classes(gui_styles.wrong_msg_classes)
                self.user_answers[self.exercise_pointer] = (user_input, Proofreading.WRONG)
            self.result_table.set_visibility(True)
        finally:
            app.storage.user["courses"][self.course_name]["user_answers"] = self.user_answers


    def load_exercise(self, exercise_pointer: int) -> None:
        """Triggered from the next_button to display next exercise."""

        self.exercise_pointer = exercise_pointer
        app.storage.user["courses"][self.course_name]["exercise_pointer"] = self.exercise_pointer

        logger.debug(f"exercise_pointer: {exercise_pointer}")
        if self.user_answers[self.exercise_pointer] is not None:
            self.sql_input.value = self.user_answers[self.exercise_pointer][0]
            self.run_sql()

        if self.exercise_pointer + 1 > len(self.course.exercises):
            self.next_button.on("click", self.finished_course)
            self.next_button.text = "Kurs abschließen"

        if self.exercise_pointer > len(self.course.exercises):
            #raise Exception("Exercise " + str(exercise_pointer) + " does not exist in:\n" + str(app.storage.user["exercise_json"]))
            return

        self.result_table.set_visibility(False)
        self.result_feedback_label.set_visibility(False)
        self.result_feedback_label.text = None
        self.exercise_textfield.content = self.course.exercises[self.exercise_pointer]
        self.sql_input.value = ""


    async def generate_course(self) -> None:
        """Start prompt and update page afterward."""

        app.storage.user["courses"][self.course_name] = {}
        logger.info("Start AI call for sample solutions.")
        self.sample_solutions = await databaise.course_create_sample_solutions(self.database_structure, self.course_template)
        logger.info("Sample solutions generated.")
        app.storage.user["courses"][self.course_name]["sample_solutions"] = self.sample_solutions.model_dump_json()
        logger.info("Start AI call for course generation.")
        self.course = await databaise.course_create_exercise(self.sample_solutions)
        logger.info("Course generated.")
        app.storage.user["courses"][self.course_name]["course"] = self.course.model_dump_json()

        self.ready(0)


    def load_course_safe(self) -> None:
        """Load course safe."""

        try:
            course_data = app.storage.user["courses"][self.course_name]
            self.sample_solutions = CourseTemplate.model_validate_json(course_data["sample_solutions"])
            self.course = Course.model_validate_json(course_data["course"])
            self.story_textfield.content = self.course.story
            self.ready(course_data["exercise_pointer"])
        except KeyError as e:
            logger.exception(f"{repr(e)}\nError on loading course. Generating new course to proceed.")
            ui.timer(0.1, self.generate_course, once=True)


    def ready(self, exercise_pointer: int) -> None:
        """Run after all data is ready to use.

        As the AI prompts need to run in a different thread than the page
        all variables that depend on the result need to be set outside
        __init__(). So after loading the course safe **or** after the course
        generation this method should run to set those variables.
        """

        self.user_answers = [None for _ in self.course.exercises]
        app.storage.user["courses"][self.course_name]["user_answers"] = self.user_answers
        self.story_textfield.content = self.course.story
        self.load_exercise(exercise_pointer)
        self.run_button.text = "Antwort überprüfen"
        self.run_button.on("click", self.run_sql)
        self.next_button.text = "Nächste Aufgabe"
        self.next_button.on("click", lambda: self.load_exercise(self.exercise_pointer + 1))
        logger.info("UI updated.")


    def handle_key(self, e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            self.run_sql()


    def on_sql_input_change(self) -> None:
        sql_input_value = str(self.sql_input.value or "")
        app.storage.user["courses"][self.course_name]["sql_input_value"] = sql_input_value
        if self.user_answers[self.exercise_pointer] is not None:
            if self.user_answers[self.exercise_pointer][1] != Proofreading.NO_PROOFREADING:
                return
        self.user_answers[self.exercise_pointer] = (sql_input_value, Proofreading.NO_PROOFREADING)
        app.storage.user["courses"][self.course_name]["user_answers"] = self.user_answers