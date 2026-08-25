"""Module for Page where user can choose a topic."""

from nicegui import ui, app, events

import CssStyles


def get_page() -> None:
    """Function to build the page"""

    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.markdown("Thema der Datenbank")
            ui.label("Gib zuerst das Thema der Datenbank an.")

            with ui.row():
                ui.label("Thema:")
                topic_input = ui.input(placeholder="Thema der Datenbank")

            ui.button("Senden", on_click=lambda: _next_page(topic_input.value))

    def handle_key(e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            _next_page(topic_input.value)
    ui.keyboard(on_key=handle_key, ignore=[])


def _next_page(topic: str) -> None:
    """Saves topic that user chose and redirects to ChooseTablesPage"""

    app.storage.user["database_build"] = topic
    ui.navigate.to("/a/Tabellenwahl")
