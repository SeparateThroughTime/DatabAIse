"""Module for displaying and managing the courses

.. attention::

    Occasionally the Page gets in an endless reload loop. The cause could be a reload on connection loss
    when the AI takes too long. Further investigation necessary.
"""
import logging
import sqlite3
from enum import Enum
from typing import override

import pandas
from nicegui import ui, app, events

from sqlite3 import Connection
from nicegui.elements.button import Button
from nicegui.elements.input import Input
from nicegui.elements.label import Label
from nicegui.elements.markdown import Markdown
from nicegui.elements.pagination import Pagination
from nicegui.elements.restructured_text import ReStructuredText
from nicegui.elements.table import Table

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


class CoursePage(pages.Page):
    """Class to build the page"""

    _database_instance: Connection

    _sql_string: str
    _database_structure: DatabaseStructure3
    _course: Course
    _sample_solutions: CourseTemplate
    _course_name: str
    _user_answers: list[tuple[str, Proofreading] | None]
    _exercise_pointer: int
    _course_template: CourseTemplate

    _choose_course_button: Button
    _regenerate_button: Button
    _topic_markdown: Markdown
    _story_textfield: ReStructuredText
    _exercise_textfield: ReStructuredText
    _sql_input: Input
    _run_button: Button
    _result_table: Table
    _error_feedback_label: Label
    _success_feedback_label: Label
    _wrong_feedback_label: Label
    _pagination: Pagination
    _previous_button: Button
    _next_button: Button
    _database_tables: list[Table]


    def __init__(self, control_group: bool = False):
        super().__init__(control_group)


    @override
    def get_page(self):
        logger.info("Start loading page.")
        self._course_name = app.storage.user["course_name"]
        self._sql_string = app.storage.user["sql_string"]
        self._database_structure = DatabaseStructure3.model_validate_json(app.storage.user["database_build"])
        self._course_template \
            = CourseTemplate.model_validate_json(app.storage.user["course_template"])

        logger.debug(f"Creating virtual database with SQL file:\n{self._sql_string}")
        self._database_instance = sqlite3.connect(":memory:")
        for query in self._sql_string.splitlines()[2:]:
            try:
                self._database_instance.execute(query)
            except Exception as e:
                raise Exception("SQL Error for '" + query + "':", e)
        self._database_instance.commit()
        logger.info("Virtual database connected.")

        ui.keyboard(on_key=self._handle_key)
        with pages.MainCard():
            with ui.column().classes("items-start", remove="items-center"):
                with ui.row().classes("justify-between"):
                    self._choose_course_button = ui.button("Zurück zu Kurswahl",
                                                           on_click=lambda: ui.navigate.to(pages.get_page_link(
                                                               "choose_course", self._control_group)))
                    self._regenerate_button = ui.button("Kurs neu generieren", on_click=self._regenerate_course)

            with ui.column():
                self._topic_markdown = ui.markdown(self._course_name)
                with pages.SubCard():
                    with ui.column():
                        ui.markdown("Hintergrundgeschichte").classes("text-h5")
                        self._story_textfield = ui.restructured_text("")


                with pages.SubCard():
                    with ui.column():
                        ui.markdown("Aufgabe").classes("text-h5")
                        with ui.row():
                            self._previous_button = ui.button("Vorherige Aufgabe",
                                                    on_click=lambda: self._load_exercise(self._exercise_pointer - 1))
                            self._next_button = ui.button("Nächste Aufgabe",
                                                    on_click=lambda: self._load_exercise(self._exercise_pointer + 1))
                        self._pagination = ui.pagination(1, len(self._course_template.exercise_solutions),
                                                         direction_links=False)
                        self._pagination.on("click", self._on_pagination_change)
                        self._exercise_textfield = ui.restructured_text("")
                        self._sql_input = ui.textarea(on_change=self._on_sql_input_change)
                        self._run_button = ui.button("Antwort überprüfen", on_click=self._run_sql)
                        self._success_feedback_label = pages.SuccessLabel("").set_visibility(False)
                        self._error_feedback_label = pages.ErrorLabel("").set_visibility(False)
                        self._wrong_feedback_label = pages.WrongLabel("").set_visibility(False)
                        self._result_table = ui.table(rows=[{}], columns=[{}])
                        self._result_table.set_visibility(False)

                with ui.card():
                    with ui.column():
                        ui.markdown("Tabellen der Datenbank").classes("text-h5")
                        with ui.row():
                            self._database_tables = []
                            self._database_structure \
                                = DatabaseStructure3.model_validate_json(app.storage.user["database_build"])
                            for table in self._database_structure.tables:
                                with ui.expansion(table.name):
                                    self._database_tables.append(ui.table(
                                        columns=[{'name': "name", 'label': "Spalte", 'field': "name"},
                                                {'name': "type", 'label': "Typ", 'field': "type"}],
                                        rows=[{"name": attribute.name, "type": attribute.type}
                                                for attribute in table.attributes]))

        if self._course_name in app.storage.user["courses"]:
            self._load_course_safe()
        else:
            ui.timer(0.1, lambda: pages.wait_for_ai_response_dialog(self._generate_course), once=True)
        logger.info("Page built finished.")


    def _finished_course(self) -> None:
        """Triggered from the next_button after the last exercise to return to ChooseCoursePage."""

        ui.navigate.to(pages.get_page_link("choose_course", self._control_group))


    def _run_sql(self) -> None:
        """Triggered from the run_button to run sql query.

        User query is executed on database. If it runs an error the error will
        be shown to the user. If the execution succeeds, the result will be
        compared to the result of the sample solution and the user gets a
        feedback whether there answer is correct.
        """

        correct_query = self._sample_solutions.exercise_solutions[self._exercise_pointer].sql_query
        correct_result = pandas.read_sql_query(correct_query, self._database_instance)
        user_input = str(self._sql_input.value or "")

        self._error_feedback_label.text = ""
        self._error_feedback_label.set_visibility(False)
        self._success_feedback_label.text = ""
        self._success_feedback_label.set_visibility(False)
        self._wrong_feedback_label.text = ""
        self._wrong_feedback_label.set_visibility(False)

        try:
            user_result = pandas.read_sql_query(user_input, self._database_instance)
        except pandas.errors.DatabaseError as e:
            self._error_feedback_label.text = str(e)
            self._error_feedback_label.set_visibility(True)
            self._result_table.set_visibility(False)
            self._user_answers[self._exercise_pointer] = (user_input, Proofreading.SYNTAX)
        else:
            self._result_table.columns = [{'name': col, 'label': col, 'field': col} for col in user_result]
            self._result_table.rows = user_result.to_dict('records')
            if correct_result.equals(user_result):
                self._success_feedback_label.text = "Deine Antwort ist richtig!"
                self._success_feedback_label.set_visibility(True)
                self._user_answers[self._exercise_pointer] = (user_input, Proofreading.CORRECT)
            else:
                self._wrong_feedback_label.text = ("Dein Ergebnis stimmt noch nicht mit den Lösungen überein.\n"
                                            "Überprüfe, ob du einen Fehler gemacht hast. Falls du trotzdem glaubst, "
                                            "dass deine Eingabe korrekt ist, frage bei deiner Lehrkraft nach. Da "
                                            "die Aufgaben KI-generiert sind, könnte auch die Lösung falsch sein.")
                self._wrong_feedback_label.set_visibility(True)
                self._user_answers[self._exercise_pointer] = (user_input, Proofreading.WRONG)
            self._result_table.set_visibility(True)
        finally:
            app.storage.user["courses"][self._course_name]["user_answers"] = self._user_answers


    def _load_exercise(self, exercise_pointer: int) -> None:
        """Triggered from the next_button to display next exercise."""

        self._exercise_pointer = exercise_pointer
        app.storage.user["courses"][self._course_name]["exercise_pointer"] = self._exercise_pointer
        self._pagination.set_value(self._exercise_pointer)

        if self._exercise_pointer > len(self._course.exercises):
            self._finished_course()
            return

        if self._exercise_pointer + 1> len(self._course.exercises):
            self._next_button.text = "Kurs abschließen"
        else:
            self._next_button.text = "Nächste Aufgabe"

        if self._exercise_pointer <= 1:
            self._previous_button.props("disabled")
        else:
            self._previous_button.props(remove="disabled")

        if self._exercise_pointer > len(self._course.exercises):
            #raise Exception("Exercise " + str(exercise_pointer) + " does not exist in:\n" + str(app.storage.user["exercise_json"]))
            return

        self._result_table.set_visibility(False)
        self._error_feedback_label.text = ""
        self._error_feedback_label.set_visibility(False)
        self._success_feedback_label.text = ""
        self._success_feedback_label.set_visibility(False)
        self._wrong_feedback_label.text = ""
        self._wrong_feedback_label.set_visibility(False)
        self._exercise_textfield.content = self._course.exercises[self._exercise_pointer]
        self._sql_input.value = ""

        if self._user_answers[self._exercise_pointer] is not None:
            logger.info("Found user answer for exercise.")
            x: list[tuple[str, int]] = [("", 1)]
            (a, b) = x[0]
            (user_input, a) = (self._user_answers[self._exercise_pointer] or (None, None))
            self._sql_input.value = user_input
            self._run_sql()


    async def _generate_course(self) -> None:
        """Start prompt and update page afterward."""

        app.storage.user["courses"][self._course_name] = {}
        logger.info("Start AI call for sample solutions.")
        self._sample_solutions = await databaise.course_create_sample_solutions(self._database_structure, self._course_template)
        logger.info("Sample solutions generated.")
        app.storage.user["courses"][self._course_name]["sample_solutions"] = self._sample_solutions.model_dump_json()
        logger.info("Start AI call for course generation.")
        self._course = await databaise.course_create_exercise(self._sample_solutions)
        logger.info("Course generated.")
        app.storage.user["courses"][self._course_name]["course"] = self._course.model_dump_json()
        self._user_answers = [None for _ in self._course.exercises]

        self._ready(0)


    def _regenerate_course(self) -> None:
        with ui.dialog() as dialog, ui.card(), ui.column():
            ui.markdown("Kurs neu generieren?")
            ui.restructured_text("Durch das Neugenerieren des Kurses, gehen alle bisherigen Antworten verloren."
                                 " Der Kurs wird auf Basis der aktuellen Datenbank nochmals von der KI generiert.")
            with ui.row():
                ui.button("Neu generieren!",
                          on_click=lambda: (ui.timer(0.1,
                                                     lambda: pages.wait_for_ai_response_dialog(self._generate_course),
                                                     once=True), dialog.close()))
                ui.button("Abbrechen", on_click=lambda: dialog.close)
        dialog.open()


    def _load_course_safe(self) -> None:
        """Load course safe."""

        try:
            course_data = app.storage.user["courses"][self._course_name]
            self._sample_solutions = CourseTemplate.model_validate_json(course_data["sample_solutions"])
            self._course = Course.model_validate_json(course_data["course"])
            self._story_textfield.content = self._course.story
            self._user_answers = course_data["user_answers"]
            self._exercise_pointer = course_data["exercise_pointer"]
            self._exercise_pointer = ((self._exercise_pointer - 1) % len(self._course.exercises)) + 1
        except KeyError as e:
            logger.exception(f"{repr(e)}\nError on loading course. Generating new course to proceed.")
            ui.timer(0.1, self._generate_course, once=True)
        else:
            self._ready(course_data["exercise_pointer"])


    def _ready(self, exercise_pointer: int) -> None:
        """Run after all data is ready to use.

        As the AI prompts need to run in a different thread than the page
        all variables that depend on the result need to be set outside
        __init__(). So after loading the course safe **or** after the course
        generation this method should run to set those variables.
        """

        app.storage.user["courses"][self._course_name]["user_answers"] = self._user_answers
        self._story_textfield.content = self._course.story
        self._load_exercise(exercise_pointer)
        logger.info("UI updated.")


    def _handle_key(self, e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            self._run_sql()


    def _on_sql_input_change(self) -> None:
        sql_input_value = str(self._sql_input.value or "")
        app.storage.user["courses"][self._course_name]["sql_input_value"] = sql_input_value
        if self._user_answers[self._exercise_pointer] is not None:
            if self._user_answers[self._exercise_pointer][1] != Proofreading.NO_PROOFREADING:
                return
        self._user_answers[self._exercise_pointer] = (sql_input_value, Proofreading.NO_PROOFREADING)
        app.storage.user["courses"][self._course_name]["user_answers"] = self._user_answers


    def _on_pagination_change(self) -> None:
        logger.debug("Pagination click detected")
        exercise_destination = int(self._pagination.value or 0)
        self._load_exercise(exercise_destination)
