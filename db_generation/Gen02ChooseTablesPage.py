from nicegui import ui, app, events
import json

import CssStyles
import DatabAIse


def next_page(table_inputs):
    tables = []
    for table_input in table_inputs:
        tables.append(table_input.value)
    app.storage.user["tables"] = tables

    ui.navigate.to("/Spaltenwahl")


def get_page():
    topic = app.storage.user["topic"]

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

    ui.timer(0.1, lambda: start_prompt(topic, table_inputs, button), once=True)

    def handle_key(e: events.KeyEventArguments):
        if e.action.keydown and e.key.enter:
            next_page(table_inputs)
    ui.keyboard(on_key=handle_key)


async def start_prompt(topic, table_inputs, button):
    response = await DatabAIse.db_create_tables_agent(topic)

    tables = json.loads(response)
    i = 0
    for key in tables:
        table_inputs[i].value = tables[key]
        i = i + 1

    button.on("click", lambda: next_page(table_inputs))
    button.text = "Senden"