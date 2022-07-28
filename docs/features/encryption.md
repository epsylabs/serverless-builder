# Encryption

One of the core assumption behind serverless-builder was to simplify a process of building reliable and secure
services with best practices applied by default - that means full support for encryption at rest and in transit.

`serverless-builder` has a built-in support for [AWS KMS](https://aws.amazon.com/kms/) encryption with per service encryption key.

**Enabling encryption feature**

```python
from serverless.service.environment import Environment
from serverless.aws.provider import Provider as AWSProvider
from serverless import Service
from serverless.aws.features.encryption import Encryption

service = Service(
    "serverless-builder-demo",
    "serverless-builder demo service",
    environment=Environment(),
    provider=AWSProvider()
)

service.enable(Encryption())

service.render()
```

Importing an Encryption feature will perform a coupe of things: 

1. Create a new Customer managed key with AWS KMS with relevant usage policy (Resource name: `ServiceEncryptionKey` )
2. Create a new KMS Alias matching `alias/${self:service}-${sls:stage}` pattern (Resource name: `ServiceEncryptionKeyAlias`)
3. Import and configure [serverless-kms-grants](https://www.serverless.com/plugins/serverless-kms-grants) plugin for managing usage permissions on service encryption key

**Side effects**

Each function registered with serverless-builder will be added to `serverless-kms-grants` plugin configuration without any additional work.

```python
service.builder.function.generic("show", "Show function")
```

will be translated into:

```yaml
  kmsGrants:
  - kmsKeyId: alias/${self:service}-${sls:stage}
    roleName: ${self:service}-${sls:stage}-${aws:region}-service-6dbb8
```

Please note that IAM roles have autogenerated suffixes to enforce globally unique names. 
Please check `serverless-builder` naming conventions for more details.

## LogGroups

By default serverless framework is using unencrypted logs. If you enable Encryption feature `serverless-builder` will overwrite this behaviour for all registered lambda functions
and will enable log encryption with created KMS key.

## Secrets

If you need to store secrets in your application you should use [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/),
`serverless-builder` makes this integration much simpler.

```python
from serverless.aws.iam.secrets_manager import SecretsManagerReader
from serverless.aws.resources.kms import EncryptableResource
from troposphere.secretsmanager import Secret

secret = "/services/${self:service}/${sls:stage}"

self.provider.iam.apply(SecretsManagerReader(secret))
self.resources.add(Secret(title="ServiceSecret", KmsKeyId=EncryptableResource.encryption_alias(), Name=secret))
```

AWS by default uses default AWS managed KMS key for encrypting secrets, but you can change that behaviour to use
service owned encryption key. 

## DynamoDB

`serverless-builder` is providing a `troposphere` compatible `DynamoDB` resource definition with some extra features including
integrated support for server side encryption.

Whenever you need to create a new DynamoDB table it's recommend to use implementation provided by `serverless-builder`

```python
from serverless.aws.resources.dynamodb import Table
from troposphere.dynamodb import AttributeDefinition, KeySchema

table = Table(
    "SampleTable",
    BillingMode="PAY_PER_REQUEST",
    AttributeDefinitions=[
        AttributeDefinition(AttributeName="id", AttributeType="S"),
    ],
    KeySchema=[
        KeySchema(AttributeName="id", KeyType="HASH"),
    ],
)
service.resources.add(table)
```

`serverless-builder` will translate that into a valid table definition with KMS encryption enabled, it will also define `DepndsOn` 
to ensure that table is created after encryption key and aliases are available. 

```yaml
    SampleTable:
      Properties:
        TableName: ServerlessBuilderDemoSampleTable-${sls:stage}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
        KeySchema:
        - AttributeName: id
          KeyType: HASH
        PointInTimeRecoverySpecification:
          PointInTimeRecoveryEnabled: true
        SSESpecification:
          SSEEnabled: true
          SSEType: KMS
          KMSMasterKeyId:
            Ref: ServiceEncryptionKey
      Type: AWS::DynamoDB::Table
      DeletionPolicy: Retain
      DependsOn:
      - ServiceEncryptionKeyAlias
```

## S3 Buckets

`serverless-builder` is providing a S3 Bucket wrapper which is supporting server side encryption by default, you should use it 
whenever you need to create new S3 bucket.

```python
from serverless.aws.resources.s3 import S3Bucket

bucket = S3Bucket(
    "sample-bucket"
)
service.resources.add(bucket)
```

`S3Bucket` class will automatically take care of setting up encryption for your bucket, and will generate yaml similar to 
that one:

```yaml
    SampleBucket:
      Properties:
        AccessControl: Private
        PublicAccessBlockConfiguration:
          BlockPublicAcls: true
          BlockPublicPolicy: true
          IgnorePublicAcls: true
          RestrictPublicBuckets: true
        VersioningConfiguration:
          Status: Enabled
        BucketName: sample-bucket.${aws:region}.${ssm:/global/primary-domain}
        BucketEncryption:
          ServerSideEncryptionConfiguration:
          - BucketKeyEnabled: true
            ServerSideEncryptionByDefault:
              KMSMasterKeyID:
                Ref: ServiceEncryptionKey
              SSEAlgorithm: aws:kms
      Type: AWS::S3::Bucket
```

## Kinesis

`KinesisStream` wrapper provided by `serverless-builder` has as well built-in support for encryption feature detection.
All you need to do is to use it instead of default one.

```python
from serverless.aws.resources.kinesis import KinesisStream

stream = KinesisStream("sample-name")
service.resources.add(stream)
```

Generated Yaml syntax
```yaml
    SampleName:
      Properties:
        Name: ${self:service}-${sls:stage}-sample-name
        StreamEncryption:
          KeyId:
            Ref: ServiceEncryptionKey
          EncryptionType: KMS
      Type: AWS::Kinesis::Stream
```