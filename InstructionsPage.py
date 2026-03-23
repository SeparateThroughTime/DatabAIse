from nicegui import ui
import CssStyles


def on_create_db(self, msg):
    msg.page.redirect = "/Themenwahl"


def on_upload_db(self, msg):
    msg.page.redirect = "/Upload"


def get_page():
    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.image("images/logo.png").props("width=60%")
            ui.restructured_text("""Dieses Tool ist zur Nutzung in einer Studie entwickelt.
                                    Ihr werdet von eurer Lehrkraft in eine Kontrollgruppe und eine Experimentalgruppe eingeteilt.
                                    Nutze die entsprechenden Button je nachdem, wie du eingeteilt bist, um loszulegen.
                                    
                                    *Zwischen den Schritten kann es zu Wartezeiten kommen, da die Antwort der KI Zeit benötigt.
                                    Bitte gedulde dich und lade nicht die Seite neu. Das führt nur zu neuen Anfragen an die KI und verlängert deine Wartezeit.*
                                    
                                    Bevor du anfängst, fülle bitte die Vorumfrage aus, insofern du an der Studie teilnimmst.
                                    """).style('margin-left: 10%; margin-right: 10%')

            ui.button("Teilnahme an der Vorumfrage", on_click=lambda: ui.navigate.to("https://cryptpad.fr/form/#/2/form/view/rEpyzVy1ixXJbHELucLHyHNXjWjd9ByDePDkkDOu2C0/", new_tab=True))

            with ui.row():
                with ui.card().classes("col-5"):
                    ui.markdown("Experimentalgruppe")
                    ui.restructured_text("""Mit dem Tool wirst du Datenbanken zu Themen deiner Wahl mithilfe von KI erstellen.
                                    Zu der Datenbank werden dir entsprechende Aufgaben gestellt.
                                    
                                    Falls du bereits eine Datenbank erstellt hast, die du wiederverwenden möchtest, klicke auf **Lade Datenbank hoch**.
                                    Falls du noch keine Datenbank erstellt hast, oder eine neue erstellen möchtest, klicke auf **Erstelle Datenbank**.""")
                    ui.button("Erstelle Datenbank", on_click=lambda: ui.navigate.to("/Themenwahl"))
                    ui.button("Lade Datenbank hoch", on_click=lambda: ui.navigate.to("/Upload"))

                with ui.card().classes("col-5"):
                    ui.markdown("Kontrollgruppe")
                    ui.restructured_text("""Du kannst direkt mit der Aufgabenbearbeitung loslegen.
                                    Klicke auf **Zur Kurswahl** um zu beginnen.""")
                    ui.button("Zur Kurswahl", on_click=lambda: ui.navigate.to("/Kurswahl2"))

            ui.button("Teilnahme an der Nachumfrage", on_click=lambda: ui.navigate.to("https://cryptpad.fr/form/#/2/form/view/v1pD9HRuMrT9mytSd2yxBCkn9T6rXGQCr21Pndo-Lk8/", new_tab=True))