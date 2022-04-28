import json
import requests
import urllib
import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime
import decimalencoder

def lambda_handler(event, context):
    try:
        id = ""
        try:
            id = event['pathParameters']['id']
        except:
            ret = {
                "statusCode": 400,
                "isBase64Encoded": 'false',
                "headers":{"Content-Type": "application/json"},
                "body": json.dumps({
                    "Error" : "missing id"
                })
            }
            return ret
        
        payload = ""
        try:
            payload = json.loads(event['body'])
        except:
            ret = {
                "statusCode": 400,
                "isBase64Encoded": 'false',
                "headers":{"Content-Type": "application/json"},
                "body": json.dumps({
                    "Error" : "missing payload"
                })
            }
            return ret
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODBTABLE'])

        result = table.get_item(
            Key={
                'Id': id
            }
        )
        response = result['Item']
        timestamp = str(datetime.utcnow())
        payload['UpdatedAt'] = timestamp
        
        for x in payload.keys():
            response[x] = payload[x]


        response = result['Item']
        timestamp = str(datetime.utcnow())

        jsonExpressionAttributeValues = {}
        strUpdateExpression = "SET "
        for x in payload.keys():
            jsonExpressionAttributeValues[':' + x] = payload[x]
            strUpdateExpression = strUpdateExpression + x + " =:" + x + ", "

        if strUpdateExpression.strip()[-1] == ",":
            strUpdateExpression = strUpdateExpression.strip()[0:-1]

        result = table.update_item(
            Key={'Id': response['Id']},
            ExpressionAttributeValues=jsonExpressionAttributeValues,
            UpdateExpression=strUpdateExpression,
            ReturnValues='ALL_NEW',
        )
        dataRet = result['Attributes']

        return {
            "statusCode": 200,
            "isBase64Encoded": "false",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(dataRet, cls=decimalencoder.DecimalEncoder)
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

# tmpRet = lambda_handler(None, None)
# tmpRet2 = tmpRet