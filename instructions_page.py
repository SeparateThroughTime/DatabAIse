"""Module for the front page."""
from typing import override

from nicegui import ui, app

import pages

class InstructionPage(pages.Page):

    def _nav_list_setter(self, val):
        self._nav_list = [pages.Pages.HOME]


    @override
    def save_progress(self):
        pass


    @override
    def get_page(self):
        """Function to build the page"""

        with pages.MainCard():
            with ui.column():
                ui.image("images/logo.png").props("width=60%")
                group_designation = "B" if self._control_group else "A"
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
                          on_click=lambda: self.navigate_to(pages.PRETEST_LINK, new_tab=True))

                with pages.SubCard():
                    if self._control_group:
                        self._get_control_group_page()
                    else:
                        self._get_experimental_group_page()

                ui.button("Teilnahme an der Nachumfrage",
                          on_click=lambda: self.navigate_to(pages.POSTTEST_LINK, new_tab=True))


    def _get_control_group_page(self) -> None:
        ui.restructured_text("""Du kannst direkt mit der Aufgabenbearbeitung loslegen.
                                    Klicke auf **Zur Kurswahl** um zu beginnen.""")
        ui.button("Zur Kurswahl",
                  on_click=lambda: self.navigate_to(pages.Pages.CHOOSE_COURSE))


    def _get_experimental_group_page(self) -> None:
        ui.restructured_text("""Mit dem Tool wirst du Datenbanken zu Themen deiner Wahl mithilfe von KI erstellen.
                                    Zu der Datenbank werden dir entsprechende Aufgaben gestellt.
                                    
                                    Falls du bereits eine Datenbank erstellt hast, die du wiederverwenden möchtest,
                                    klicke auf **Lade Datenbank hoch**.
                                    Falls du noch keine Datenbank erstellt hast, oder eine neue erstellen möchtest,
                                    klicke auf **Erstelle Datenbank**.""")
        if "database_build" in app.storage.user:
            if "final" in app.storage.user["database_build"]:
                ui.button("Zur Kurswahl", on_click=lambda: self.navigate_to(pages.Pages.CHOOSE_COURSE))
        ui.button("Erstelle Datenbank", on_click=lambda: self.navigate_to(pages.Pages.CHOOSE_TOPIC, prompt=True))
        ui.button("Lade Datenbank hoch", on_click=lambda: self.navigate_to(pages.Pages.UPLOAD_DATABASE))
