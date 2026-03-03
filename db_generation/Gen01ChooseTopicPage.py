import CssStyles
import DatabAIse
from nicegui import ui, app

def next_page(topic):
    app.storage.user["topic"] = topic
    ui.navigate.to("/Tabellenwahl")


def get_page():
    with ui.card().classes(CssStyles.card):
        with ui.column().classes(CssStyles.column):
            ui.markdown("Thema der Datenbank").classes(CssStyles.markdown)
            ui.label("Gib zuerst das Thema der Datenbank an.").classes(CssStyles.label)

            with ui.row().classes(CssStyles.row):
                ui.label("Thema:").classes(CssStyles.label)
                topic_input = ui.input(placeholder="Thema der Datenbank").classes(CssStyles.input)

            ui.button("Senden", on_click=lambda: next_page(topic_input.value)).classes(CssStyles.button)