import json
import requests
import urllib
import boto3
import os
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    try:
        environment = ""
        try:
            environment = os.environ['ENVIRONMENT']
        except:
            environment = "prod"

        urlEndpoints = ""
        try:
            urlEndpoints = os.environ['URLENDPOINTS']
        except:
            urlEndpoints = "https://4c580kazfg.execute-api.eu-west-1.amazonaws.com/Prod/"
            
        
        # event = {
        #     "Url": "www.bbc.co.uk",
        #     "Id": "5ce2fdc8b98611eab461d2b07a929316",
        #     "status": "READY",
        #     "error": "",
        #     "result": {
        #     "bucket": "rrlino-serverless",
        #     "key": "www.bbc.co.uk_82ddba1cf63611ea9faf4e6064841c1f.json"
        #     }
        # }
        print(json.dumps(event, indent=2))

        s3 = boto3.resource('s3')
        content_object = s3.Object(event['result']['bucket'], event['result']['key'])
        file_content = content_object.get()['Body'].read().decode('utf-8')
        sslReport = json.loads(file_content)


        tagsToPost = {}
        tagsToPost['Url'] = sslReport['host'].replace(".", "_")
        
        tempCalcInSeconds = sslReport['testTime'] - sslReport['startTime']
        tempCalcInSeconds = tempCalcInSeconds / 1000
        
        expDateDays = 365
        tagsToPost['ExpireNext30Days'] = "false"
        # tagsToPost['TimeToGetReportInSec'] = tempCalcInSeconds
        expireDate = datetime.utcfromtimestamp(sslReport['certs'][0]['notAfter']/1000)
        expDateDays = (expireDate.date() - datetime.utcnow().date()).days
        print("days: " + str(expDateDays))

        if expDateDays <= 30:
            tagsToPost['ExpireNext30Days'] = "true"
        
        tagsToPost['QtyEndpoints'] = len(sslReport['endpoints'])
        tmpEndpoint = sslReport['endpoints'][0]
        tagsToPost['Grade'] = tmpEndpoint['grade']
        tmpProtocol = tmpEndpoint['details']['protocols'][0]
        if tmpProtocol['version'] == "1.0":
            tagsToPost['tls'] = tmpProtocol['version'].replace(".", "_")
            
        if 'tls' not in tagsToPost.keys() and tmpProtocol['version'] == "1.1":
            tagsToPost['tls'] = tmpProtocol['version'].replace(".", "_")
            
        if 'tls' not in tagsToPost.keys() and tmpProtocol['version'] == "1.2":
            tagsToPost['tls'] = tmpProtocol['version'].replace(".", "_")
            
        if 'tls' not in tagsToPost.keys() and tmpProtocol['version'] == "1.3":
            tagsToPost['tls'] = tmpProtocol['version'].replace(".", "_")

        if "Id" in event.keys():
            apiUrl = urlEndpoints + event['Id']
            print(apiUrl)
            headers = {"Content-Type": "application/json"}
            response = requests.get(apiUrl, headers=headers, timeout=120)
            endpointItem = json.loads(response.text)
            print(json.dumps(endpointItem))
            endpointUrl = endpointItem['Url']

            endpointItem['LastCheck'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            endpointItem['S3Bucket'] = event['result']['bucket']
            endpointItem['S3File'] = event['result']['key']
            
            del endpointItem['Url']
            del endpointItem['Id']
            del endpointItem['CreatedAt']

            response = requests.put(apiUrl, headers=headers, data=json.dumps(endpointItem), timeout=120)
            #print(json.dumps(endpointItem))
            #print("Response PUT Endpoint: " + endpointUrl + " : " + response.text)
        
        return {
            "statusCode": 200,
            "isBase64Encoded": "false",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(event)
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