"""Module for page where user can choose tables."""
import logging
from typing import override

from nicegui import ui, app, events

import databaise
import logger_module
from base_models import DatabaseStructure0
import pages
import re

logger: logging.Logger = logger_module.create_logger(__name__)

class ChooseTablesPage(pages.Page):

    _database: DatabaseStructure0

    def _nav_list_setter(self, val):
        self._nav_list = pages.generate_dynamic_db_generation_nav_list(pages.Pages.CHOOSE_TABLES)


    @override
    def save_progress(self):
        if not self._database.tables:
            return
        app.storage.user["database_build"][pages.Pages.CHOOSE_TABLES] = self._database.model_dump()


    @override
    def get_page(self) -> None:
        """Function to build the page"""

        self._database = DatabaseStructure0(topic=app.storage.user["database_build"][pages.Pages.CHOOSE_TOPIC], tables=[])

        if pages.Pages.CHOOSE_TABLES in app.storage.user["database_build"] and not self.prompt:
            self._database: DatabaseStructure0 = DatabaseStructure0.model_validate(
                app.storage.user["database_build"][pages.Pages.CHOOSE_TABLES])

        with pages.MainCard(), ui.column():
            ui.markdown("Tabellen der Datenbank")
            ui.restructured_text("Überprüfe, ob du folgende Tabellen für die Datenbank nutzen möchtest. "
                                 "Du kannst sie vor dem nächsten Schritt noch abändern.")

            with pages.SubCard():
                with ui.grid(columns=4):
                    self._tables_ui()

            ui.button("Senden", on_click=lambda: self._next_page())

        if self.prompt:
            ui.timer(0.1, lambda: pages.wait_for_ai_response_dialog(self._start_prompt), once=True)
        ui.keyboard(on_key=self._handle_key, ignore=[])


    async def _start_prompt(self) -> None:
        self._database = await databaise.db_create_tables(self._database.topic)
        await self._tables_ui.refresh()


    @ui.refreshable
    def _tables_ui(self) -> None:
        for i in range(len(self._database.tables)):
            with pages.MiniCard(), ui.row():
                table_input = ui.input(f"Tabelle {i + 1}")
                table_input.value = self._database.tables[i]
                table_input.on("change", lambda e, index=i: self._on_table_input_change(index, e.args))
                remove_button = ui.button(icon="delete").props("color=negative")
                remove_button.on("click", lambda index=i: self._on_remove_button_click(index))

        with pages.MiniCard():
            self._add_button = ui.button(icon="add").props("color=positive").classes("w-full")
            self._add_button.on("click", self._on_add_button_click)


    def _handle_key(self, e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            self._next_page()


    def _next_page(self) -> None:
        """Saves tables and redirects to :class:`db_generation.gen_03_choose_attributes_page`"""

        if len(self._database.tables) < 1:
            with ui.dialog() as dialog, ui.card(), ui.column():
                ui.label("Es sind keine Tabellen vorhanden. Bitte füge Tabellen hinzu und versuche es erneut. "
                         "Alternativ kannst du auch diese Seite neu laden, damit erneut Tabellennamen generiert werden.")
                ui.button("Ok", on_click=dialog.close)
            dialog.open()
            return

        if any([re.sub("[_]", "", databaise.namingConventions(table)) == "" for table in self._database.tables]):
            with ui.dialog() as dialog, ui.card(), ui.column():
                ui.label("Eine oder mehrere Tabellen haben keinen gültigen Namen. Bitte überprüfe die Tabellennamen "
                         "und versuche es erneut.")
                ui.button("Ok", on_click=dialog.close)
            dialog.open()
            return

        self.navigate_to(pages.Pages.CHOOSE_ATTRIBUTES, prompt=True)


    async def _on_remove_button_click(self, index: int) -> None:
        self._database.tables.pop(index)
        await self._tables_ui.refresh()


    async def _on_add_button_click(self):
        self._database.tables.append("")
        await self._tables_ui.refresh()


    def _on_table_input_change(self, index: int, value: str):
        self._database.tables[index] = value
