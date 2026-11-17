"""Module for structure and style of the pages.

This module defines the hierarchy of alle pages. Each function with
:code:`@ui.page("path")` builds a page for the specific path.
"""
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import StrEnum
from typing import Any, Optional, overload

import logger_module
from collections.abc import Awaitable

from nicegui import ui, Client, app
from nicegui.elements.card import Card
from nicegui.elements.label import Label
from nicegui.elements.button_group import ButtonGroup


class Pages(StrEnum):
    HOME = "home"
    CHOOSE_COURSE = "choose_course"
    COURSE = "course"
    LICENSES = "licenses"
    CHOOSE_TOPIC = "choose_topic"
    CHOOSE_TABLES = "choose_tables"
    CHOOSE_ATTRIBUTES = "choose_attributes"
    CREATE_DATABASE = "create_database"
    UPLOAD_DATABASE = "upload_database"


class Page(ABC):

    _control_group: bool
    _nav_list: list[Pages]
    _prompt: bool

    @property
    def nav_list(self) -> list[Pages]:
        return self._nav_list


    @nav_list.setter
    def nav_list(self, val):
        self._nav_list_setter(val)


    @abstractmethod
    def _nav_list_setter(self, val):
        pass

    @property
    def prompt(self) -> bool:
        return app.storage.user["prompt"] if "prompt" in app.storage.user else False


    def __init__(self, control_group: bool = False, client: Optional[Client] = None):
        self.nav_list = None
        self._control_group = control_group

        if client:
            client.content.classes('items-center')
        ui.on_exception(lambda e: self._on_exception(e))
        self._init_default_styles()
        self._header()
        self._navigation()
        self.get_page()
        self._footer()


    @abstractmethod
    def save_progress(self):
        pass


    @overload
    def navigate_to(self, target: Pages, *, prompt: bool=False, new_tab: bool=False):
        pass

    @overload
    def navigate_to(self, target: str, *, prompt: bool=False, new_tab: bool=False):
        pass

    # noinspection default-argument
    def navigate_to(self, target, *, prompt: bool=False, new_tab: bool=False) -> None:
        if isinstance(target, Pages):
            app.storage.user["prompt"] = True if prompt else False
            target = get_page_link(target, self._control_group)
        elif isinstance(target, str):
            pass
        else:
            raise TypeError(f"Invalid target type: {type(target)}")
        self.save_progress()
        ui.navigate.to(target, new_tab=new_tab)



    @abstractmethod
    def get_page(self):
        pass


    @staticmethod
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


    @staticmethod
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


    def _header(self) -> None:
        """Builds the header for every page and defines default styles.

        This needs to run for every page **before** the actual page.

        :param control_group:
            Whether the header is for the control or experimental group.
        """

        with ui.header(elevated=True):
            ui.image("images/favicon.png").classes('w-8 cursor-pointer').on(
                "click", lambda: self.navigate_to(Pages.HOME))
            ui.label("DatabAIse").classes('text-h5')
            ui.label(" ")


    def _navigation(self) -> None:
        with BreadcrumbButtonGroup().classes('absolute-left'):
            for nav_key in self._nav_list:
                title = _PAGE_TITLE[nav_key]
                ui.button(title, on_click=lambda e=nav_key: self.navigate_to(e))


    def _footer(self) -> None:
        """Builds the footer for every page.

        Needs to run for every page **after** the actual page.

        :param control_group:
            Whether the header is for the control or experimental group.
        """
        with ui.footer(elevated=True):
            app.add_static_file(local_file="LICENSE", url_path="/Lizenz")
            ui.link("released under the MIT-License", "/Lizenz", new_tab=True)
            ui.link("utilized software", get_page_link(Pages.LICENSES, self._control_group))
            ui.label("developed by David Seßner")


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
    Pages.HOME: "/a",
    Pages.CHOOSE_COURSE: "/a/Kurswahl",
    Pages.COURSE: "/a/Kurs",
    Pages.LICENSES: "/a/Lizenzen",
    Pages.CHOOSE_TOPIC: "/a/Themenwahl",
    Pages.CHOOSE_TABLES: "/a/Tabellenwahl",
    Pages.CHOOSE_ATTRIBUTES: "/a/Attributswahl",
    Pages.CREATE_DATABASE: "/a/Datenbank",
    Pages.UPLOAD_DATABASE: "/a/Upload"
}

_PAGE_LINKS_CONTROL_GROUP = {
    Pages.HOME: "/b",
    Pages.CHOOSE_COURSE: "/b/Kurswahl",
    Pages.COURSE: "/b/Kurs",
    Pages.LICENSES: "/b/Lizenzen"
}

_PAGE_TITLE = {
    Pages.HOME: "Home",
    Pages.CHOOSE_COURSE: "Kurswahl",
    Pages.COURSE: "Kurs",
    Pages.LICENSES: "Lizenzen",
    Pages.CHOOSE_TOPIC: "Themenwahl",
    Pages.CHOOSE_TABLES: "Tabellenwahl",
    Pages.CHOOSE_ATTRIBUTES: "Attributswahl",
    Pages.CREATE_DATABASE: "Finalisierung",
    Pages.UPLOAD_DATABASE: "Upload"
}


def build() -> None:
    """Starts NiceGUI."""

    ui.run(port=8080, title="DatabAIse", language="de-DE",
           storage_secret="A>dQ@KgXnXQD0iXs", reconnect_timeout=10.0, reload=False)


def get_page_link(page_key: Pages, control_group: bool) -> str:
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


def generate_dynamic_db_generation_nav_list(current_page: Pages) -> list[Pages]:
    nav_list = [Pages.HOME]
    if not "database_build" in app.storage.user:
        nav_list.append(current_page)
        return nav_list

    prompt: bool = False
    if "prompt" in app.storage.user:
        if app.storage.user["prompt"]:
            prompt = True

    db_gen_pages: list[Pages] = \
        [Pages.CHOOSE_TOPIC, Pages.CHOOSE_TABLES, Pages.CHOOSE_ATTRIBUTES, Pages.CREATE_DATABASE]
    def add_page(page: Pages) -> bool:
        if page in app.storage.user["database_build"] or current_page == page:
            nav_list.append(page)
        return True if current_page == page and prompt else False
    for page in db_gen_pages:
        if add_page(page): break

    return nav_list


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.HOME])
def _a_instructions(client: Client) -> None:
    instructions_page.InstructionPage(client=client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.CHOOSE_COURSE])
def _a_choose_course(client: Client) -> None:
    choose_course_page.ChooseCoursePage(client=client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.COURSE])
def _a_course(client: Client) -> None:
    course_page.CoursePage(client=client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.LICENSES])
def _a_licenses(client: Client) -> None:
    licenses.LicensesPage(client=client)


@ui.page(_PAGE_LINKS_CONTROL_GROUP[Pages.HOME])
def _b_instructions(client: Client) -> None:
    instructions_page.InstructionPage(client=client, control_group=True)


@ui.page(_PAGE_LINKS_CONTROL_GROUP[Pages.CHOOSE_COURSE])
def _b_choose_course(client: Client) -> None:
    choose_course_page.ChooseCoursePage(client=client, control_group=True)


@ui.page(_PAGE_LINKS_CONTROL_GROUP[Pages.COURSE])
def _b_course(client: Client) -> None:
    course_page.CoursePage(client=client, control_group=True)


@ui.page(_PAGE_LINKS_CONTROL_GROUP[Pages.LICENSES])
def _b_licenses(client: Client) -> None:
    licenses.LicensesPage(client=client, control_group=True)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.CHOOSE_ATTRIBUTES])
def _choose_attributes(client: Client) -> None:
    gen_03_choose_attributes_page.ChooseAttributesPage(client=client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.CHOOSE_TABLES])
def _choose_table(client: Client) -> None:
    gen_02_choose_tables_page.ChooseTablesPage(client=client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.CHOOSE_TOPIC])
def _choose_topic(client: Client) -> None:
    gen_01_choose_topic_page.ChooseTopicPage(client=client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.CREATE_DATABASE])
def _create_database(client: Client) -> None:
    gen_04_create_database_page.CreateDatabasePage(client=client)


@ui.page(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.UPLOAD_DATABASE])
def _upload(client: Client) -> None:
    upload_page.UploadPage(client=client)


#TODO: Only for development. Should be deleted before launch!
@ui.page("/")
def root_page() -> None:
    ui.navigate.to(_PAGE_LINKS_EXPERIMENTAL_GROUP[Pages.HOME])


class TestPage(Page):

    def save_progress(self, **kwargs):
        pass

    def _nav_list_setter(self, val):
        pass

    def get_page(self):
        with BreadcrumbButtonGroup():
            ui.button("Erster")


@ui.page("/test")
def _test(client: Client) -> None:
    TestPage(client=client)

