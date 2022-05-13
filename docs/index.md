# Start here

<h2 align="center">serverless-builder</h2>
<p align="center">
<a href="https://pypi.org/project/serverless-builder/"><img alt="PyPI" src="https://img.shields.io/pypi/v/serverless-builder"></a>
<a href="https://pypi.org/project/serverless-builder/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/serverless-builder.svg"></a>
<a href="https://github.com/epsylabs/serverless-builder/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/serverless-builder.svg"></a>
</p>

serverless-builder is Python (3.8+) interface to easily generate [serverless.yml](https://www.serverless.com/) file.

## Install
To use stable version use latest version from `pypi`:

```shell
$ pip install serverless-builder
```

## How?

With a language you know (python) you can quickly generate `serverless.yml` file, share plugins between projects, follow best practices.

```python
from serverless import Service
from serverless.aws.features import XRay
from serverless.provider import AWSProvider
from serverless.service.plugins.composed_vars import ComposedVars
from serverless.service.plugins.prune import Prune
from serverless.service.plugins.python_requirements import PythonRequirements

service = Service(
    "service-name",
    "some dummy service",
    AWSProvider()
)
service.plugins.add(ComposedVars())
service.plugins.add(Prune())
service.plugins.add(PythonRequirements())

service.enable(XRay())

service.builder.function.generic("test", "description")

service.render()
```

Those few lines of code equals to almost 100 lines in YAML.

`serverless-builder` comes with:

* plugin management with autoconfiguration
* function factory (with some best practice hints)
* autoconfiguration of some provider specific features like AWS X-Ray
* easy resource manipulation with [troposphere lib](https://github.com/cloudtools/troposphere) (but if you want you can use old good dict)
* easier IAM management with predefined permission sets
* built-in support for any serverless attributes


We tested it on Python 3.8+, but it should work on lower versions up to 3.6.

## Why?
It came to life when we started getting lost in massive (and complex) CloudFormation configuration and had to duplicate
YAML modules between our micro services.

When we're starting new micro service we have some preferences in terms of how we want to handle SQS with DLQ, list of plugins we want to use,
the way we store params between environments or simple as default tags for our services.

Now, imagine that you have this perfect setup in one of your projects, but you need to multiply it by 2, 10, 20, 40... micro services.

So you prepared your YAML modules or some batch scripts. Not super handy nor easily to maintain.

Then you realised that your "perfect setup" has a bug. So you have to go through 40 micro services and change CloudFormation in all of them.

Wouldn't it be nice to have it done programmatically in language you like, that is easy to extend, or even executed automatically by your CI/CD process?

That's where `serverless-builder` becomes handy!

## Thank you!
Massive thanks goes to [@dxd1](https://github.com/dxd1>) for his original idea and implementation.
