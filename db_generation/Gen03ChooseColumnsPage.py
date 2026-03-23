from nicegui import ui, app, events
import json

import CssStyles
import DatabAIse


def next_page(column_inputs):
    tables = app.storage.user["tables"]
    columns = []

    for i in range(len(column_inputs)):
        columns.append([])
        for j in range(len(column_inputs[i])):
            columns[i].append(column_inputs[i][j].value)

    app.storage.user["columns"] = columns

    ui.navigate.to("/Datenbank")


def get_page():
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
    ui.timer(0.1, lambda: start_prompt(topic, tables, column_inputs, button), once=True)

    def handle_key(e: events.KeyEventArguments):
        if e.action.keydown and e.key.enter:
            next_page(column_inputs)
    ui.keyboard(on_key=handle_key)


async def start_prompt(topic, tables, column_inputs, button):
    response = await DatabAIse.db_create_columns_agent(topic, tables)
    tables = json.loads(response)

    table_counter = 0
    for key in tables:
        column_counter = 0
        for column in tables[key]:
            column_inputs[table_counter][column_counter].value = column
            column_counter = column_counter + 1
        table_counter = table_counter + 1

    button.on("click", lambda: next_page(column_inputs))
    button.text = "Senden"