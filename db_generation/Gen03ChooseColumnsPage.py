from nicegui import ui, app
import json

import DatabAIse
import CssStyles


def next_page(column_inputs):
    tables = app.storage.user["tables"]
    columns = []

    for i in range(len(column_inputs)):
        columns.append([])
        for j in range(len(column_inputs[i])):
            columns[i].append(column_inputs[i][j].value)

    print("Columns:")
    print(columns)
    app.storage.user["columns"] = columns

    ui.navigate.to("/Datenbank")


def get_page():
    topic = app.storage.user["topic"]
    tables = app.storage.user["tables"]
    (ui.restructured_text("Überprüfe, ob die Spalten für die Tabellen sinnvoll sind. "
                          "Du kannst sie auch noch anpassen vor dem nächsten Schritt.").classes(CssStyles.text))

    column_inputs = []
    column_inputs.append([])
    ui.label(tables[0]).classes(CssStyles.label)
    column_inputs[0].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs[0].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs[0].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs.append([])
    ui.label(tables[1]).classes(CssStyles.label)
    column_inputs[1].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs[1].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs[1].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs.append([])
    ui.label(tables[2]).classes(CssStyles.label)
    column_inputs[2].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs[2].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs[2].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs.append([])
    ui.label(tables[3]).classes(CssStyles.label)
    column_inputs[3].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs[3].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    column_inputs[3].append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))

    button = ui.button("Warte auf KI-Antwort").classes(CssStyles.button)
    ui.timer(0.1, lambda: start_prompt(topic, tables, column_inputs, button), once=True)


async def start_prompt(topic, tables, column_inputs, button):
    response = await DatabAIse.db_create_columns_agent(topic, tables)
    print(response)
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