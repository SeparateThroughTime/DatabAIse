from licenses import Licenses
from courses import ChooseCoursePage, CoursePage
from b import BChooseCoursePage, BInstructionsPage, BCoursePage
from db_generation import Gen01ChooseTopicPage, Gen02ChooseTablesPage, Gen03ChooseColumnsPage, Gen04CreateDatabasePage, UploadPage
import InstructionsPage
from nicegui import ui, Client, app


def build():
    ui.run(port=8080, title="DatabAIse", language="de-DE",
           storage_secret="A>dQ@KgXnXQD0iXs", reconnect_timeout=10.0, reload=False)


def header(root):
    ui.colors(primary="#8fb6ff", secondary="#e3b36f", accent="#80acff", dark="#1d1d1d", dark_page="#0d347a")

    ui.button.default_classes('text-center bg-primary q-pa-sm shadow-1')
    ui.input.default_classes('')
    ui.label.default_classes('text-left')
    ui.restructured_text.default_classes('text-center')
    ui.restructured_text.default_style('')
    ui.upload.default_classes('text-center shadow-1')
    ui.table.default_classes('text-left shadow-1')
    ui.markdown.default_classes('text-h3')
    ui.card.default_classes('items-center col-9')
    ui.image.default_classes('')
    ui.header.default_classes('bg-primary fixed-top justify-between')
    ui.footer.default_classes('bg-secondary fixed-bottom justify-between')
    ui.column.default_classes('items-center w-full')
    ui.row.default_classes('items-center justify-center')
    ui.textarea.default_style('width: 90%; background-color: gainsboro')

    with ui.header(elevated=True):
        ui.image("images/favicon.png").classes('w-8 cursor-pointer').on("click", lambda: ui.navigate.to(root))
        ui.label("DatabAIse").classes('text-h5')
        ui.label(" ")


def footer(root):
    with ui.footer(elevated=True):
        app.add_static_file(local_file="LICENSE", url_path="/Lizenz")
        ui.link("released under the MIT-License", "/Lizenz", new_tab=True)
        ui.link("utilized software", root + "/Lizenzen")
        ui.label("published by David Seßner")


@ui.page("/a")
def a_instructions(client: Client):
    client.content.classes('items-center')
    header("/a")
    InstructionsPage.get_page()
    footer("/a")


@ui.page("/a/Themenwahl")
def choose_topic(client: Client):
    client.content.classes('items-center')
    header("/a")
    Gen01ChooseTopicPage.get_page()
    footer("/a")


@ui.page("/a/Tabellenwahl")
def choose_table(client: Client):
    client.content.classes('items-center')
    header("/a")
    Gen02ChooseTablesPage.get_page()
    footer("/a")


@ui.page("/a/Spaltenwahl")
async def choose_columns(client: Client):
    client.content.classes('items-center')
    header("/a")
    Gen03ChooseColumnsPage.get_page()
    footer("/a")


@ui.page("/a/Datenbank")
def create_database(client: Client):
    client.content.classes('items-center')
    header("/a")
    Gen04CreateDatabasePage.get_page()
    footer("/a")


@ui.page("/a/Upload")
def upload(client: Client):
    client.content.classes('items-center')
    header("/a")
    UploadPage.get_page()
    footer("/a")


@ui.page("/a/Kurswahl")
def a_choose_course(client: Client):
    client.content.classes('items-center')
    header("/a")
    ChooseCoursePage.get_page()
    footer("/a")


@ui.page("/a/Kurs")
def a_course(client: Client):
    client.content.classes('items-center')
    header("/a")
    CoursePage.get_page()
    footer("/a")


@ui.page("/a/Lizenzen")
def a_licenses(client: Client):
    client.content.classes("items-center")
    header("/a")
    Licenses.get_page()
    footer("/a")


@ui.page("/b")
def b_instructions(client: Client):
    client.content.classes('items-center')
    header("/b")
    BInstructionsPage.get_page()
    footer("/b")


@ui.page("/b/Kurswahl")
def control_choose_course(client: Client):
    client.content.classes("items-center")
    header("/b")
    BChooseCoursePage.get_page()
    footer("/b")


@ui.page("/b/Kurs")
def a_course(client: Client):
    client.content.classes('items-center')
    header("/b")
    BCoursePage.get_page()
    footer("/b")


@ui.page("/b/Lizenzen")
def a_licenses(client: Client):
    client.content.classes("items-center")
    header("/b")
    Licenses.get_page()
    footer("/b")
