import io
import starlette.responses
import justpy
from six import StringIO
import DatabAIse

def get_page(request):
    webpage = justpy.WebPage()
    print("redirected")

    topic = ""
    sql_string = ""
    for field in DatabAIse.session_data[request.session_id]["msg_form_date"]:
        if field.name == "topic":
            topic = field.value
        if field.name == "sql":
            sql_file = field.value

    sql_file = StringIO(sql_string)
    sql_file.seek(0)
    return starlette.responses.StreamingResponse(
        content=sql_file,
        headers={'Content-Disposition':'attachment; filename="' + topic + '.sql"'}
    )