# Plugins
To activate plugin you just need to add it, with `service.plugins.add` function.
E.g.
```python
from serverless.plugins import ComposedVars

service.plugins.add(ComposedVars())
```

Majority of plugins is customisable, and during initialization allows you to pass config to itself.

## serverless-aws-signer
## serverless-plugin-composed-vars
## serverless-deployment-bucket
## serverless-domain-manager
## serverless-iam-roles-per-function
## serverless-kms-grants
## serverless-localstack
## serverless-prune-plugin
## serverless-python-requirements
## serverless-scriptable-plugin
## serverless-secrets-mgr-plugin
## serverless-step-functions
## serverless-vpc-discovery
