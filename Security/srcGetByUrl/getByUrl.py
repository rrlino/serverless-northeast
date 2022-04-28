import json
import requests
import urllib
import boto3
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
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

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODBTABLE'])
        
        response = table.scan(FilterExpression=Attr('Url').eq(id))
        print(response)
        dataRet = response['Items']
        
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