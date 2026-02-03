import justpy

from DatabAIse import session_data
from DatabAIse import test_sql
import CssStyles


def on_create_db(self, msg):
    msg.page.redirect = "/Themenwahl"


def on_upload_db(self, msg):
    msg.page.redirect = "/Upload"


def get_page(request):
    print("Start!")
    webpage = justpy.WebPage()

    if request.session_id not in session_data:
        session_data[request.session_id] = {}

    instruction_text = justpy.P(text="Instuktionen", a=webpage)

    create_db_button = justpy.Input(value="Erstelle Datenbank", a=webpage, classes=CssStyles.button, click=on_create_db)
    upload_db_button = justpy.Input(value="Lade Datenbank hoch", a=webpage, classes=CssStyles.button, click=on_upload_db)
    return webpage


def test_on_create_db(self, msg):
    msg.page.redirect = "/Datenbank"
    session_data[msg.session_id] =test_sql


def test_get_page():
    print("Start!")
    webpage = justpy.WebPage()

    instruction_text = justpy.P(text="Instuktionen", a=webpage)

    create_db_button = justpy.Input(value="Erstelle Datenbank", a=webpage, classes=CssStyles.button, click=test_on_create_db)
    upload_db_button = justpy.Input(value="Lade Datenbank hoch", a=webpage, classes=CssStyles.button, click=on_upload_db)
    return webpage

