from courses import ChooseCoursePage, CoursePage
from db_generation import Gen01ChooseTopicPage, Gen02ChooseTablesPage, Gen03ChooseColumnsPage, Gen04CreateDatabasePage, UploadPage
import InstructionsPage

from nicegui import ui


def build():
    ui.run(host="127.0.0.1", port=8000, title="DatabAIse", favicon="/images/favicon.png", language="de-DE",
           storage_secret="A>dQ@KgXnXQD0iXs")


@ui.page("/")
def instructions():
    InstructionsPage.get_page()

@ui.page("/Themenwahl")
def choose_topic():
    Gen01ChooseTopicPage.get_page()

@ui.page("/Tabellenwahl")
def choose_table():
    Gen02ChooseTablesPage.get_page()

@ui.page("/Spaltenwahl")
async def choose_columns():
    Gen03ChooseColumnsPage.get_page()

@ui.page("/Datenbank")
def create_database():
    Gen04CreateDatabasePage.get_page()

@ui.page("/Upload")
def upload():
    UploadPage.get_page()

@ui.page("/Kurswahl")
def upload():
    ChooseCoursePage.get_page()

@ui.page("/Kurs")
def course():
    CoursePage.get_page()