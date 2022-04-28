import json
import requests
import urllib
import boto3
import csv
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import decimalencoder

def lambda_handler(event, context):
    try:
        id = ""
        try:
            id = event['queryStringParameters']['id']
        except:
            id = ""

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODBTABLE'])
        # filtering_exp = Key(filter_key).eq(filter_value)
        # response = table.scan(FilterExpression=filtering_exp)
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

        # varTmpRet = json.dumps(dataRet)
        exportCsv = ""
        try:
            exportCsv = event['queryStringParameters']['export']
        except:
            exportCsv = ""
        
        contents = ""
        if exportCsv == "csv":
            # open a file for writing
            csv_data = open('/tmp/csv_file.csv', 'w')
            # create the csv writer object
            csvwriter = csv.writer(csv_data)

            count = 0
            for item in dataRet:
                if count == 0:
                        header = item.keys()
                        csvwriter.writerow(header)
                        count += 1
                csvwriter.writerow(item.values())


            csv_binary = open('/tmp/csv_file.csv', 'rb').read()
            csv_data.close()
            headers = {}
            headers[str("content-type")] = 'text/csv'
            headers['Content-Disposition'] = 'attachment;filename="Endpoints.csv"'

            return {
                "statusCode": 200,
                "isBase64Encoded": "false",
                "headers": headers,
                "body": contents
            }

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