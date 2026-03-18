from nicegui import ui, app

import CssStyles


def next_page(topic):
    app.storage.user["topic"] = topic
    ui.navigate.to("/Tabellenwahl")


def get_page():
    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.markdown("Thema der Datenbank")
            ui.label("Gib zuerst das Thema der Datenbank an.")

            with ui.row():
                ui.label("Thema:")
                topic_input = ui.input(placeholder="Thema der Datenbank")

            ui.button("Senden", on_click=lambda: next_page(topic_input.value))