"""Module for page where user can choose columns"""

from nicegui.elements.input import Input
from nicegui import ui, app, events
import json
from typing import List

import CssStyles
import DatabAIse


def get_page() -> None:
    """Function to build the page"""

    topic = app.storage.user["topic"]
    tables = app.storage.user["tables"]

    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.markdown("Attribute der Tabellen")
            ui.restructured_text("Überprüfe, ob die Attribute für die Tabellen sinnvoll sind. "
                                  "Du kannst sie auch noch anpassen vor dem nächsten Schritt.")
            column_inputs = []
            with ui.card():
                ui.label(tables[0])
                with ui.row():
                    column_inputs.append([])
                    column_inputs[0].append(ui.input(value="Warte auf KI-Antwort"))
                    column_inputs[0].append(ui.input(value="Warte auf KI-Antwort"))
                    column_inputs[0].append(ui.input(value="Warte auf KI-Antwort"))
            with ui.card():
                ui.label(tables[1])
                with ui.row():
                    column_inputs.append([])
                    column_inputs[1].append(ui.input(value="Warte auf KI-Antwort"))
                    column_inputs[1].append(ui.input(value="Warte auf KI-Antwort"))
                    column_inputs[1].append(ui.input(value="Warte auf KI-Antwort"))
            with ui.card():
                ui.label(tables[2])
                with ui.row():
                    column_inputs.append([])
                    column_inputs[2].append(ui.input(value="Warte auf KI-Antwort"))
                    column_inputs[2].append(ui.input(value="Warte auf KI-Antwort"))
                    column_inputs[2].append(ui.input(value="Warte auf KI-Antwort"))
            with ui.card():
                ui.label(tables[3])
                with ui.row():
                    column_inputs.append([])
                    column_inputs[3].append(ui.input(value="Warte auf KI-Antwort"))
                    column_inputs[3].append(ui.input(value="Warte auf KI-Antwort"))
                    column_inputs[3].append(ui.input(value="Warte auf KI-Antwort"))

            button = ui.button("Warte auf KI-Antwort")

    async def start_prompt() -> None:
        response = await DatabAIse.db_create_columns_agent(topic, tables)
        tables_with_columns = json.loads(response)

        table_counter = 0
        for key in tables_with_columns:
            column_counter = 0
            for column in tables_with_columns[key]:
                column_inputs[table_counter][column_counter].value = column
                column_counter = column_counter + 1
            table_counter = table_counter + 1

        button.on("click", lambda: _next_page(column_inputs))
        button.text = "Senden"
    ui.timer(0.1, start_prompt, once=True)

    def handle_key(e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            _next_page(column_inputs)
    ui.keyboard(on_key=handle_key, ignore=[])


def _next_page(column_inputs: List[List[Input]]) -> None:
    """Saves columns and redirects to CreateDatabasePage"""

    tables = app.storage.user["tables"]
    columns = []

    for i in range(len(column_inputs)):
        columns.append([])
        for j in range(len(column_inputs[i])):
            columns[i].append(column_inputs[i][j].value)

    app.storage.user["columns"] = columns

    ui.navigate.to("/a/Datenbank")
