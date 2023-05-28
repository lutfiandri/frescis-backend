import json
from bson import json_util


import azure.functions as func
from pymongo import MongoClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    # Retrieve the UID from the query parameters
    uid = req.params.get('uid')

    if not uid:
        return func.HttpResponse(
            "Please provide a UID parameter in the query string.",
            status_code=400
        )

    # Assuming you have a MongoDB connection running
    cosmos_uri = "mongodb://frescis-mongo:w6zrCWZbMjBWkPOLTD7BarZHD91ZRgJFh2j7KupPwIp2ciSlvSnNC2oUBjhk1Ju4jcFssNyCWJO2ACDbCB9q7w==@frescis-mongo.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@frescis-mongo@"
    client = MongoClient(cosmos_uri)

    db = client["frescis-db"]
    collection = db["histories"]

    # Create a query object to match the UID
    query = {'uid': uid}

    # Use the find method to retrieve all matching documents
    cursor = collection.find(query)

    # Convert the documents to a list
    histories = list(cursor)
    new_histories = []

    for history in histories:
        # Convert the ObjectId to a string
        history['_id'] = str(history['_id'])
        new_histories.append(history)

    # Close the MongoDB connection
    client.close()

    result = {
        'histories': new_histories
    }

    result_json = json.dumps(result, default=json_util.default)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        "Content-Type": "application/json"
    }

    # Return the retrieved histories as the HTTP response
    return func.HttpResponse(body=result_json, headers=headers)
