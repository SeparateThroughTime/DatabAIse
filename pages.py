"""Module for structure and style of the pages.

This module defines the hierarchy of alle pages. Each function with
:code:`@ui.page("path")` builds a page for the specific path.
"""
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import logger_module
from collections.abc import Awaitable

from nicegui import ui, Client, app
from nicegui.elements.card import Card
from nicegui.elements.label import Label
from nicegui.elements.button_group import ButtonGroup


class Page(ABC):

    NAV_LIST: list[str]

    _control_group: bool

    @abstractmethod
    def __init__(self, control_group: bool):
        self._control_group = control_group
        self.get_page()


    def get_page(self):
        pass


class ErrorLabel(Label):

    def __init__(self, text: str = ''):
        super().__init__(text)
        super().classes('text-negative text-weight-bold')



class SuccessLabel(Label):

    def __init__(self, text: str = ''):
        super().__init__(text)
        super().classes('text-positive')


class WrongLabel(Label):

    def __init__(self, text: str = ''):
        super().__init__(text)
        super().classes('text-negative')

class MainCard(Card):

    def __init__(self):
        super().__init__(align_items='center')
        super().style('margin-top: 3%; margin-left: 1%; margin-right: 1%;')
        super().classes('w-full')


class SubCard(Card):

    def __init__(self):
        super().__init__(align_items='center')
        super().classes('w-full')


class MiniCard(Card):

    def __init__(self):
        super().__init__()
        super().classes('bg-secondary')


class BreadcrumbButtonGroup(ButtonGroup):

    def __init__(self):
        super().__init__()
        super().style('background: transparent;')
        super().classes('no-shadow')

    def __exit__(self, *_):
        super().__exit__(*_)
        #number_children = len(self.default_slot.children)
        for index, child in enumerate(self.default_slot.children):
            child.style('padding: 0 24px 0 32px; height: 40px; border-radius: 0 !important;')
            if index == 0:
                child.style('padding-left: 20px; clip-path: '
                            'polygon(0% 0%, calc(100% - 15px) 0%, 100% 50%, calc(100% - 15px) 100%, 0% 100%);')
            #elif index == number_children - 1:
            #    child.style('padding-right: 20px; clip-path: '
            #                'polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%, 15px 50%);')
            else:
                child.style('clip-path: '
                            'polygon(0% 0%, calc(100% - 15px) 0%, 100% 50%, calc(100% - 15px) 100%, 0% 100%, '
                            '15px 50%);')

            if index % 2 == 0:
                child.classes('bg-primary')
            else:
                child.classes('bg-secondary')


from licenses import licenses
from courses import choose_course_page, course_page
from db_generation import gen_01_choose_topic_page, gen_02_choose_tables_page, gen_03_choose_attributes_page, gen_04_create_database_page, upload_page
import instructions_page

PRETEST_LINK: str = "https://cryptpad.fr/form/#/2/form/view/rEpyzVy1ixXJbHELucLHyHNXjWjd9ByDePDkkDOu2C0/"
POSTTEST_LINK: str = "https://cryptpad.fr/form/#/2/form/view/v1pD9HRuMrT9mytSd2yxBCkn9T6rXGQCr21Pndo-Lk8/"

logger = logger_module.create_logger("pages")

_PAGE_LINKS_EXPERIMENTAL_GROUP = {
    "home": "/a",
    "choose_course": "/a/Kurswahl",
    "course": "/a/Kurs",
    "licenses": "/a/Lizenzen",
    "choose_topic": "/a/Themenwahl",
    "choose_tables": "/a/Tabellenwahl",
    "choose_attributes": "/a/Attributswahl",
    "create_database": "/a/Datenbank",
    "upload_database": "/a/Upload"
}

_PAGE_LINKS_CONTROL_GROUP = {
    "home": "/b",
    "choose_course": "/b/Kurswahl",
    "course": "/b/Kurs",
    "licenses": "/b/Lizenzen"
}

_PAGE_TITLE = {
    "home": "Home",
    "choose_course": "Kurswahl",
    "course": "Kurs",
    "licenses": "Lizenzen",
    "choose_topic": "Themenwahl",
    "choose_tables": "Tabellenwahl",
    "choose_attributes": "Attributswahl",
    "create_database": "Finalisierung",
    "upload_database": "Upload"
}


def build() -> None:
    """Starts NiceGUI."""

    ui.run(port=8080, title="DatabAIse", language="de-DE",
           storage_secret="A>dQ@KgXnXQD0iXs", reconnect_timeout=10.0, reload=False)


def get_page_link(page_key: str, control_group: bool) -> str:
    """Function to get the link to the pages.

    :param page_key: Like *'home'* or *'choose_topic'*.
    :param control_group:
        Whether it returns the link for control group or experimental group.
    :return: Link to the page.
    """

    return _PAGE_LINKS_CONTROL_GROUP[page_key] if control_group else _PAGE_LINKS_EXPERIMENTAL_GROUP[page_key]


async def wait_for_ai_response_dialog(ai_call: Callable[[], Awaitable[Any]]) -> None:
    """Function to wrap an AI call with a dialog that is closing when the
    call is finished.

    :param ai_call: async def with no parameter for AI call.
    :return:
    """

    with ui.dialog() as dialog, ui.card(), ui.column():
        ui.markdown("Warte auf KI-Antwort...")
        ui.spinner("pie", size="xl")
    # noinspection async-call
    dialog.props("persistent")
    # noinspection async-call
    dialog.open()

    try:
        await ai_call()
    except Exception as e:
        # Ensure that dialog is closed when an error occurs
        # noinspection async-call
        dialog.close()
        raise e
    else:
        # noinspection async-call
        dialog.close()


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP["home"])
def _a_instructions(client: Client) -> None:
    _page_builder(instructions_page.InstructionPage, client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP["choose_course"])
def _a_choose_course(client: Client) -> None:
    _page_builder(choose_course_page.ChooseCoursePage, client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP["course"])
def _a_course(client: Client) -> None:
    _page_builder(course_page.CoursePage, client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP["licenses"])
def _a_licenses(client: Client) -> None:
    _page_builder(licenses.LicensesPage, client)


@ui.page(_PAGE_LINKS_CONTROL_GROUP["home"])
def _b_instructions(client: Client) -> None:
    _page_builder(instructions_page.InstructionPage, client, True)


@ui.page(_PAGE_LINKS_CONTROL_GROUP["choose_course"])
def _b_choose_course(client: Client) -> None:
    _page_builder(choose_course_page.ChooseCoursePage, client, True)


@ui.page(_PAGE_LINKS_CONTROL_GROUP["course"])
def _b_course(client: Client) -> None:
    _page_builder(course_page.CoursePage, client, True)


@ui.page(_PAGE_LINKS_CONTROL_GROUP["licenses"])
def _b_licenses(client: Client) -> None:
    _page_builder(licenses.LicensesPage, client, True)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP["choose_attributes"])
def _choose_attributes(client: Client) -> None:
    _page_builder(gen_03_choose_attributes_page.ChooseAttributesPage, client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP["choose_tables"])
def _choose_table(client: Client) -> None:
    _page_builder(gen_02_choose_tables_page.ChooseTablesPage, client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP["choose_topic"])
def _choose_topic(client: Client) -> None:
    _page_builder(gen_01_choose_topic_page.ChooseTopicPage, client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP["create_database"])
def _create_database(client: Client) -> None:
    _page_builder(gen_04_create_database_page.CreateDatabasePage, client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP["upload_database"])
def _upload(client: Client) -> None:
    _page_builder(upload_page.UploadPage, client)


def _footer(control_group:bool = False) -> None:
    """Builds the footer for every page.

    Needs to run for every page **after** the actual page.

    :param control_group:
        Whether the header is for the control or experimental group.
    """
    with ui.footer(elevated=True):
        app.add_static_file(local_file="LICENSE", url_path="/Lizenz")
        ui.link("released under the MIT-License", "/Lizenz", new_tab=True)
        ui.link("utilized software", get_page_link("licenses", control_group))
        ui.label("developed by David Seßner")


def _init_default_styles() -> None:
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
    ui.grid.default_classes('items-center w-full')
    ui.textarea.default_style('width: 90%; background-color: gainsboro')


def _header(control_group: bool = False) -> None:
    """Builds the header for every page and defines default styles.

    This needs to run for every page **before** the actual page.

    :param control_group:
        Whether the header is for the control or experimental group.
    """

    with ui.header(elevated=True):
        ui.image("images/favicon.png").classes('w-8 cursor-pointer').on("click",
                                                                        lambda: ui.navigate.to(get_page_link("home", control_group)))
        ui.label("DatabAIse").classes('text-h5')
        ui.label(" ")


def _navigation(nav_list: list[str], control_group) -> None:
    with BreadcrumbButtonGroup().classes('absolute-left'):
        for nav_key in nav_list:
            title = _PAGE_TITLE[nav_key]
            link = _PAGE_LINKS_CONTROL_GROUP[nav_key] if control_group and nav_key in _PAGE_LINKS_CONTROL_GROUP \
                else _PAGE_LINKS_EXPERIMENTAL_GROUP[nav_key]
            ui.button(title, on_click=ui.navigate.to(link))


def _page_builder(page: type[Page], client: Client, control_group: bool = False):
    client.content.classes('items-center')
    ui.on_exception(lambda e: _on_exception(e))
    _init_default_styles()
    _header(control_group)
    _navigation(page.NAV_LIST, control_group)
    page(control_group)
    _footer(control_group)


def _on_exception(e: Exception) -> None:
    """Handler for on page exceptions.

    :param e: caught exception
    :return:
    """

    with ui.dialog() as dialog, ui.card(), ui.column():
        ui.markdown("Fehler")
        ui.restructured_text("Ein unerwarteter Fehler ist aufgetreten. Falls etwas nicht funktionieren sollte, "
                             "lade die Seite neu und schaue, ob es danach funktioniert.")
        ErrorLabel("Fehlermeldung: " + str(e))
        ui.button("Ok :(", on_click=dialog.close)
    dialog.open()


#TODO: Only for development. Should be deleted before launch!
@ui.page("/")
def root_page() -> None:
    ui.navigate.to(_PAGE_LINKS_EXPERIMENTAL_GROUP["home"])


class TestPage(Page, ABC):

    def __init__(self, control_group):
        super().__init__(control_group)


    def get_page(self):
        with BreadcrumbButtonGroup():
            ui.button("Erster")


@ui.page("/test")
def _test(client: Client) -> None:
    _page_builder(TestPage, client)

