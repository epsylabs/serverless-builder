<h2 align="center">serverless-builder</h2>
<p align="center">
<a href="https://pypi.org/project/serverless-builder/"><img alt="PyPI" src="https://img.shields.io/pypi/v/serverless-builder"></a>
<a href="https://pypi.org/project/serverless-builder/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/serverless-builder.svg"></a>
<a href="https://github.com/epsylabs/serverless-builder/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/serverless-builder.svg"></a>
</p>

serverless-builder is Python (3.8+) interface to easily generate [serverless.yml](https://www.serverless.com/) file.

## Features

* full support for all features provided by serverless framework and CloudFormation
* autoconfiguration for provider specific features (eg. AWS X-Ray, Death Letter Queues, Encryption etc.)
* function factory for common serverless functions (http, even-bridge, SQS, kinesis)
* security by default - including encryption, backups and DLQ
* easier IAM management with predefined permission sets
* support for multi-region deployments
* integrations with AWS Power Tools, Sentry
* naming strategy enforced across all resources
* support for multi-stack and shared resources
* automatic alerting 
* support for step functions via (serverless-step-functions)

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

## Credits
Massive thanks goes to [@dxd1](https://github.com/dxd1) for his original idea and implementation.

`serverless-builder` is actively developed at [Epsy](https://github.com/epsyhealth) - would you like to change a world with us? 
Check our open positions at: https://epsyhealth.com/careers
