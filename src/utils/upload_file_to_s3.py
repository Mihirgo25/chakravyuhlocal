import boto3
from botocore.exceptions import ClientError
from configs.env import *
from datetime import datetime
import io
import mimetypes
import sharepy
import os
from libs.logger import logger


def upload_file_to_s3(url):
    file_name = url.rsplit("/", 1)[-1]

    file_to_write_in = url
    file = open(file_to_write_in, "rb").read()
    s3_client = boto3.client(
        "s3",
        region_name=AWS_S3_REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    file = io.BytesIO(file)
    bucket_name = AWS_S3_BUCKET_NAME
    now = datetime.utcnow()
    dt_string = now.strftime("%Y_%m_%d_%H_%M_%S_%f")
    key = dt_string
    try:
        file_content_type = mimetypes.guess_type(file_name)[0]
        conf = boto3.s3.transfer.TransferConfig(
            multipart_threshold=10000, max_concurrency=4
        )
        s3_client.upload_fileobj(
            file,
            bucket_name,
            key,
            Config=conf,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file_content_type,
                "ContentDisposition": "inline",
            },
        )
    except ClientError as e:
        logger.error(e,exc_info=True)
        return None
    file_url = "https://{}.s3.ap-south-1.amazonaws.com/{}".format(bucket_name, key)
    print(file_url)
    os.remove(file_to_write_in)
    return file_url
