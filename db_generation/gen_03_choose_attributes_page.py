"""Module for page where user can choose attributes"""
from typing import override

from nicegui.elements.input import Input
from nicegui import ui, app, events

import databaise
from base_models import DatabaseStructure0, DatabaseStructure1, _Table1
import pages


class ChooseAttributesPage(pages.Page):

    _attribute_inputs: list[list[Input]]
    _database_build: DatabaseStructure0

    def __init__(self, control_group: bool):
        super().__init__(control_group)


    @override
    def get_page(self, control_group: bool = False) -> None:
        """Function to build the page"""

        self._database_build = DatabaseStructure0.model_validate(app.storage.user["database_build"])
        topic = self._database_build.topic
        tables = self._database_build.tables

        with pages.MainCard():
            with ui.column():
                ui.markdown("Attribute der Tabellen")
                ui.restructured_text("Überprüfe, ob die Attribute für die Tabellen sinnvoll sind. "
                                      "Du kannst sie auch noch anpassen vor dem nächsten Schritt.")
                self._attribute_inputs = []
                with ui.card():
                    ui.label(tables[0])
                    with ui.row():
                        self._attribute_inputs.append([])
                        self._attribute_inputs[0].append(ui.input())
                        self._attribute_inputs[0].append(ui.input())
                        self._attribute_inputs[0].append(ui.input())
                with ui.card():
                    ui.label(tables[1])
                    with ui.row():
                        self._attribute_inputs.append([])
                        self._attribute_inputs[1].append(ui.input())
                        self._attribute_inputs[1].append(ui.input())
                        self._attribute_inputs[1].append(ui.input())
                with ui.card():
                    ui.label(tables[2])
                    with ui.row():
                        self._attribute_inputs.append([])
                        self._attribute_inputs[2].append(ui.input())
                        self._attribute_inputs[2].append(ui.input())
                        self._attribute_inputs[2].append(ui.input())
                with ui.card():
                    ui.label(tables[3])
                    with ui.row():
                        self._attribute_inputs.append([])
                        self._attribute_inputs[3].append(ui.input())
                        self._attribute_inputs[3].append(ui.input())
                        self._attribute_inputs[3].append(ui.input())

                ui.button("Senden", on_click=lambda: self._next_page())
                ui.keyboard(on_key=self._handle_key, ignore=[])
                ui.timer(0.1, lambda: pages.wait_for_ai_response_dialog(self._start_prompt), once=True)


    async def _start_prompt(self) -> None:
        response = await databaise.db_create_attributes(self._database_build)
        tables_with_attributes = response.tables

        table_counter = 0
        for table in tables_with_attributes:
            attribute_counter = 0
            for attribute in table.attributes:
                self._attribute_inputs[table_counter][attribute_counter].value = attribute
                attribute_counter = attribute_counter + 1
            table_counter = table_counter + 1


    def _handle_key(self, e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            self._next_page()


    def _next_page(self) -> None:
        """Saves attributes and redirects to :class:`db_generation.gen_04_create_database_page`"""

        database_build : DatabaseStructure0 = DatabaseStructure0.model_validate(app.storage.user["database_build"])
        topic = database_build.topic
        table_names = database_build.tables

        tables : list[_Table1] = []
        for i in range(len(self._attribute_inputs)):
            attributes : list[str] = []
            for j in range(len(self._attribute_inputs[i])):
                attribute_name = str(self._attribute_inputs[i][j].value or "")
                attributes.append(attribute_name)
            table = _Table1(name=table_names[i], attributes=attributes)
            tables.append(table)

        new_database_build = DatabaseStructure1(topic=topic, tables=tables)
        app.storage.user["database_build"] = new_database_build.model_dump()

        ui.navigate.to(pages.get_page_link("create_database", self._control_group))
