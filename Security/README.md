## Journey into Serverless with Automation
## Check the SSL from your endpoints

* [GET] - `HealthCheck` - /HealthCheck
* [GET] - `List` - /
* [GET] - `GetById` - /{id}
* [POST] - `Post` - /
* [PUT] - `Put` - /{id}
* [DELETE] - `Delete` - /{id}

## Deploy the application


sam build --use-container --skip-pull-image && sam package --output-template-file packaged.yaml --s3-bucket rrlino-serverless --profile serverless_north_east && sam deploy --template-file packaged.yaml --profile serverless_north_east --capabilities CAPABILITY_NAMED_IAM --stack-name Serverless-North-East-SSL-Checker


## Payload

Basic contract:
```json
{
  "Id": "76298ab30f8143c0eb44de2be1050e2d",
  "UpdatedAt": "2021-12-22 22:48:26.582883",
  "Url": "www.bbc.co.uk",
  "Enabled": true,
  "CreatedAt": "2021-12-22 21:18:55.722570"
}
```