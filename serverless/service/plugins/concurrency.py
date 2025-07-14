from serverless.service.plugins.generic import Generic


class ProvisionedConcurrencyAutoscaling(Generic):
    yaml_tag = "!WarmUpPlugin"

    def __init__(
        self,
    ):
        super().__init__("serverless-provisioned-concurrency-autoscaling")

    def enable(self, service):
        pass


def autoscaling(
    enabled=True,
    alias="provisioned",
    provisioned=1,
    global_min=0,
    global_max=2,
    office_min=2,
    office_max=5,
    afterhours_min=0,
    afterhours_max=0,
):
    return dict(
        provisionedConcurrency=provisioned,
        concurrencyAutoscaling=dict(
            enabled=enabled,
            alias=alias,
            maximum=global_max,
            minimum=global_min,
            usage=0.75,
            scaleInCooldown=0,
            scaleOutCooldown=0,
            customMetric=dict(statistic="maximum"),
            scheduledActions=[
                dict(
                    name="ScaleUpWorkingHours",
                    timezone="America/Chicago",
                    schedule="cron(0 7 ? * * *)",
                    action=dict(minimum=office_min, maximum=office_max),
                ),
                dict(
                    name="ScaleDownWorkingHours",
                    timezone="America/Chicago",
                    schedule="cron(0 18 ? * * *)",
                    action=dict(minimum=afterhours_min, maximum=afterhours_max),
                ),
            ],
        ),
    )

def autoscaling_enabled():
    return autoscaling(
        provisioned="${self:custom.vars.provisioning.concurrency}",
        enabled="${self:custom.vars.provisioning.autoscaling}"
    )
