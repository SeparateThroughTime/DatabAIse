"""Module for Page where user can choose a topic."""
from typing import override, Optional

from nicegui import ui, app, events
from nicegui.elements.input import Input

import pages


class ChooseTopicPage(pages.Page):

    _topic_input: Input

    def _nav_list_setter(self, val):
        self._nav_list = pages.generate_dynamic_db_generation_nav_list(pages.Pages.CHOOSE_TOPIC)


    @override
    def save_progress(self):
        if not self._topic_input.value:
            return
        topic = str(self._topic_input.value or "")
        app.storage.user["database_build"][pages.Pages.CHOOSE_TOPIC] = topic


    @override
    def get_page(self) -> None:
        """Function to build the page"""

        if not "database_build" in app.storage.user or self.prompt:
            app.storage.user["database_build"] = {}

        topic: Optional[str] = None
        if pages.Pages.CHOOSE_TOPIC in app.storage.user["database_build"]:
            topic = app.storage.user["database_build"][pages.Pages.CHOOSE_TOPIC]

        with pages.MainCard():
            with ui.column():
                ui.markdown("Thema der Datenbank")
                ui.label("Gib zuerst das Thema der Datenbank an.")

                with ui.row():
                    ui.label("Thema:")
                    self._topic_input = ui.input(value=topic, placeholder="Thema der Datenbank")

                ui.button("Senden", on_click=lambda: self._next_page())


        ui.keyboard(on_key=self._handle_key, ignore=[])


    def _next_page(self) -> None:
        """Saves topic that user chose and redirects to :class:`db_generation.gen_02_choose_tables_page`"""

        self.navigate_to(pages.Pages.CHOOSE_TABLES, prompt=True)


    def _handle_key(self, e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            self._next_page()