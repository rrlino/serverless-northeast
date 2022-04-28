import json
import requests
import time
import sys
import logging
import urllib
import boto3
import csv
import os
import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import decimalencoder


def lambda_handler(event, context):
    try:
        sqsQueue = ""
        try:
            sqsQueue = os.environ['QUEUE_URL']
        except:
            sqsQueue = ""

        sslRecheckHours = 0
        try:
            sslRecheckHours = int(os.environ['SSLRECHECKHOURS'])
        except:
            sslRecheckHours = 12

        dynamoDBTable = ""
        try:
            dynamoDBTable = os.environ['DYNAMODBTABLE']
        except:
            dynamoDBTable = "TBD"

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(dynamoDBTable)
        response = table.scan()

        items = response['Items']
        while True:
            print('qtyItems: ' + str(len(response['Items'])))
            if response.get('LastEvaluatedKey'):
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items += response['Items']
            else:
                break

        dataRet = items
        arrRet = []
        for x in dataRet:
            current_date_time = datetime.datetime.now()
            if "LastCheck" not in x.keys():
                tmpLastCheck = current_date_time + datetime.timedelta(hours = -24)
                x["LastCheck"] = tmpLastCheck.strftime('%Y-%m-%d %H:%M:%S.%f')
                print("x[LastCheck]: " + x["LastCheck"])

            tmpLastCheck = datetime.datetime.strptime(x["LastCheck"], '%Y-%m-%d %H:%M:%S.%f')
            hours_added = datetime.timedelta(hours = sslRecheckHours)
            
            expireDateTime = tmpLastCheck + hours_added
            print("expireDateTime: " + expireDateTime.strftime('%Y-%m-%d %H:%M:%S.%f'))

            if expireDateTime < current_date_time:
                print("inputStep: " + json.dumps(x))
                respSqs = send_sqs_message(sqsQueue, x)
                x['responseSqs'] = json.dumps(respSqs)
                arrRet.append(x)
            
            time.sleep(1.2)
        
        return {
            "statusCode": 200,
            "isBase64Encoded": "false",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(arrRet, cls=decimalencoder.DecimalEncoder)
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