import logging
import tempfile
import json

import azure.functions as func
from roboflow import Roboflow

rf = Roboflow(api_key="HOCRxNRROICgFZfge4M8")
project = rf.workspace().project("frescis")
model = project.version(1).model


def main(req: func.HttpRequest) -> func.HttpResponse:

    # Check if the request contains a file named 'image'
    if 'image' not in req.files:
        return func.HttpResponse("No 'image' file provided.", status_code=400)

    # Retrieve the file from the request
    file = req.files['image']

    # Create a temporary file
    tmp_file_path = ""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_path = tmp_file.name

        # Save the file data to the temporary file
        file.save(tmp_file_path)

    # Make predictions on the image
    result = model.predict(tmp_file_path).json()
    result_json = json.dumps(result)

    headers = {
        "Content-Type": "application/json"
    }

    return func.HttpResponse(result_json, headers=headers)
