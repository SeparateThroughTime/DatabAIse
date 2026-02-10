import re

import justpy
import json

import DatabAIse
import CssStyles


def next_page(self, msg):
    tables = DatabAIse.session_data[msg.session_id]["tables"]
    unstructured_columns = []
    columns = [[]]

    for field in DatabAIse.session_data[msg.session_id]:
        if "column" in field.name:
            unstructured_columns.append(field.value)
    print("Data fetched")

    columns_per_table = 0
    if len(unstructured_columns) > 0:
        columns_per_table = len(unstructured_columns) // len(tables)
    columns_total_counter = 0
    tables_counter = 0
    while tables_counter < len(tables):
        columns.append([])
        for columns_counter in range(columns_per_table):
            columns[tables_counter].append(unstructured_columns[columns_total_counter])
            columns_total_counter += 1
        tables_counter += 1
    print("Data structured")

    # At the end of columns is an empty list. Don't know why...
    columns.pop()
    print("Columns:")
    print(columns)
    DatabAIse.session_data[msg.session_id]["columns"] = columns

    if columns_per_table <= 0:
        print("Error?")
        return

    msg.page.redirect = "/Datenbank"


def get_page(request):
    webpage = justpy.WebPage()

    topic = DatabAIse.session_data[request.session_id]["topic"]
    tables = DatabAIse.session_data[request.session_id]["tables"]
    ai_content = "The database has the topic: '" + topic + "'. The database has the tables: "
    for table in tables:
        ai_content += "'" + table + ", "
    ai_content = ai_content[:-2]
    ai_content += (". Suggest for every table 3 attributes. "
                   "Primary keys will be incremental integer which must not any of your suggestions. "
                   "The suggested keys must not be secondary keys neither. "
                   "The output is a json with following structure: "
                   '{"table1": ["column1, column2, column3], ..., "table4": ["column1, column2, column3"]} ')

    response = DatabAIse.db_generation_prompt(ai_content)

    print(response)
    tables = json.loads(response)

    instruction_text = justpy.P(a=webpage,
                                text="Überprüfe, ob die Spalten für die Tabellen sinnvoll sind. Du kannst sie auch noch anpassen vor dem nächsten Schritt.")

    form = justpy.Form(a=webpage, classes=CssStyles.form)

    topic_input = justpy.Input(a=form, type="hidden", name="topic", value=topic)

    table_inputs = []
    table_labels = []
    column_inputs = [[]]
    table_counter = 1
    for key in tables:
        table_inputs.append(justpy.Input(a=form, type="hidden", name="table" + str(table_counter), value=key))

        table_labels.append(justpy.Label(a=form, text=key, classes=CssStyles.label))

        column_counter = 1
        column_inputs.append([])
        for column in tables[key]:
            column_inputs[table_counter - 1].append(
                justpy.Input(a=form, type="text", name="column" + str(table_counter) + str(column_counter),
                             value=column, classes=CssStyles.input))
            column_counter = column_counter + 1
        table_labels[table_counter - 1].for_component = column_inputs[table_counter - 1][0]
        table_counter = table_counter + 1

    submit_button = justpy.Input(value="Senden", type="submit", a=form, classes=CssStyles.button)
    form.on("submit", next_page)

    return webpage
