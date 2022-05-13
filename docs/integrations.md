# Integrations
Integrations are bridge between `serverless-builder` and third party libraries.


## AWS Lambda Powertools Python
[AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/) is great tool! If you haven't used it yet have a look!
`serverless-builder` integrates with it in few places

### Enable it
```python
from serverless.integration.powertools import Powertools

service.enable(Powertools())
```

### Automatically sets ENV variables
It will set `POWERTOOLS_SERVICE_NAME` and `POWERTOOLS_LOGGER_LOG_EVENT` ENV variables.

### Creates idempotency DynamoDB table
To be able to use [idempotency](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/idempotency/) you need to create separated DynamoDB table for your service.

`with_idempotency` function allows you to create both, dynamodb table, and set correct IAM permissions for it.

You can use it for any lambda function.

```python
# example of use with `http_get`
service.builder.function.http_get(
    "test-list", 
    "List all tests", 
    "/"
).with_idempotency()
```

It will generate following YAML
```yaml
service: service-name
provider:
...
  iam:
    role:
      statements:
      - Sid: ServiceNameTestListIdempotencyFullAccess
        Effect: Allow
        Action:
        - dynamodb:GetItem
        - dynamodb:Query
        - dynamodb:Scan
        - dynamodb:BatchWriteItem
        - dynamodb:DeleteItem
        - dynamodb:UpdateItem
        - dynamodb:PutItem
        Resource:
        - Fn::GetAtt:
          - ServiceNameTestListIdempotency
          - Arn
      name: ${self:service}-${sls:stage}-${aws:region}-service

functions:
  TestList:
    name: service-name-${sls:stage}-test-list
    description: List all tests
    handler: service_name.test-list.handler
    events:
    - http:
        path: /
        method: GET
    environment:
      IDEMPOTENCY_TABLE:
        Ref: ServiceNameTestListIdempotency

resources:
...
    ServiceNameTestListIdempotency:
      Properties:
        TableName: ServiceName${sls:stage}TestListIdempotency
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
        KeySchema:
        - AttributeName: id
          KeyType: HASH
        TimeToLiveSpecification:
          AttributeName: expiration
          Enabled: true
        PointInTimeRecoverySpecification:
          PointInTimeRecoveryEnabled: true
      Type: AWS::DynamoDB::Table
      DeletionPolicy: Retain
```

???+ info "Info: You can use it without enabling integration"
     Running `service.enable(Powertools())` is not required but highly recommended

???+ warning "Warning: You still need to setup your lambda to use idempotency"
     You still need to follow [idempotency configuration](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/idempotency/#idempotent-decorator) for your lambda to use this table

## Sentry

### Enable it
```python
from serverless.integration.sentry import Sentry

service.enable(Sentry("https://5eb925ae-ee50-47c4-b5e8-a240cf834820@47c4.ingest.sentry.io/123456789"))
```

### Automatically sets ENV variables
It will automatically set `SENTRY_DSN`, `SENTRY_ENVIRONMENT` and `SENTRY_RELEASE`.

???+ info "Info: Set version in ENV"
     Your Ci/CD needs to set `VERSION` ENV variable with current release version.
