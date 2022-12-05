import boto3
import logging
from botocore.exceptions import ClientError
import config

S3_ACCESS_KEY = config.S3_ACCESS_KEY
S3_SECRET_KEY = config.S3_SECRET_KEY
S3_ENDPOINT_URL = config.S3_ENDPOINT_URL

def upload_to_s3_bucket(local_file, bucket_name, s3_file):

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    try:
        s3_resource = boto3.resource(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY
        )

    except Exception as exc:
        logging.error(exc)
    else:
        try:
            bucket = s3_resource.Bucket(bucket_name)

            with open(local_file, "rb") as file:
                bucket.put_object(
                    ACL='private',
                    Body=file,
                    Key=s3_file
                )
        except ClientError as e:
            logging.error(e)


def download_from_s3_bucket(ad_id, bucket_name):

    logging.basicConfig(level=logging.INFO)

    try:
        s3_resource = boto3.resource(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY
        )
    except Exception as exc:
        logging.error(exc)
    else:
        try:
            bucket = s3_resource.Bucket(bucket_name)

            object_name = '' + str(ad_id) + '.png'
            download_path = f"static/downloads/{object_name}"

            bucket.download_file(
                object_name,
                download_path
            )
        except ClientError as e:
            logging.error(e)
            