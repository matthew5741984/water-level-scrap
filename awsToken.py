import boto3
from settings import get_aws_access_key
from settings import get_aws_secret_access_key
from settings import get_region


def aws_session_token():
    mysession = boto3.Session(
        aws_access_key_id=get_aws_access_key(),
        aws_secret_access_key=get_aws_secret_access_key(),
        region_name=get_region(),
    )
    return mysession
