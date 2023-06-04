import logging
import tempfile
import json

import azure.functions as func

from roboflow import Roboflow
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader

# Roboflow
rf = Roboflow(api_key="HOCRxNRROICgFZfge4M8")
project = rf.workspace().project("frescis")
model = project.version(3).model
 
# Cloudinary
cloudinary.config(
    cloud_name='drziipos7',
    api_key='275238259143145',
    api_secret='90LCTp-FwqSbpikx77HGItV8qt8'
)


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

    # Save image
    response = cloudinary.uploader.upload(tmp_file_path)
    logging.info("response", response)

    result["image_url"] = str(response["secure_url"])
    result["uid"] = req.form.get("uid")
    result_json = json.dumps(result)

    # Save to histories
    cosmos_uri = "mongodb://frescis-mongo:w6zrCWZbMjBWkPOLTD7BarZHD91ZRgJFh2j7KupPwIp2ciSlvSnNC2oUBjhk1Ju4jcFssNyCWJO2ACDbCB9q7w==@frescis-mongo.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@frescis-mongo@"
    client = MongoClient(cosmos_uri)

    db = client["frescis-db"]
    collection = db["histories"]

    # result['uid'] = req.form.get('uid')
    collection.insert_one(result)

    client.close()

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        "Content-Type": "application/json"
    }

    return func.HttpResponse(result_json, headers=headers)
