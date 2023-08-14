import boto3
from botocore.exceptions import ClientError
from configs.env import AWS_S3_BUCKET_NAME, AWS_S3_REGION_NAME
import io
import mimetypes
import os


class S3Upload:
    def __init__(self, dt_string: str, path: str) -> None:
        self.s3_client = boto3.client(
            "s3",
            region_name=AWS_S3_REGION_NAME,
        )
        self.key = dt_string

        self.dt_string = dt_string

        self.file_name = path.rsplit("/", 1)[-1]

        self.file_to_write_in = path

    def get_url(self) -> str:
        file = open(self.file_to_write_in, "rb").read()
        file = io.BytesIO(file)
        bucket_name = AWS_S3_BUCKET_NAME
        self.dt_string = self.dt_string + self.file_name

        try:
            file_content_type = mimetypes.guess_type(self.file_name)[0]
            conf = boto3.s3.transfer.TransferConfig(
                multipart_threshold=10000, max_concurrency=4
            )
            self.s3_client.upload_fileobj(
                file,
                bucket_name,
                self.key,
                Config=conf,
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": file_content_type,
                    "ContentDisposition": "inline",
                },
            )
        except ClientError as e:
            return None
        file_url = "https://{}.s3.ap-south-1.amazonaws.com/{}.json".format(
            bucket_name, self.key
        )
        os.remove(self.file_to_write_in)
        return file_url
