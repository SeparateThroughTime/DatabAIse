"""Module for Page where user can choose a topic."""
from typing import override

from nicegui import ui, app, events
from nicegui.elements.input import Input

import gui_styles
import pages


class ChooseTopicPage(pages.Page):

    _topic_input: Input

    def __init__(self, control_group: bool):
        super().__init__(control_group)


    @override
    def get_page(self) -> None:
        """Function to build the page"""

        with ui.card().style(gui_styles.maincard_style):
            with ui.column():
                ui.markdown("Thema der Datenbank")
                ui.label("Gib zuerst das Thema der Datenbank an.")

                with ui.row():
                    ui.label("Thema:")
                    self._topic_input = ui.input(placeholder="Thema der Datenbank")

                ui.button("Senden", on_click=lambda: self._next_page())


        ui.keyboard(on_key=self._handle_key, ignore=[])


    def _next_page(self) -> None:
        """Saves topic that user chose and redirects to :class:`db_generation.gen_02_choose_tables_page`"""

        topic = str(self._topic_input.value or "")
        app.storage.user["database_build"] = topic
        ui.navigate.to(pages.get_page_link("choose_tables", self._control_group))


    def _handle_key(self, e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            self._next_page()