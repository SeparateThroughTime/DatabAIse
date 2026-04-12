from nicegui import ui, app

import CssStyles
import DatabAIse


def on_course_x(course_template_string, course_name, course_db):
    app.storage.user["course_template_string"] = course_template_string
    app.storage.user["course_name"] = course_name
    app.storage.user["sql_string"] = course_db
    app.storage.user["db_json"] = DatabAIse.sql_to_json(app.storage.user["sql_string"])
    ui.navigate.to("/b/Kurs")


def get_page():

    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.markdown("Kurswahl")
            ui.restructured_text("Du kannst jetzt einen Kurs auswählen. Die KI wird dann Aufgaben passend zu deiner Datenbank erstellen.\n"
                                 "Falls du noch nie mit Datenbanken gearbeitet hast, solltest du die Kurse der Reihe nach bearbeiten. "
                                 "Falls du bereits Erfahrungen hast, mache da weiter, wo du gerade stehst oder über die Themen, mit denen du noch "
                                 "die größten Schwierigkeiten hast.")
            with ui.row():
                ui.button("Kurs 1: Projektion", on_click=lambda: on_course_x(DatabAIse.course_template_1, "Kurs 1: Projektion", DatabAIse.course_1_db))
                ui.button("Kurs 2: Selektion", on_click=lambda: on_course_x(DatabAIse.course_template_2, "Kurs 2: Selektion", DatabAIse.course_2_db))
                ui.button("Kurs 3: Sortierung", on_click=lambda: on_course_x(DatabAIse.course_template_3, "Kurs 3: Sortierung", DatabAIse.course_3_db))
                ui.button("Kurs 4: Aggregatsfunktionen", on_click=lambda: on_course_x(DatabAIse.course_template_4, "Kurs 4: Aggregatsfunktionen", DatabAIse.course_4_db))
                ui.button("Kurs 5: Join", on_click=lambda: on_course_x(DatabAIse.course_template_5, "Kurs 5: Join", DatabAIse.course_5_db))
                ui.button("Kurs 6: Unterabfragen", on_click=lambda: on_course_x(DatabAIse.course_template_6, "Kurs 6: Unterabfragen", DatabAIse.course_6_db))