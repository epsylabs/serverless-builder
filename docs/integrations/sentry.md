# Sentry

## Enable it
```python
from serverless.integration.sentry import Sentry

service.enable(Sentry("https://xxxx-yyyy-zzzzz-wwwww.ingest.sentry.io/123456789"))
```

### Automatically sets ENV variables
It will automatically set `SENTRY_DSN`, `SENTRY_ENVIRONMENT` and `SENTRY_RELEASE`.

???+ info "You need to provide value for `VERSION` environment variable during the deployment to use release features of sentry."
