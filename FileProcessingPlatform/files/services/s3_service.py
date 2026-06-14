import uuid

import boto3

from django.conf import settings


s3_client = boto3.client(
    "s3",
    # endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    # aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
    # aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    # region_name=settings.AWS_S3_REGION_NAME,

    endpoint_url= "http://localstack:4566",
    aws_access_key_id= "test",
    aws_secret_access_key= "test",
    region_name= "us-east-1",
)


def generate_presigned_upload_url(filename):

    unique_filename = f"{uuid.uuid4()}--{filename}"

    response = s3_client.generate_presigned_url(
        ClientMethod = "put_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": unique_filename
        },
        ExpiresIn=3600,
    )

    return {
        "upload_url":response,
        "filename": unique_filename
    }

