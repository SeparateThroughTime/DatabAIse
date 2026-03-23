from nicegui import ui, html, app


def get_page():
    app.add_static_files("/Lizenzen", "licenses")
    with ui.column().classes("items-stretch").style("max-width: 700px; min-width: 30%"):
        with html.table().style("text-align: center; border: 1px solid black;"):
            with html.tr():
                with html.th():
                    ui.label("Software").style("text-align: center")
                with html.th():
                    ui.label("Lizenz").style("text-align: center")

            with html.tr():
                with html.td():
                    ui.link("Deepseek Model", "https://www.deepseek.com/")
                with html.td():
                    ui.link("Deepseek License Agreement", "/Lizenzen/DEEPSEEK_MODEL")

            with html.tr():
                with html.td():
                    ui.link("Google Gen AI SDK", "https://github.com/googleapis/python-genai")
                with html.td():
                    ui.link("MIT License", "/Lizenzen/GOOGLE_API")

            with html.tr():
                with html.td():
                    ui.link("Google Gemini Model", "https://gemini.google/de/about/?hl=de")
                with html.td():
                    ui.link("Google Terms of Service", "https://ai.google.dev/gemini-api/terms")

            with html.tr():
                with html.td():
                    ui.link("NiceGUI", "https://nicegui.io/")
                with html.td():
                    ui.link("BSD 3-Clause", "/Lizenzen/PANDAS")

            with html.tr():
                with html.td():
                    ui.link("OpenAI Model", "https://openai.com")
                with html.td():
                    ui.link("OpenAI Europe Terms of Use", "https://openai.com/policies/eu-terms-of-use/")

            with html.tr():
                with html.td():
                    ui.link("OpenAI Python API library", "https://github.com/openai/openai-python")
                with html.td():
                    ui.link("BSD 3-Clause", "/Lizenzen/OPENAI")

            with html.tr():
                with html.td():
                    ui.link("pandas", "https://pandas.pydata.org/")
                with html.td():
                    ui.link("MIT License", "/Lizenzen/NICEGUI")

            with html.tr():
                with html.td():
                    ui.link("Python", "https://www.python.org/")
                with html.td():
                    ui.link("PSF 2 License", "/Lizenzen/PYTHON")

            with html.tr():
                with html.td():
                    ui.link("SQLite3 python library", "https://pypi.org/project/pysqlite3/")
                with html.td():
                    ui.link("MIT License", "/Lizenzen/SQLITE3")