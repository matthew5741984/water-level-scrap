import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def get_aws_access_key():
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    return aws_access_key_id


def get_aws_secret_access_key():
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    return aws_secret_access_key


def get_region():
    region = os.getenv("AWS_DEFAULT_REGION")
    return region
