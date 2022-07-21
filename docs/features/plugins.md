# Plugins

`serverless-builder` has a native support for most common serverless plugins with predefined setup. 

To activate plugin you just need to add it, with `service.plugins.add` function.

E.g.
```python
from serverless.plugins import ComposedVars

service.plugins.add(ComposedVars())
```

Majority of plugins is customisable, and during initialization allows you to pass config to itself.

## Supported plugins

### serverless-aws-signer

Documentation: https://www.npmjs.com/package/serverless-aws-signer

#### Default configuration

* `sign_policy` - "Enforce"
* `source_bucket` and `destination_bucket` - configured to use `deploymentBucket` 
* `destination_prefix` - `signed-`

#### Minimal setup

```python
from serverless.service.plugins.code_sign import AWSCodeSign

self.plugins.add(
    AWSCodeSign(
        "${ssm:/global/lambda-signing-profile}",
    )
)
```

## serverless-deployment-bucket

Documentation: https://www.npmjs.com/package/serverless-deployment-bucket

#### Default configuration

* `bucket_name` - name or "${self:provider.deploymentBucket.name}"

#### Minimal setup

```python
from serverless.service.plugins.deployment_bucket import DeploymentBucket

self.plugins.add(DeploymentBucket())
```

## serverless-domain-manager

Documentation: https://www.serverless.com/plugins/serverless-domain-manager

#### Default configuration

* `domain` - FQDN used as a base for API gateway
* `api` - Name of the API

#### Minimal setup

```python
from serverless.service.plugins.domain_manager import DomainManager

self.plugins.add(DomainManager(domain="example.com"))
```

## serverless-iam-roles-per-function
## serverless-prune-plugin
## serverless-python-requirements
## serverless-scriptable-plugin
## serverless-secrets-mgr-plugin
## serverless-step-functions
## serverless-vpc-discovery
