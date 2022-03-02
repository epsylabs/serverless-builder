from typing import Dict, Optional

from serverless.service.plugins.generic import Generic


class InvalidInputException(Exception):
    pass


class DeploymentBucket(Generic):
    """
    Plugin homepage: https://www.npmjs.com/package/serverless-deployment-bucket
    Example of use
    ```python
    service.plugins.add(DeploymentBucket())
    ```
    """

    yaml_tag = "!DeploymentBucketPlugin"

    def __init__(
        self,
        name: Optional[str] = None,
        serverSideEncryption: Optional[str] = None,
        kmsKeyID: Optional[str] = None,
        versioning: Optional[bool] = None,
        accelerate: Optional[bool] = None,
        blockPublicAccess: Optional[bool] = None,
        tags: Optional[Dict] = None,
    ):
        super().__init__("serverless-deployment-bucket")

        self.bucket_name = name or "${self:provider.deploymentBucket.name}"

        if serverSideEncryption:
            self.serverSideEncryption = serverSideEncryption

        if kmsKeyID:
            if serverSideEncryption == "aws:kms":
                self.kmsKeyID = kmsKeyID
            else:
                raise InvalidInputException("kmsKeyID can only be set if serverSideEncryption is 'aws:kms'")

        if versioning:
            self.versioning = versioning

        if accelerate:
            self.accelerate = accelerate

        if blockPublicAccess:
            self.blockPublicAccess = blockPublicAccess

        if tags:
            self.tags = list(map(lambda key, value: {"Key": key, "Value": value}, tags.items()))

    def enable(self, service):
        export = dict(self)
        export.pop("name", None)

        export["name"] = export["bucket_name"]
        export.pop("bucket_name")

        service.custom.deploymentBucket = dict(self)
