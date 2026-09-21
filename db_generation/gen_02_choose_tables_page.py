"""Module for page where user can choose tables."""
from typing import override

from nicegui.elements.grid import Grid
from nicegui.elements.input import Input
from nicegui import ui, app, events, elements
from nicegui.elements.row import Row

import databaise
from base_models import DatabaseStructure0
import pages


class ChooseTablesPage(pages.Page):

    _table_inputs: list[Input]
    _topic: str
    _tables_grid: Grid

    def __init__(self, control_group: bool):
        super().__init__(control_group)


    @override
    def get_page(self) -> None:
        """Function to build the page"""

        self._topic = app.storage.user["database_build"]
        self._table_inputs = []

        with pages.MainCard():
            with ui.column():
                ui.markdown("Tabellen der Datenbank")
                ui.restructured_text("Überprüfe, ob du folgende Tabellen für die Datenbank nutzen möchtest. "
                                     "Du kannst sie vor dem nächsten Schritt noch abändern.")

                with pages.SubCard():
                    self._tables_grid = ui.grid(columns=4)

                ui.button("Senden", on_click=lambda: self._next_page())
                ui.timer(0.1, lambda: pages.wait_for_ai_response_dialog(self._start_prompt), once=True)
                ui.keyboard(on_key=self._handle_key, ignore=[])


    async def _start_prompt(self) -> None:
        result = await databaise.db_create_tables(self._topic)
        tables = result.tables

        for i in range(len(tables)):
            table_input = ui.input(f"Tabelle {i + 1}")
            table_input.value = tables[i]
            table_input.move(self._tables_grid)
            self._table_inputs.append(table_input)


    def _handle_key(self, e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            self._next_page()


    def _next_page(self) -> None:
        """Saves tables and redirects to :class:`db_generation.gen_03_choose_attributes_page`"""

        topic = app.storage.user["database_build"]
        table_strings = []
        for table_input in self._table_inputs:
            table_strings.append(table_input.value)
        tables = DatabaseStructure0(topic=topic, tables=table_strings)
        app.storage.user["database_build"] = tables.model_dump()

        ui.navigate.to(pages.get_page_link("choose_attributes", self._control_group))
