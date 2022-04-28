import json
import requests
import urllib
import boto3
import csv
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import decimalencoder

def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODBTABLE'])
        dataRet = {}
        print(json.dumps(event))
        operation = event['requestContext']['http']['method']

        if operation == "POST":
            #Check token somehow... for now blocked...
            return {
                "statusCode": 401,
                "isBase64Encoded": 'false',
                "headers":{"Content-Type": "application/json"},
                "body":json.dumps({"message": "Unauthorized"})
            }
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

            result = {
                "statusCode": 200,
                "isBase64Encoded": "false",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(dataRet, cls=decimalencoder.DecimalEncoder)
            }
            
            print ("result", json.dumps(result)) 
        else:
            #operation == GET

            id = ""
            try:
                id = event['queryStringParameters']['id']
            except:
                id = ""

            response = table.scan()
            items = response['Items']
            while True:
                # print('qtyItems: ' + str(len(response['Items'])))
                if response.get('LastEvaluatedKey'):
                    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    items += response['Items']
                else:
                    break
            
            dataRet = items
            
            result = {
                "statusCode": 200,
                "isBase64Encoded": "false",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(dataRet, cls=decimalencoder.DecimalEncoder)
            }

        return result
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