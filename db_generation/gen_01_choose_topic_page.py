"""Module for Page where user can choose a topic."""

from nicegui import ui, app, events

import gui_styles
import pages


def get_page(control_group: bool = False) -> None:
    """Function to build the page"""

    with ui.card().style(gui_styles.maincard_style):
        with ui.column():
            ui.markdown("Thema der Datenbank")
            ui.label("Gib zuerst das Thema der Datenbank an.")

            with ui.row():
                ui.label("Thema:")
                topic_input = ui.input(placeholder="Thema der Datenbank")

            ui.button("Senden", on_click=lambda: _next_page(topic_input.value, control_group))

    def handle_key(e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            _next_page(topic_input.value, control_group)
    ui.keyboard(on_key=handle_key, ignore=[])


def _next_page(topic: str, control_group: bool) -> None:
    """Saves topic that user chose and redirects to :class:`db_generation.gen_02_choose_tables_page`"""

    app.storage.user["database_build"] = topic
    ui.navigate.to(pages.get_page_link("choose_tables", control_group))
