"""Module for the front page."""

from nicegui import ui
import CssStyles


def get_page() -> None:
    """Function to build the page"""

    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.image("images/logo.png").props("width=60%")
            ui.restructured_text("""Dieses Tool ist zur Nutzung in einer Studie entwickelt.
                                    Ihr werdet von eurer Lehrkraft in Gruppe A und Gruppe B eingeteilt.
                                    Hier bist du richtig, wenn du in **Gruppe A** eingeteilt wurdest.
                                    
                                    *Zwischen den Schritten kann es zu Wartezeiten kommen, da die Antwort der KI Zeit benötigt.
                                    Bitte gedulde dich und lade nicht die Seite neu. Das führt nur zu neuen Anfragen an die KI und verlängert deine Wartezeit.*
                                    
                                    Bevor du anfängst, fülle bitte die Vorumfrage aus, insofern du an der Studie teilnimmst.
                                    """).style('margin-left: 10%; margin-right: 10%')

            ui.button("Teilnahme an der Vorumfrage", on_click=lambda: ui.navigate.to("https://cryptpad.fr/form/#/2/form/view/rEpyzVy1ixXJbHELucLHyHNXjWjd9ByDePDkkDOu2C0/", new_tab=True))

            with ui.card().classes("col-6", remove="col-9"):
                ui.restructured_text("""Mit dem Tool wirst du Datenbanken zu Themen deiner Wahl mithilfe von KI erstellen.
                                Zu der Datenbank werden dir entsprechende Aufgaben gestellt.
                                
                                Falls du bereits eine Datenbank erstellt hast, die du wiederverwenden möchtest, klicke auf **Lade Datenbank hoch**.
                                Falls du noch keine Datenbank erstellt hast, oder eine neue erstellen möchtest, klicke auf **Erstelle Datenbank**.""")
                ui.button("Erstelle Datenbank", on_click=lambda: ui.navigate.to("/a/Themenwahl"))
                ui.button("Lade Datenbank hoch", on_click=lambda: ui.navigate.to("/a/Upload"))


            ui.button("Teilnahme an der Nachumfrage", on_click=lambda: ui.navigate.to("https://cryptpad.fr/form/#/2/form/view/v1pD9HRuMrT9mytSd2yxBCkn9T6rXGQCr21Pndo-Lk8/", new_tab=True))