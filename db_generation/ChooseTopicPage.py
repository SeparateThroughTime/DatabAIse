import justpy
import CssStyles
import DatabAIse

def next_page(self, msg):
    msg.page.redirect = "/Tabellenwahl"
    DatabAIse.session_data[msg.session_id] = msg.form_data

def get_page(request):
    webpage = justpy.WebPage()

    instruction_text = justpy.P(text="Gib das Thema der Datenbank an.", a=webpage)

    form = justpy.Form(a=webpage, classes=CssStyles.form)

    topic_label = justpy.Label(a=form, text="Thema:", classes=CssStyles.label)
    topic_input = justpy.Input(a=form, type="text", name="topic", placeholder="Thema der Datenbank", classes=CssStyles.input)
    topic_label.for_component = topic_input

    submit_button = justpy.Input(value="Senden", type="submit", a=form, classes=CssStyles.button)
    form.on("submit", next_page)

    return webpage
