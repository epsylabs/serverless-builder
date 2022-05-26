import json
from os import getcwd
from os.path import join, isfile

import boto3
import click
import yaml
from loguru import logger

from serverless.aws.features.encryption import Encryption


@click.group()
def cli():
    pass


@cli.group()
def kms():
    pass


def retrieve_key(service):
    kms_client = boto3.client("kms")
    response = kms_client.list_keys(Limit=1000)

    for cmk in response["Keys"]:
        try:
            tags = kms_client.list_resource_tags(KeyId=cmk["KeyArn"])
            if (next(filter(lambda x: x["TagKey"] == "SERVICE", tags["Tags"]), {})).get("TagValue") == service:
                metadata = kms_client.describe_key(KeyId=cmk["KeyId"]).get("KeyMetadata")
                if not all([metadata.get("Enabled"), metadata.get("KeyState") == "Enabled"]):
                    continue

                return cmk["KeyId"], cmk["KeyArn"]
        except Exception as e:
            print(e)

    return None, None


def replace_variables(variables, string):
    for word, initial in variables.items():
        string = string.replace(word, initial)

    return string


@kms.command(name="create")
@click.argument("service")
@click.option("-p", "--path", default=join(getcwd(), "serverless.yml"), type=click.Path(exists=True))
@click.option('-s', '--stage', required=True)
@click.option('-r', '--region', multiple=True)
def kms_create(service, region, stage, path):
    client = boto3.client('kms')

    variables = {
        "${aws:accountId}": boto3.client('sts').get_caller_identity().get('Account'),
        "${aws:region}": client.meta.region_name,
        "${self:service}": service,
        "${sls:stage}": stage
    }

    POLICY_TEMPLATE = Encryption.POLICY
    with open(path, "r") as f:
        definition = yaml.load(f, Loader=yaml.Loader)
        for fn in definition.get("functions").values():
            POLICY_TEMPLATE["Statement"].append({
                "Effect": "Allow",
                "Principal": {"Service": "logs.${aws:region}.amazonaws.com"},
                "Action": [
                    "kms:Encrypt*",
                    "kms:Decrypt*",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:Describe*",
                ],
                "Resource": "*",
                "Condition": {
                    "ArnLike": {
                        "kms:EncryptionContext:aws:logs:arn": "arn:aws:logs:${aws:region}:${aws:accountId}:log-group:/aws/lambda/"
                                                              + fn.get("name")
                    }
                },
            })

    POLICY_TEMPLATE = json.dumps(POLICY_TEMPLATE)

    defaults = dict(
        Description=f"Encryption Key for {service}",
        Tags=[
            {
                'TagKey': 'SERVICE',
                'TagValue': service
            },
        ],
    )

    logger.info(f"Creating multi-region KMS key for {service} in {region}")

    key_id, key_arn = retrieve_key(service)
    if not key_id:
        logger.info("Master key not found. Creating a new one.")
        response = client.create_key(
            Policy=replace_variables(variables, POLICY_TEMPLATE),
            MultiRegion=True,
            **defaults
        )

        key_id = response.get("KeyMetadata").get("KeyId")
        key_arn = response.get("KeyMetadata").get("Arn")
    else:
        logger.info("Update key policy")
        client.put_key_policy(
            KeyId=key_id,
            PolicyName="default",
            Policy=replace_variables(variables, POLICY_TEMPLATE)
        )

    logger.info(f"Using key: {key_id}")

    try:
        alias = f'alias/{service}-{stage}'
        client.create_alias(
            AliasName=alias,
            TargetKeyId=key_id,
        )
        logger.info(f"Created an alias: {alias}")
    except client.exceptions.AlreadyExistsException:
        logger.info(f"Using existing alias: {alias}")

    for target_region in [r for r in region if r != client.meta.region_name]:
        logger.info(f"Replicating key to: {target_region}")
        variables["${aws:region}"] = target_region

        target_session = boto3.client('kms', region_name=target_region)

        try:
            replica = target_session.describe_key(KeyId=key_id).get("KeyMetadata")
            logger.info(f"Key replica {key_id} exists in {target_region}")
        except target_session.exceptions.NotFoundException as e:
            replica = client.replicate_key(
                Policy=replace_variables(variables, POLICY_TEMPLATE),
                KeyId=key_id,
                ReplicaRegion=target_region,
                **defaults
            ).get("ReplicaKeyMetadata")
            logger.info(f"Replicate key created in {target_region}")

        logger.info(f"Update key policy in {target_region}")
        target_session.put_key_policy(
            KeyId=key_id,
            PolicyName="default",
            Policy=replace_variables(variables, POLICY_TEMPLATE)
        )

        try:
            target_session.create_alias(
                AliasName=f'alias/{service}-{stage}',
                TargetKeyId=replica.get("KeyId"),
            )
            logger.info(f"Created key alias in {target_region}")
        except client.exceptions.AlreadyExistsException:
            logger.info(f"Using existing alias of key in {target_region}")
