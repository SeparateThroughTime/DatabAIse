import justpy
from justpy import SetRoute
from openai import OpenAI


@SetRoute("/")
def get_first(request):
    webpage = justpy.WebPage()
    print("1")

    form = justpy.Form(a=webpage)
    submit_button = justpy.Input(value="Senden", type="submit", a=form)
    form.on("submit", on_submit)

    prompt()
    return webpage


def on_submit(self, msg):
    msg.page.redirect = "/second"


@SetRoute("/second")
def get_second(request):
    webpage = justpy.WebPage()
    print("2")

    form = justpy.Form(a=webpage)
    submit_button = justpy.Input(value="Senden2", type="submit", a=form)
    form.on("submit", on_submit)

    prompt()
    return webpage


def prompt():
    ai_client = OpenAI(api_key="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")
    response = ai_client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": "Say Hello"},
        ],
        model="gpt-5-nano",
        stream=False)


if __name__ == "__main__":
    justpy.justpy()