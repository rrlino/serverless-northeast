import json
import requests
import urllib
import boto3
from botocore.exceptions import ClientError
import logging
import os
import uuid
from datetime import datetime
import decimalencoder

def lambda_handler(event, context):
    try:
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
        
        timestamp = str(datetime.utcnow())
        # Set the item to set to the payload
        item = payload
        # Set additional item propeties that we create
        item['Id'] = str(uuid.uuid1()).replace("-", "")
        item['Enabled'] = True
        item['CreatedAt'] = timestamp
        item['UpdatedAt'] = timestamp
        
        # write the item to the database
        result = table.put_item(Item=item)
        dataRet = item

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