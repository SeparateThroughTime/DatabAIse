from courses import ChooseCoursePage, Course1Page
from db_generation import ChooseTopicPage, ChooseTablesPage, ChooseColumnsPage, CreateDatabasePage, DownloadPage, UploadPage
import InstructionsPage

from justpy import justpy
from justpy import SetRoute


def build():
    justpy()


@SetRoute("/")
def instructions(request):
    return InstructionsPage.get_page(request)


@SetRoute("/Themenwahl")
def choose_topic(request):
    return ChooseTopicPage.get_page(request)


@SetRoute("/Tabellenwahl")
def choose_table(request):
    return ChooseTablesPage.get_page(request)


@SetRoute("/Spaltenwahl")
def choose_columns(request):
    return ChooseColumnsPage.get_page(request)

@SetRoute("/Datenbank")
def create_database(request):
    return CreateDatabasePage.get_page(request)


@SetRoute("/Download")
def download(request):
    return DownloadPage.get_page(request)


@SetRoute("/Upload")
def upload(request):
    return UploadPage.get_page(request)


@SetRoute("/Kurswahl")
def upload(request):
    return ChooseCoursePage.get_page(request)


@SetRoute("/Kurs")
def course_1(request):
    return Course1Page.get_page(request)