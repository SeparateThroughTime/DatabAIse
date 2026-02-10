import justpy
import json
import CssStyles
import DatabAIse


def next_page(self, msg):
    msg.page.redirect = "/Spaltenwahl"
    DatabAIse.session_data[msg.session_id] = msg.form_data

def get_test_page(request):
    webpage = justpy.WebPage()

    instruction_text = justpy.P(a=webpage, text="Überprüfe, ob du folgende Themen für die Datenbank nutzen möchtest. "
                                                "Du kannst sie vor dem nächsten Schritt noch abändern.")

    form = justpy.Form(a=webpage, classes=CssStyles.form)

    topic_input = justpy.Input(a=form, type="hidden", name="topic", value="Metal-Bands")

    table_labels = []
    table_inputs = []

    table_labels.append(justpy.Label(a=form, text="Tabelle 1:", classes=CssStyles.label))
    table_inputs.append(justpy.Input(a=form, type="text", name="table1", value="Bands", classes=CssStyles.input))
    table_labels[0].for_component = table_inputs[0]

    table_labels.append(justpy.Label(a=form, text="Tabelle 2:", classes=CssStyles.label))
    table_inputs.append(justpy.Input(a=form, type="text", name="table2", value="Alben", classes=CssStyles.input))
    table_labels[1].for_component = table_inputs[1]

    table_labels.append(justpy.Label(a=form, text="Tabelle 3:", classes=CssStyles.label))
    table_inputs.append(justpy.Input(a=form, type="text", name="table3", value="Titel", classes=CssStyles.input))
    table_labels[2].for_component = table_inputs[2]

    table_labels.append(justpy.Label(a=form, text="Tabelle 4:", classes=CssStyles.label))
    table_inputs.append(justpy.Input(a=form, type="text", name="table4", value="Konzerte", classes=CssStyles.input))
    table_labels[3].for_component = table_inputs[3]

    submit_button = justpy.Input(value="Senden", type="submit", a=form, classes=CssStyles.button)
    form.on("submit", next_page)

    return webpage


def get_page(request):
    webpage = justpy.WebPage()

    topic = -1
    for field in DatabAIse.session_data[request.session_id]:
        if field.name == "topic":
            topic = field.value

    response = DatabAIse.db_generation_prompt("Suggest 4 table names for a database with the topic '" + topic +
                                "'. It must be reasonable to have at least two 1-to-many relations and one"
                                " many-to-many relation between the tables."
                                " The suggested tables must not be relational tables."
                                " The output only contains the table names only, as: "
                                '{"A": "table1", "B": "table2", "C": "table3", "D": "table4"}')

    instruction_text = justpy.P(a=webpage, text="Überprüfe, ob du folgende Themen für die Datenbank nutzen möchtest. "
                                                "Du kannst sie vor dem nächsten Schritt noch abändern.")

    form = justpy.Form(a=webpage, classes=CssStyles.form)

    topic_input = justpy.Input(a=form, type="hidden", name="topic", value=topic)

    print(response)
    tables = json.loads(response)
    table_labels = []
    table_inputs = []
    i = 1
    for key in tables:
        table_labels.append(justpy.Label(a=form, text="Tabelle " + str(i) + ":", classes=CssStyles.label))
        table_inputs.append(justpy.Input(a=form, type="text", name="table" + str(i), value=tables[key], classes=CssStyles.
                                         input))
        table_labels[i-1].for_component = table_inputs[i-1]
        i = i + 1

    submit_button = justpy.Input(value="Senden", type="submit", a=form, classes=CssStyles.button)
    form.on("submit", next_page)

    return webpage
