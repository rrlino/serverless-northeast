import json
import requests
import boto3
import uuid
import os
from datetime import datetime
from botocore.exceptions import ClientError

API = 'https://api.ssllabs.com/api/v3/'
print('Check Job status function')

def lambda_handler(event, context):
    # Log the received event
    print("Received event: " + json.dumps(event, indent=2))

    environment = ""
    try:
        environment = os.environ['ENVIRONMENT']
    except:
        environment = "dev"
        
    try:

        path = 'analyze'
        payloadSslLabs = {
            'host': event['Url'],
            'publish': 'off',
            'all': 'on',
            'ignoreMismatch': 'on'
        }
        urlSslLabsApi = API + path

        try:
            response = requests.get(urlSslLabsApi, params=payloadSslLabs)
        except requests.exception.RequestException:
            logging.exception('Request failed.')

        responseStatusCode = response.status_code

        event['status'] = "wait"

        if responseStatusCode == 400:
            event['status'] = "[API] invocation error"
        elif responseStatusCode == 429:
            event['status'] = "[API] client request rate too high or too many new assessments too fast"
        elif responseStatusCode == 500:
            event['status'] = "[API] internal error"
        elif responseStatusCode == 503:
            event['status'] = "[API] the service is not available"
        elif responseStatusCode == 529:
            event['status'] = "[API] the service is overloaded"
        elif responseStatusCode == 200:
            response = response.json()
            event['status'] = response['status']
        else:
            print('Other')
        
        event['error'] = ""
        if "errors" in response:
            event['status'] = "ERROR"
            event['error'] = response['errors'][0]['message']
            print("event['error'] : " + event['error'])
            
        print("event['status'] : " + event['status'])

        if event['status'] == "READY":
            fileName = event['Url'] + "_" + str(uuid.uuid1()).replace("-", "") + ".json"
            print(fileName)
            s3 = boto3.resource('s3')
            bucketName = "rrlino-serverless"
            try:
                s3.Object(bucketName, fileName).put(Body=json.dumps(response))
            except ClientError as e:
                print("Unexpected error: %s" % e)
            event['result'] = { "bucket" : bucketName, "key" : fileName} 

        return event
    except Exception as inst:
        print(inst)
