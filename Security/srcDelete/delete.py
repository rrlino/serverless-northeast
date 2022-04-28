import json
import requests
import urllib
import boto3
from botocore.exceptions import ClientError
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

        result = table.get_item(
            Key={
                'Id': id
            }
        )
        response = result['Item']

        timestamp = str(datetime.utcnow())
        # update the item in the database
        dataRet = table.update_item(
            Key={
                'Id': id
            },
            ExpressionAttributeValues={
            ':UpdatedAt': timestamp,
            ':Enabled':false
            },
            UpdateExpression='SET Enabled = :Enabled, '
                            'UpdatedAt = :UpdatedAt',
            ReturnValues='ALL_NEW',
        )

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