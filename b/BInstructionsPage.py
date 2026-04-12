from nicegui import ui
import CssStyles

def get_page():
    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.image("images/logo.png").props("width=60%")
            ui.restructured_text("""Dieses Tool ist zur Nutzung in einer Studie entwickelt.
                                    Ihr werdet von eurer Lehrkraft in Gruppe A und Gruppe B eingeteilt.
                                    Hier bist du richtig, wenn du in **Gruppe B** eingeteilt wurdest.
                                    
                                    *Zwischen den Schritten kann es zu Wartezeiten kommen, da die Antwort der KI Zeit benötigt.
                                    Bitte gedulde dich und lade nicht die Seite neu. Das führt nur zu neuen Anfragen an die KI und verlängert deine Wartezeit.*
                                    
                                    Bevor du anfängst, fülle bitte die Vorumfrage aus, insofern du an der Studie teilnimmst.
                                    """).style('margin-left: 10%; margin-right: 10%')

            ui.button("Teilnahme an der Vorumfrage", on_click=lambda: ui.navigate.to("https://cryptpad.fr/form/#/2/form/view/rEpyzVy1ixXJbHELucLHyHNXjWjd9ByDePDkkDOu2C0/", new_tab=True))

            with ui.card().classes("col-6"):
                ui.restructured_text("""Du kannst direkt mit der Aufgabenbearbeitung loslegen.
                                Klicke auf **Zur Kurswahl** um zu beginnen.""")
                ui.button("Zur Kurswahl", on_click=lambda: ui.navigate.to("/b/Kurswahl"))

            ui.button("Teilnahme an der Nachumfrage", on_click=lambda: ui.navigate.to("https://cryptpad.fr/form/#/2/form/view/v1pD9HRuMrT9mytSd2yxBCkn9T6rXGQCr21Pndo-Lk8/", new_tab=True))