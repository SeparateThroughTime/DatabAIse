"""Module for the front page."""

from nicegui import ui

import gui_styles
import pages




def get_page(control_group: bool = False) -> None:
    """Function to build the page"""

    with ui.card().style(gui_styles.maincard_style):
        with ui.column():
            ui.image("images/logo.png").props("width=60%")
            group_designation = "B" if control_group else "A"
            ui.restructured_text(f"""Dieses Tool ist zur Nutzung in einer Studie entwickelt.
                                     Ihr werdet von eurer Lehrkraft in Gruppe A und Gruppe B eingeteilt.
                                     Hier bist du richtig, wenn du in **Gruppe {group_designation}** eingeteilt wurdest.
                                     
                                     *Zwischen den Schritten kann es zu Wartezeiten kommen, da die Antwort der KI Zeit 
                                     benötigt.
                                     Bitte gedulde dich und lade nicht die Seite neu. Das führt nur zu neuen Anfragen an
                                     die KI und verlängert deine Wartezeit.*
                                     
                                     Bevor du anfängst, fülle bitte die Vorumfrage aus, insofern du an der Studie 
                                     teilnimmst.
                                     """).style('margin-left: 10%; margin-right: 10%')

            ui.button("Teilnahme an der Vorumfrage",
                      on_click=lambda: ui.navigate.to(pages.PRETEST_LINK, new_tab=True))

            with ui.card().classes("col-6", remove="col-9"):
                if control_group:
                    _get_control_group_page()
                else:
                    _get_experimental_group_page()

            ui.button("Teilnahme an der Nachumfrage", on_click=lambda: ui.navigate.to(pages.POSTTEST_LINK, new_tab=True))


def _get_control_group_page() -> None:
    ui.restructured_text("""Du kannst direkt mit der Aufgabenbearbeitung loslegen.
                                Klicke auf **Zur Kurswahl** um zu beginnen.""")
    ui.button("Zur Kurswahl",
              on_click=lambda: ui.navigate.to(pages.get_page_link("choose_course", True)))


def _get_experimental_group_page() -> None:
    ui.restructured_text("""Mit dem Tool wirst du Datenbanken zu Themen deiner Wahl mithilfe von KI erstellen.
                                Zu der Datenbank werden dir entsprechende Aufgaben gestellt.
                                
                                Falls du bereits eine Datenbank erstellt hast, die du wiederverwenden möchtest,
                                klicke auf **Lade Datenbank hoch**.
                                Falls du noch keine Datenbank erstellt hast, oder eine neue erstellen möchtest,
                                klicke auf **Erstelle Datenbank**.""")
    ui.button("Erstelle Datenbank", on_click=lambda: ui.navigate.to(pages.get_page_link(
        "choose_topic", False)))
    ui.button("Lade Datenbank hoch", on_click=lambda: ui.navigate.to(pages.get_page_link(
        "upload_database", False)))
