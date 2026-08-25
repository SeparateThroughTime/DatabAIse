"""Module for page where user can choose columns"""

from nicegui.elements.input import Input
from nicegui import ui, app, events

import CssStyles
import DatabAIse
from BaseModels import DatabaseStructure0, DatabaseStructure1, _Table1


def get_page() -> None:
    """Function to build the page"""

    database_build : DatabaseStructure0 = DatabaseStructure0.model_validate(app.storage.user["database_build"])
    topic = database_build.topic
    tables = database_build.tables

    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.markdown("Attribute der Tabellen")
            ui.restructured_text("Überprüfe, ob die Attribute für die Tabellen sinnvoll sind. "
                                  "Du kannst sie auch noch anpassen vor dem nächsten Schritt.")
            attribute_inputs = []
            with ui.card():
                ui.label(tables[0])
                with ui.row():
                    attribute_inputs.append([])
                    attribute_inputs[0].append(ui.input(value="Warte auf KI-Antwort"))
                    attribute_inputs[0].append(ui.input(value="Warte auf KI-Antwort"))
                    attribute_inputs[0].append(ui.input(value="Warte auf KI-Antwort"))
            with ui.card():
                ui.label(tables[1])
                with ui.row():
                    attribute_inputs.append([])
                    attribute_inputs[1].append(ui.input(value="Warte auf KI-Antwort"))
                    attribute_inputs[1].append(ui.input(value="Warte auf KI-Antwort"))
                    attribute_inputs[1].append(ui.input(value="Warte auf KI-Antwort"))
            with ui.card():
                ui.label(tables[2])
                with ui.row():
                    attribute_inputs.append([])
                    attribute_inputs[2].append(ui.input(value="Warte auf KI-Antwort"))
                    attribute_inputs[2].append(ui.input(value="Warte auf KI-Antwort"))
                    attribute_inputs[2].append(ui.input(value="Warte auf KI-Antwort"))
            with ui.card():
                ui.label(tables[3])
                with ui.row():
                    attribute_inputs.append([])
                    attribute_inputs[3].append(ui.input(value="Warte auf KI-Antwort"))
                    attribute_inputs[3].append(ui.input(value="Warte auf KI-Antwort"))
                    attribute_inputs[3].append(ui.input(value="Warte auf KI-Antwort"))

            button = ui.button("Warte auf KI-Antwort")

    async def start_prompt() -> None:
        response = await DatabAIse.db_create_attributes(database_build)
        tables_with_attributes = response.tables

        table_counter = 0
        for table in tables_with_attributes:
            attribute_counter = 0
            for attribute in table.attributes:
                attribute_inputs[table_counter][attribute_counter].value = attribute
                attribute_counter = attribute_counter + 1
            table_counter = table_counter + 1

        button.on("click", lambda: _next_page(attribute_inputs))
        button.text = "Senden"
    ui.timer(0.1, start_prompt, once=True)

    def handle_key(e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            _next_page(attribute_inputs)
    ui.keyboard(on_key=handle_key, ignore=[])


def _next_page(column_inputs: list[list[Input]]) -> None:
    """Saves columns and redirects to CreateDatabasePage"""

    database_build : DatabaseStructure0 = DatabaseStructure0.model_validate(app.storage.user["database_build"])
    topic = database_build.topic
    table_names = database_build.tables

    tables : list[DatabaseStructure1.Table] = []
    for i in range(len(column_inputs)):
        attributes_for_table : list[str] = []
        for j in range(len(column_inputs[i])):
            attributes_for_table.append(column_inputs[i][j].value)
        table = _Table1(name=table_names[i], attributes=attributes_for_table)
        tables.append(table)

    new_database_build = DatabaseStructure1(topic=topic, tables=tables)
    app.storage.user["database_build"] = new_database_build.model_dump()

    ui.navigate.to("/a/Datenbank")
