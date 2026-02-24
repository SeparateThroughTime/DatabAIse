from nicegui import ui, app
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

    ui.restructured_text("Überprüfe, ob du folgende Tabellen für die Datenbank nutzen möchtest. "
                         "Du kannst sie vor dem nächsten Schritt noch abändern.").classes(CssStyles.text)

    table_inputs = []
    ui.label("Tabelle 1:").classes(CssStyles.label)
    table_inputs.append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    ui.label("Tabelle 2:").classes(CssStyles.label)
    table_inputs.append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    ui.label("Tabelle 3:").classes(CssStyles.label)
    table_inputs.append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))
    ui.label("Tabelle 4:").classes(CssStyles.label)
    table_inputs.append(ui.input(value="Warte auf KI-Antwort").classes(CssStyles.input))

    button = ui.button("Warte auf KI-Antwort").classes(CssStyles.button)

    ui.timer(0.1, lambda: start_prompt(topic, table_inputs, button), once=True)


async def start_prompt(topic, table_inputs, button):
    response = await DatabAIse.db_create_tables_agent(topic)

    print(response)
    tables = json.loads(response)
    i = 0
    for key in tables:
        table_inputs[i].value = tables[key]
        i = i + 1

    button.on("click", lambda: next_page(table_inputs))
    button.text = "Senden"