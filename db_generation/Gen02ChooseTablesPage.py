"""Module for page where user can choose tables."""

from nicegui.elements.input import Input
from nicegui import ui, app, events, elements

import CssStyles
import DatabAIse
from BaseModels import DatabaseStructure0


def get_page() -> None:
    """Function to build the page"""

    topic = app.storage.user["database_build"]

    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.markdown("Tabellen der Datenbank")
            ui.restructured_text("Überprüfe, ob du folgende Tabellen für die Datenbank nutzen möchtest. "
                                 "Du kannst sie vor dem nächsten Schritt noch abändern.")

            table_inputs = []
            with ui.row():
                ui.label("Tabelle 1:")
                table_inputs.append(ui.input(value="Warte auf KI-Antwort"))
            with ui.row():
                ui.label("Tabelle 2:")
                table_inputs.append(ui.input(value="Warte auf KI-Antwort"))
            with ui.row():
                ui.label("Tabelle 3:")
                table_inputs.append(ui.input(value="Warte auf KI-Antwort"))
            with ui.row():
                ui.label("Tabelle 4:")
                table_inputs.append(ui.input(value="Warte auf KI-Antwort"))

            button = ui.button("Warte auf KI-Antwort")

    async def start_prompt() -> None:
        result = await DatabAIse.db_create_tables(topic)
        tables = result.tables

        for i in range(len(tables)):
            table_inputs[i].value = tables[i]

        button.on("click", lambda: _next_page(table_inputs))
        button.text = "Senden"
    ui.timer(0.1, start_prompt, once=True)

    def handle_key(e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            _next_page(topic, table_inputs)
    ui.keyboard(on_key=handle_key, ignore=[])


def _next_page(table_inputs: list[Input]) -> None:
    """Saves tables and redirects to ChooseColumnsPage"""

    topic = app.storage.user["database_build"]
    table_strings = []
    for table_input in table_inputs:
        table_strings.append(table_input.value)
    tables = DatabaseStructure0(topic=topic, tables=table_strings)
    app.storage.user["database_build"] = tables.model_dump()

    ui.navigate.to("/a/Spaltenwahl")
