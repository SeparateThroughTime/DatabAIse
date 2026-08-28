"""Module for displaying the page where the user can choose a course."""
import logging

from nicegui import ui, app

import gui_styles
import databaise
import logger_module
import pages


logger: logging.Logger = logger_module.create_logger(__name__)


def get_page(control_group: bool = False) -> None:
    """Function to build the page."""

    with ui.card().style(gui_styles.maincard_style):
        with ui.column():
            ui.markdown("Kurswahl")
            ui.restructured_text("Du kannst jetzt einen Kurs auswählen. Die KI wird dann Aufgaben passend zu deiner Datenbank erstellen.\n"
                                 "Falls du noch nie mit Datenbanken gearbeitet hast, solltest du die Kurse der Reihe nach bearbeiten. "
                                 "Falls du bereits Erfahrungen hast, mache da weiter, wo du gerade stehst oder über die Themen, mit denen du noch "
                                 "die größten Schwierigkeiten hast.")
            with ui.row():
                ui.button("Kurs 1: Projektion", on_click=lambda: _on_course_x(1,
                                                                            "Kurs 1: Projektion",
                                                                              control_group))
                ui.button("Kurs 2: Selektion", on_click=lambda: _on_course_x(2,
                                                                            "Kurs 2: Selektion",
                                                                            control_group))
                ui.button("Kurs 3: Sortierung", on_click=lambda: _on_course_x(3,
                                                                            "Kurs 3: Sortierung",
                                                                            control_group))
                ui.button("Kurs 4: Aggregatsfunktionen", on_click=lambda: _on_course_x(4,
                                                                            "Kurs 4: Aggregatsfunktionen",
                                                                            control_group))
                ui.button("Kurs 5: Join", on_click=lambda: _on_course_x(5,
                                                                            "Kurs 5: Join",
                                                                            control_group))
                ui.button("Kurs 6: Unterabfragen", on_click=lambda: _on_course_x(6,
                                                                            "Kurs 6: Unterabfragen",
                                                                            control_group))


def _on_course_x(course_number: int, course_name: str, control_group: bool) -> None:
    """Function is triggered when any course button is clicked.

    :param course_number: Number of the course.
    :param course_name:
        Name of the course for the title of the next page.
    """

    try:
        match course_number:
            case 1:
                app.storage.user["course_template"] = databaise.course_template_1.model_dump_json()
            case 2:
                app.storage.user["course_template"] = databaise.course_template_2.model_dump_json()
            case 3:
                app.storage.user["course_template"] = databaise.course_template_3.model_dump_json()
            case 4:
                app.storage.user["course_template"] = databaise.course_template_4.model_dump_json()
            case 5:
                app.storage.user["course_template"] = databaise.course_template_5.model_dump_json()
            case 6:
                app.storage.user["course_template"] = databaise.course_template_6.model_dump_json()
            case _:
                raise ValueError(f"Expected course_number between 1 and 6 but got {course_number}.")
    except ValueError as e:
        logger.exception(repr(e))
        raise

    app.storage.user["course_name"] = course_name

    if control_group:
        try:
            match course_number:
                case 1:
                    app.storage.user["sql_string"] = databaise.course_1_db
                case 2:
                    app.storage.user["sql_string"] = databaise.course_2_db
                case 3:
                    app.storage.user["sql_string"] = databaise.course_3_db
                case 4:
                    app.storage.user["sql_string"] = databaise.course_4_db
                case 5:
                    app.storage.user["sql_string"] = databaise.course_5_db
                case 6:
                    app.storage.user["sql_string"] = databaise.course_6_db
                case _:
                    raise ValueError(f"Expected course_number between 1 and 6 but got {course_number}.")
        except ValueError as e:
            logger.exception(repr(e))
            raise

    ui.navigate.to(pages.get_page_link("course", control_group))

