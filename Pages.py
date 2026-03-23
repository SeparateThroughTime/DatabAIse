from licenses import Licenses
from courses import ChooseCoursePage, CoursePage, ControlChooseCoursePage
from db_generation import Gen01ChooseTopicPage, Gen02ChooseTablesPage, Gen03ChooseColumnsPage, Gen04CreateDatabasePage, UploadPage
import InstructionsPage
from nicegui import ui, Client, app


def build():
    ui.run(port=8080, title="DatabAIse", language="de-DE",
           storage_secret="A>dQ@KgXnXQD0iXs", reconnect_timeout=10.0, reload=False)


def header():
    ui.colors(primary="#8fb6ff", secondary="#e3b36f", accent="#80acff", dark="#1d1d1d", dark_page="#0d347a")

    ui.button.default_classes('text-center bg-primary q-pa-sm shadow-1')
    ui.input.default_classes('')
    ui.label.default_classes('text-left')
    ui.restructured_text.default_classes('text-center')
    ui.restructured_text.default_style('')
    ui.upload.default_classes('text-center shadow-1')
    ui.table.default_classes('text-left shadow-1')
    ui.markdown.default_classes('text-h3')
    ui.card.default_classes('items-center')
    ui.image.default_classes('')
    ui.header.default_classes('bg-primary fixed-top justify-between')
    ui.footer.default_classes('bg-secondary fixed-bottom justify-between')
    ui.column.default_classes('items-center w-full')
    ui.row.default_classes('items-center justify-center')
    ui.textarea.default_style('width: 90%; background-color: gainsboro')

    with ui.header(elevated=True):
        ui.image("images/favicon.png").classes('w-8 cursor-pointer').on("click", lambda: ui.navigate.to("/"))
        ui.label("DatabAIse").classes('text-h5')
        ui.label(" ")



def footer():
    with ui.footer(elevated=True):
        app.add_static_file(local_file="LICENSE", url_path="/Lizenz")
        ui.link("released under the MIT-License", "/Lizenz", new_tab=True)
        ui.link("utilized software", "/Lizenzen")
        ui.label("published by David Seßner")


@ui.page("/")
def instructions(client: Client):
    client.content.classes('items-center')
    header()
    InstructionsPage.get_page()
    footer()


@ui.page("/Themenwahl")
def choose_topic(client: Client):
    client.content.classes('items-center')
    header()
    Gen01ChooseTopicPage.get_page()
    footer()


@ui.page("/Tabellenwahl")
def choose_table(client: Client):
    client.content.classes('items-center')
    header()
    Gen02ChooseTablesPage.get_page()
    footer()


@ui.page("/Spaltenwahl")
async def choose_columns(client: Client):
    client.content.classes('items-center')
    header()
    Gen03ChooseColumnsPage.get_page()
    footer()


@ui.page("/Datenbank")
def create_database(client: Client):
    client.content.classes('items-center')
    header()
    Gen04CreateDatabasePage.get_page()
    footer()


@ui.page("/Upload")
def upload(client: Client):
    client.content.classes('items-center')
    header()
    UploadPage.get_page()
    footer()


@ui.page("/Kurswahl")
def upload(client: Client):
    client.content.classes('items-center')
    header()
    ChooseCoursePage.get_page()
    footer()


@ui.page("/Kurs")
def course(client: Client):
    client.content.classes('items-center')
    header()
    CoursePage.get_page()
    footer()


@ui.page("/Lizenzen")
def licenses(client: Client):
    client.content.classes("items-center")
    header()
    Licenses.get_page()
    footer()


@ui.page("/Kurswahl2")
def control_choose_course(client: Client):
    client.content.classes("items-center")
    header()
    ControlChooseCoursePage.get_page()
    footer()
