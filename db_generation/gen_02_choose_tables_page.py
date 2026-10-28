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

    _topic: str
    _tables: list[str]

    def __init__(self, control_group: bool):
        super().__init__(control_group)


    @override
    def get_page(self) -> None:
        """Function to build the page"""

        self._topic = app.storage.user["database_build"]
        self._tables = []

        with pages.MainCard(), ui.column():
            ui.markdown("Tabellen der Datenbank")
            ui.restructured_text("Überprüfe, ob du folgende Tabellen für die Datenbank nutzen möchtest. "
                                 "Du kannst sie vor dem nächsten Schritt noch abändern.")

            with pages.SubCard():
                with ui.grid(columns=4):
                    self._tables_ui()

            ui.button("Senden", on_click=lambda: self._next_page())
            ui.timer(0.1, lambda: pages.wait_for_ai_response_dialog(self._start_prompt), once=True)
            ui.keyboard(on_key=self._handle_key, ignore=[])


    async def _start_prompt(self) -> None:
        result = await databaise.db_create_tables(self._topic)
        self._tables = result.tables
        await self._tables_ui.refresh()


    @ui.refreshable
    def _tables_ui(self) -> None:
        for i in range(len(self._tables)):
            with pages.MiniCard(), ui.row():
                table_input = ui.input(f"Tabelle {i + 1}")
                table_input.value = self._tables[i]
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

        if len(self._tables) < 1:
            with ui.dialog() as dialog, ui.card(), ui.column():
                ui.label("Es sind keine Tabellen vorhanden. Bitte füge Tabellen hinzu und versuche es erneut. "
                         "Alternativ kannst du auch diese Seite neu laden, damit erneut Tabellennamen generiert werden.")
                ui.button("Ok", on_click=dialog.close)
            dialog.open()
            return

        if any([re.sub("[_]", "", databaise.namingConventions(table)) == "" for table in self._tables]):
            with ui.dialog() as dialog, ui.card(), ui.column():
                ui.label("Eine oder mehrere Tabellen haben keinen gültigen Namen. Bitte überprüfe die Tabellennamen "
                         "und versuche es erneut.")
                ui.button("Ok", on_click=dialog.close)
            dialog.open()
            return

        topic = app.storage.user["database_build"]
        tables = DatabaseStructure0(topic=topic, tables=self._tables)
        app.storage.user["database_build"] = tables.model_dump()

        ui.navigate.to(pages.get_page_link("choose_attributes", self._control_group))


    async def _on_remove_button_click(self, index: int) -> None:
        self._tables.pop(index)
        await self._tables_ui.refresh()


    async def _on_add_button_click(self):
        self._tables.append("")
        await self._tables_ui.refresh()


    def _on_table_input_change(self, index: int, value: str):
        self._tables[index] = value
