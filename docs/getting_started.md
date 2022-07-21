# Getting started

## 1. Install
To use stable version use latest version from `pypi`:

```shell
$ pip install serverless-builder
```

## 2. Create `serverless.yml.py`
```python 
from serverless import Service
from serverless.provider import AWSProvider

service = Service(
    "service-name",
    "Description of my service",
    AWSProvider()
)

service.render()
```

## 3. Generate serverless.yml

```shell
$ python serverless.yml.py
```

Lambda functions
`serverless-builder` allows you easily define different types of lambdas. In many cases it also takes care, by default, for setting up Dead Letter Queue (DLQ) or its asynchronous equivalent, Retry Policy or idempotency.

`serverless-builder` will take care of creating any required resources as well as IAM permissions. 
