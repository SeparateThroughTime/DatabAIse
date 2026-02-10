import io
import starlette.responses
import justpy
from six import StringIO
import DatabAIse

def get_page(request):
    print("redirected")

    sql_string = DatabAIse[request.session_id]["sql_string"]
    topic = DatabAIse[request.session_id]["topic"]

    sql_file = StringIO(sql_string)
    sql_file.seek(0)
    return starlette.responses.StreamingResponse(
        content=sql_file,
        headers={'Content-Disposition':'attachment; filename="' + topic + '.sql"'}
    )

