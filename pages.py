"""Module for structure and style of the pages.

This module defines the hierarchy of alle pages. Each function with
:code:`@ui.page("path")` builds a page for the specific path.
"""

import logger_module
from licenses import licenses
from courses import choose_course_page, course_page
from db_generation import gen_01_choose_topic_page, gen_02_choose_tables_page, gen_03_choose_attributes_page, gen_04_create_database_page, upload_page
import instructions_page
from nicegui import ui, Client, app

PRETEST_LINK: str = "https://cryptpad.fr/form/#/2/form/view/rEpyzVy1ixXJbHELucLHyHNXjWjd9ByDePDkkDOu2C0/"
POSTTEST_LINK: str = "https://cryptpad.fr/form/#/2/form/view/v1pD9HRuMrT9mytSd2yxBCkn9T6rXGQCr21Pndo-Lk8/"

logger = logger_module.create_logger("pages")

_page_links_experimental_group = {
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

_page_links_control_group = {
    "home": "/b",
    "choose_course": "/b/Kurswahl",
    "course": "/b/Kurs",
    "licenses": "/b/Lizenzen"
}

def build() -> None:
    """Starts NiceGUI."""

    ui.run(port=8080, title="DatabAIse", language="de-DE",
           storage_secret="A>dQ@KgXnXQD0iXs", reconnect_timeout=10.0, reload=False)


def footer(control_group:bool = False) -> None:
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


def header(control_group: bool = False) -> None:
    """Builds the header for every page and defines default styles.

    This needs to run for every page **before** the actual page.

    :param control_group:
        Whether the header is for the control or experimental group.
    """
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
        ui.image("images/favicon.png").classes('w-8 cursor-pointer').on("click",
                                                lambda: ui.navigate.to(get_page_link("home", control_group)))
        ui.label("DatabAIse").classes('text-h5')
        ui.label(" ")


@ui.page(_page_links_experimental_group["home"])
def a_instructions(client: Client) -> None:
    client.content.classes('items-center')
    header()
    instructions_page.get_page()
    footer()


@ui.page(_page_links_experimental_group["choose_course"])
def a_choose_course(client: Client) -> None:
    client.content.classes('items-center')
    header()
    choose_course_page.get_page()
    footer()


@ui.page(_page_links_experimental_group["course"])
def a_course(client: Client) -> None:
    client.content.classes('items-center')
    header()
    course_page.get_page()
    footer()


@ui.page(_page_links_experimental_group["licenses"])
def a_licenses(client: Client) -> None:
    client.content.classes("items-center")
    header()
    licenses.get_page()
    footer()


@ui.page(_page_links_control_group["home"])
def b_instructions(client: Client) -> None:
    client.content.classes('items-center')
    header(True)
    instructions_page.get_page(True)
    footer(True)


@ui.page(_page_links_control_group["choose_course"])
def b_choose_course(client: Client) -> None:
    client.content.classes("items-center")
    header(True)
    choose_course_page.get_page(True)
    footer(True)


@ui.page(_page_links_control_group["course"])
def b_course(client: Client) -> None:
    client.content.classes('items-center')
    header(True)
    course_page.get_page(True)
    footer(True)


@ui.page(_page_links_control_group["licenses"])
def b_licenses(client: Client) -> None:
    client.content.classes("items-center")
    header(True)
    licenses.get_page(True)
    footer(True)


@ui.page(_page_links_experimental_group["choose_attributes"])
def choose_attributes(client: Client) -> None:
    client.content.classes('items-center')
    header()
    gen_03_choose_attributes_page.get_page()
    footer()


@ui.page(_page_links_experimental_group["choose_tables"])
def choose_table(client: Client) -> None:
    client.content.classes('items-center')
    header()
    gen_02_choose_tables_page.get_page()
    footer()


@ui.page(_page_links_experimental_group["choose_topic"])
def choose_topic(client: Client) -> None:
    client.content.classes('items-center')
    header()
    gen_01_choose_topic_page.get_page()
    footer()


@ui.page(_page_links_experimental_group["create_database"])
def create_database(client: Client) -> None:
    client.content.classes('items-center')
    header()
    gen_04_create_database_page.get_page()
    footer()


@ui.page(_page_links_experimental_group["upload_database"])
def upload(client: Client) -> None:
    client.content.classes('items-center')
    header()
    upload_page.get_page()
    footer()


def get_page_link(page_key: str, control_group: bool) -> str:
    """Function to get the link to the pages.

    :param page_key: Like *'home'* or *'choose_topic'*.
    :param control_group:
        Whether it returns the link for control group or experimental group.
    :return: Link to the page.
    """

    return _page_links_control_group[page_key] if control_group else _page_links_experimental_group[page_key]


#TODO: Only for development. Should be deleted before launch!
@ui.page("/")
def root_page() -> None:
    ui.navigate.to(_page_links_experimental_group["home"])
