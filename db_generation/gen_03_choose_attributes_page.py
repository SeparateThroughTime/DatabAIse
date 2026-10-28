"""Module for page where user can choose attributes"""
from typing import override
import re
import numpy

from nicegui.elements.grid import Grid
from nicegui.elements.input import Input
from nicegui import ui, app, events

import databaise
from base_models import DatabaseStructure0, DatabaseStructure1, _Table1
import pages


class ChooseAttributesPage(pages.Page):

    _pre_database_build: DatabaseStructure0
    _post_database_build: DatabaseStructure1
    _table_uis: list["ChooseAttributesPage.TableUI"]

    def __init__(self, control_group: bool):
        super().__init__(control_group)


    @override
    def get_page(self, control_group: bool = False) -> None:
        """Function to build the page"""

        self._pre_database_build = DatabaseStructure0.model_validate(app.storage.user["database_build"])
        self._table_uis = []
        topic = self._pre_database_build.topic
        tables = self._pre_database_build.tables

        with pages.MainCard():
            with ui.column():
                ui.markdown(f"Attribute der Tabellen für die Datenbank {topic}")
                ui.restructured_text("Überprüfe, ob die Attribute für die Tabellen sinnvoll sind. "
                                      "Du kannst sie auch noch anpassen vor dem nächsten Schritt.")

                with ui.grid(columns=3):
                    for table, table_number in zip(tables, range(len(tables))):
                        self._table_uis.append(ChooseAttributesPage.TableUI(self, table_number, table))

                ui.button("Senden", on_click=lambda: self._next_page())
        ui.keyboard(on_key=self._handle_key, ignore=[])
        ui.timer(0.1, lambda: pages.wait_for_ai_response_dialog(self._start_prompt), once=True)


    async def _start_prompt(self) -> None:
        self._post_database_build = await databaise.db_create_attributes(self._pre_database_build)
        for table_ui, table in zip(self._table_uis, self._post_database_build.tables):
            table_ui.table_attributes = table.attributes
            table_ui.refresh()


    class TableUI:
        _choose_attribute_page: "ChooseAttributesPage"
        table_number: int
        table_name: str
        table_attributes: list[str]

        def __init__(self, choose_attribute_page: "ChooseAttributesPage", table_number: int, table_name: str) -> None:
            self._choose_attribute_page = choose_attribute_page
            self.table_number = table_number
            self.table_name = table_name
            self.table_attributes = []
            self._table_ui()


        def refresh(self) -> None:
            self._table_ui.refresh()


        @ui.refreshable
        def _table_ui(self) -> None:
            with pages.MiniCard(), ui.column():
                ui.label(self.table_name)
                attribute_counter = 0
                for attribute in self.table_attributes:
                    with ui.row():
                        attribute_input: Input = ui.input(f"Attribut {attribute_counter + 1}")
                        attribute_input.value = attribute
                        attribute_input.on("change", lambda e, i=attribute_counter:
                            self._choose_attribute_page._on_input_value_change(self.table_number, i, e.args))
                        remove_button = ui.button(icon="delete").props("color=negative")
                        remove_button.on("click", lambda i=attribute_counter:
                            self._choose_attribute_page._on_remove_button_click(self.table_number, i))
                    attribute_counter += 1
                add_button = ui.button(icon="add").props("color=positive").classes("w-full")
                add_button.on("click", lambda: self._choose_attribute_page._on_add_button_click(self.table_number))


    def _on_add_button_click(self, table_number: int) -> None:
        self._post_database_build.tables[table_number].attributes.append("")
        self._table_uis[table_number].refresh()


    def _on_remove_button_click(self, table_number: int, attribute_number: int) -> None:
        self._post_database_build.tables[table_number].attributes.pop(attribute_number)
        self._table_uis[table_number].refresh()


    def _handle_key(self, e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            self._next_page()


    def _on_input_value_change(self, table_number: int, attribute_number: int, value: str) -> None:
        self._post_database_build.tables[table_number].attributes[attribute_number] = value


    def _next_page(self) -> None:
        """Saves attributes and redirects to :class:`db_generation.gen_04_create_database_page`"""

        if any([len(table.attributes) < 1 for table in self._post_database_build.tables]):
            with ui.dialog() as dialog, ui.card(), ui.column():
                ui.label("In einer oder mehrerer Tabellen sind keine Attribute vorhanden. Bitte füge in allen Tabelle "
                         "Attribute hinzu und versuche es erneut. "
                         "Alternativ kannst du auch diese Seite neu laden, damit erneut Attributsnamen generiert werden.")
                ui.button("Ok", on_click=dialog.close)
            dialog.open()
            return

        if any([any([re.sub("[_]", "", databaise.namingConventions(attribute)) == ""
                 for attribute in table.attributes]) for table in self._post_database_build.tables]):
            with ui.dialog() as dialog, ui.card(), ui.column():
                ui.label("Ein oder mehrere Attribute haben keinen gültigen Namen. Bitte überprüfe die Attributsnamen "
                          "und versuche es erneut.")
                ui.button("Ok", on_click=dialog.close)
            dialog.open()
            return

        app.storage.user["database_build"] = self._post_database_build.model_dump()
        ui.navigate.to(pages.get_page_link("create_database", self._control_group))
