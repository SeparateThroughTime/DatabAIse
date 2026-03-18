from nicegui import ui, app

import DatabAIse
from DatabAIse import test_sql
import CssStyles


def on_create_db(self, msg):
    msg.page.redirect = "/Themenwahl"


def on_upload_db(self, msg):
    msg.page.redirect = "/Upload"


def get_page():
    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.image("images/logo.png").props("width=60%")
            ui.restructured_text("""Mit diesem Tool kannst du Datenbanken zu einem Thema deiner Wahl erstellen lassen!
                                    Mithilfe von KI werden Kurse zu allen SQL-Themen generiert, die du absolvieren kannst.
                                    
                                    Falls du bereits eine Datenbank erstellt hast, die du wiederverwenden möchtest, klicke auf **Lade Datenbank hoch**.
                                    Falls du noch keine Datenbank erstellt hast, oder eine neue erstellen möchtest, klicke auf **Erstelle Datenbank**.
                                    
                                    *Zwischen den Schritten kann es zu kurzen Wartezeiten kommen, da die Antwort der KI Zeit benötigt.
                                    Bitte gedulde dich und lade nicht die Seite neu. Das führt nur zu neuen Anfragen an die KI und verlängert deine Wartezeit.*""").style('margin-left: 10%; margin-right: 10%')

            ui.button("Erstelle Datenbank", on_click=lambda: ui.navigate.to("/Themenwahl"))
            ui.button("Lade Datenbank hoch", on_click=lambda: ui.navigate.to("/Upload"))