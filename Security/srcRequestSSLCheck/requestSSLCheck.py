import json
import requests
import time
import sys
import logging
import urllib
import boto3
import csv
import os
from botocore.exceptions import ClientError

sslLabsAPIUrl = 'https://api.ssllabs.com/api/v3/analyze'

def lambda_handler(event, context):
    try:

        sqsDlqQueue = ""
        try:
            sqsDlqQueue = os.environ['DLQUEUE_URL']
        except:
            sqsDlqQueue = ""


        stepFunctionArn = ""
        try:
            stepFunctionArn = os.environ['SSLSTEPFUNCTIONARN']
        except:
            stepFunctionArn = "TBD"

        stepFunctionName = ""
        try:
            stepFunctionName = os.environ['SSLSTEPFUNCTIONNAME']
        except:
            stepFunctionName = "TBD"
        
        dataRet = []

        if "Records" in event.keys():
            #Assume this lambda will be triggered by SQS, so event will be messages
            for record in event['Records']:
                payload = json.loads(record['body'], parse_float=str)
                operation = record['messageAttributes']['Method']['stringValue']
                print(json.dumps(payload))
                print(operation)
                dataRet.append(payload)
        elif event['body'] != None:
            payload = json.loads(event['body'])
            print(json.dumps(payload))
            dataRet.append(payload)

        arrRet = []
        for x in dataRet:
            # print("stepFunctionArn: " + stepFunctionArn)
            # print("stepFunctionName: " + stepFunctionName)
            print("inputStep: " + json.dumps(x))

            sslLabsApiPayload = {
                'host': x['Url'],
                'publish': 'off',
                'startNew': 'on',
                'all': 'done',
                'ignoreMismatch': 'on'
            }

            try:
                response = requests.get(sslLabsAPIUrl, params=sslLabsApiPayload)
            except requests.exception.RequestException:
                logging.exception('Request failed.')
            
            responseStatusCode = response.status_code
            
            print("response.status_code: " + str(response.status_code))
            x['status'] = "wait"

            if responseStatusCode == 400:
                x['status'] = "[SSL LABS API] invocation error"
            elif responseStatusCode == 404:
                x['status'] = "[SSL LABS API] not found"
                x['error'] = x['status']
            elif responseStatusCode == 429:
                x['status'] = "[SSL LABS API] client request rate too high or too many new assessments too fast"
            elif responseStatusCode == 500:
                x['status'] = "[SSL LABS API] internal error"
                x['error'] = x['status']
            elif responseStatusCode == 503:
                x['status'] = "[SSL LABS API] the service is not available"
                x['error'] = x['status']
            elif responseStatusCode == 529:
                x['status'] = "[SSL LABS API] the service is overloaded"
                x['error'] = x['status']
            elif responseStatusCode == 200:
                response = response.json()
                x['status'] = response['status']
            else:
                print('Other')
            
            
            if "errors" in response:
                x['status'] = "ERROR"
                msgError = response['errors'][0]['message']
                if "error" in x:
                    x['error'] = x['error'] + msgError
                else:
                    x['error'] = msgError
                
            print("x['status'] : " + x['status'])
            if 'error' not in x:
                client = boto3.client('stepfunctions')
                response = client.start_execution(
                    stateMachineArn=stepFunctionArn,
                    input= json.dumps(x)
                )
                x['executionArn'] = response.get('executionArn')
            else:
                #post to DLQ:
                respSqs = send_sqs_message(sqsDlqQueue, x)
                x['responseDlqSqs'] = json.dumps(respSqs)

            arrRet.append(x)
        
        return {
            "statusCode": 200,
            "isBase64Encoded": "false",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(arrRet)
        }
    except Exception as inst:
        print(type(inst))    # the exception instance
        print(inst.args)     # arguments stored in .args
        print(inst)          # __str__ allows args to be printed directly, but may be overridden in exception subclasses
        return {
            "statusCode": 500,
            "isBase64Encoded": 'false',
            "headers":{"Content-Type": "application/json"},
            "body": {
                "Error" : "Error"
            }
        }

def send_sqs_message(sqs_queue_url, message):
    """
    Send JSON-format message to SQS.
    :param message: Dictionary message object
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """
    sqs_client = boto3.client('sqs')
    try:
        response = sqs_client.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps(message),
            DelaySeconds=0,
            MessageAttributes={
                'Method': {
                    'StringValue': 'POST',
                    'DataType': 'String'
                }
            }
        )
        return response
    except ClientError as e:
        print(e)
        return e
# tmpRet = lambda_handler(None, None)
# tmpRet2 = tmpRet