import os

import justpy
import base64

from aiofiles.tempfile import TemporaryFile

import DatabAIse
from DatabAIse import session_data
import CssStyles


def next_page(self, msg):
    if not os.path.isdir(f'temp/{msg.session_id}'):
        os.mkdir(f'temp/{msg.session_id}')

    sql_data = None
    for field in msg.form_data:
        if field.type == "file":
            sql_data = field.files[0].file_content

    if sql_data is None:
        err_msg = justpy.Div(text="Keine Datei ausgewählt!", classes=CssStyles.err_msg, a=msg.page)
        return

    sql_file = open(f'temp/{msg.session_id}/sql_file.sql', 'wb')
    sql_file.write(base64.b64decode(sql_data))
    sql_file.close()
    sql_string = open(f'temp/{msg.session_id}/sql_file.sql').read()
    os.remove(f'temp/{msg.session_id}/sql_file.sql')
    os.rmdir(f'temp/{msg.session_id}')
    DatabAIse.session_data[msg.session_id]["sql_string"] = sql_string
    msg.page.redirect = "/Kurswahl"


def get_page(request):
    webpage = justpy.WebPage()
    form = justpy.Form(a=webpage, classes=CssStyles.form)
    input = justpy.Input(type="file", classes=CssStyles.input, name="sql_file", a=form, multiple=False, accept=".sql")
    choose_course_button = justpy.Input(value="Zur Kurswahl", type="submit", classes=CssStyles.button, a=form)
    form.on("submit", next_page)


    return webpage