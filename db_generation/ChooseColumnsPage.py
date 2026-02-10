import justpy
import json

import DatabAIse
import CssStyles


def next_page(self, msg):
    msg.page.redirect = "/Datenbank"
    DatabAIse.session_data[msg.session_id] = msg.form_data


def get_test_page(request):
    webpage = justpy.WebPage()

    topic = "Metal-Bands"

    instruction_text = justpy.P(a=webpage,
                                text="Überprüfe, ob die Spalten für die Tabellen sinnvoll sind. Du kannst sie auch noch anpassen vor dem nächsten Schritt.")

    form = justpy.Form(a=webpage, classes=CssStyles.form)

    topic_input = justpy.Input(a=form, type="hidden", name="topic", value=topic)

    table_inputs = []
    table_labels = []
    column_inputs = [[]]

    table_inputs.append(justpy.Input(a=form, type="hidden", name="table0", value="Bands"))
    table_labels.append((justpy.Label(a=form, text="Bands", classes=CssStyles.label)))
    column_inputs.append([])
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column00", value="Name", classes=CssStyles.input))
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column01", value="Gründungsjahr", classes=CssStyles.input))
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column02", value="Genre", classes=CssStyles.input))
    table_labels[0].for_component = column_inputs[-1][0]

    table_inputs.append(justpy.Input(a=form, type="hidden", name="table0", value="Alben"))
    table_labels.append((justpy.Label(a=form, text="Alben", classes=CssStyles.label)))
    column_inputs.append([])
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column10", value="Titel", classes=CssStyles.input))
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column11", value="Erscheinungsjahr", classes=CssStyles.input))
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column12", value="Dauer", classes=CssStyles.input))
    table_labels[1].for_component = column_inputs[-1][0]

    table_inputs.append(justpy.Input(a=form, type="hidden", name="table0", value="Fans"))
    table_labels.append((justpy.Label(a=form, text="Bands", classes=CssStyles.label)))
    column_inputs.append([])
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column20", value="Name", classes=CssStyles.input))
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column21", value="Alter", classes=CssStyles.input))
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column22", value="Wohnort", classes=CssStyles.input))
    table_labels[2].for_component = column_inputs[-1][0]

    table_inputs.append(justpy.Input(a=form, type="hidden", name="table0", value="Konzerte"))
    table_labels.append((justpy.Label(a=form, text="Bands", classes=CssStyles.label)))
    column_inputs.append([])
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column30", value="Ort", classes=CssStyles.input))
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column31", value="Datum", classes=CssStyles.input))
    column_inputs[-1].append(justpy.Input(a=form, type="text", name="column32", value="Ticketpreis", classes=CssStyles.input))
    table_labels[3].for_component = column_inputs[-1][0]

    submit_button = justpy.Input(value="Senden", type="submit", a=form, classes=CssStyles.button)
    form.on("submit", next_page)

    return webpage



def get_page(request):
    webpage = justpy.WebPage()

    topic = -1
    tables = []
    for field in DatabAIse.session_data[request.session_id]:
        if field.name == "topic":
            topic = field.value
        elif "table" in field.name:
            tables.append(field.value)

    ai_content = "The database has the topic: '" + topic + "'. The database has the tables: "
    for table in tables:
        ai_content += "'" + table + ", "
    ai_content = ai_content[:-2]
    ai_content += (". Suggest for every table 3 attributes. The attributes must not be primary or secondary keys."
                   "The output only contains the column names.")

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
