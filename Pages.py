from courses import ChooseCoursePage, Course1Page
from db_generation import Gen01ChooseTopicPage, Gen02ChooseTablesPage, Gen03ChooseColumnsPage, Gen04CreateDatabasePage, Gen05DownloadPage, UploadPage
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
    return Gen01ChooseTopicPage.get_page(request)


@SetRoute("/Tabellenwahl")
def choose_table(request):
    return Gen02ChooseTablesPage.get_page(request)


@SetRoute("/Spaltenwahl")
def choose_columns(request):
    return Gen03ChooseColumnsPage.get_page(request)

@SetRoute("/Datenbank")
def create_database(request):
    return Gen04CreateDatabasePage.get_page(request)


@SetRoute("/Download")
def download(request):
    return Gen05DownloadPage.get_page(request)


@SetRoute("/Upload")
def upload(request):
    return UploadPage.get_page(request)


@SetRoute("/Kurswahl")
def upload(request):
    return ChooseCoursePage.get_page(request)


@SetRoute("/Kurs")
def course_1(request):
    return Course1Page.get_page(request)