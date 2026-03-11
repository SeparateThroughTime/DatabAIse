import DatabAIse
from courses import ChooseCoursePage, CoursePage
from db_generation import Gen01ChooseTopicPage, Gen02ChooseTablesPage, Gen03ChooseColumnsPage, Gen04CreateDatabasePage, UploadPage
import InstructionsPage

from nicegui import ui, context, Client


def build():
    ui.run(port=80, title="DatabAIse", favicon="/images/favicon.png", language="de-DE",
           storage_secret="A>dQ@KgXnXQD0iXs")
    #q_page = context.client.page_container.default_slot.children[0]
    #q_page.default_classes('items-center')


@ui.page("/")
def instructions(client: Client):
    client.content.classes('items-center')
    DatabAIse.header()
    InstructionsPage.get_page()
    DatabAIse.footer()

@ui.page("/Themenwahl")
def choose_topic(client: Client):
    client.content.classes('items-center')
    DatabAIse.header()
    Gen01ChooseTopicPage.get_page()
    DatabAIse.footer()

@ui.page("/Tabellenwahl")
def choose_table(client: Client):
    client.content.classes('items-center')
    DatabAIse.header()
    Gen02ChooseTablesPage.get_page()
    DatabAIse.footer()

@ui.page("/Spaltenwahl")
async def choose_columns(client: Client):
    client.content.classes('items-center')
    DatabAIse.header()
    Gen03ChooseColumnsPage.get_page()
    DatabAIse.footer()

@ui.page("/Datenbank")
def create_database(client: Client):
    client.content.classes('items-center')
    DatabAIse.header()
    Gen04CreateDatabasePage.get_page()
    DatabAIse.footer()

@ui.page("/Upload")
def upload(client: Client):
    client.content.classes('items-center')
    DatabAIse.header()
    UploadPage.get_page()
    DatabAIse.footer()

@ui.page("/Kurswahl")
def upload(client: Client):
    client.content.classes('items-center')
    DatabAIse.header()
    ChooseCoursePage.get_page()
    DatabAIse.footer()

@ui.page("/Kurs")
def course(client: Client):
    client.content.classes('items-center')
    DatabAIse.header()
    CoursePage.get_page()
    DatabAIse.footer()
