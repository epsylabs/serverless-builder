from troposphere.s3 import Bucket, Private
from serverless.aws.resources import Resource
from serverless.service import Identifier


class S3Bucket(Resource):
    def __init__(self, BucketName, **kwargs):
        self.bucket = Bucket(
            title=Identifier(BucketName, safe=True).pascal,
            BucketName=Identifier(BucketName, safe=True).pascal,
            **kwargs
        )

        if "${self:service}" not in BucketName:
            self.bucket.properties.__setitem__("BucketName", "${self:service}-${sls:stage}-${aws:region}" + BucketName)

    def resources(self):
        return super().resources() + [self.bucket]
