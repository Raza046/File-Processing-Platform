import math
import uuid

import boto3
from botocore.exceptions import ClientError

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


def download_from_localstack_s3(bucket_name, object_key, start, end):
    # Initialize the S3 client targeting LocalStack    
    try:
        print("--------DOWNLOADING FILE----------")
        # Download the file to your specified local directory
        downloaded_chunk = s3_client.download_file(bucket_name, object_key, Range=f"bytes={start}--{end}")
        print(f"Successfully downloaded {object_key} with range : bytes= {start}--{end} ")
        response = {
            "object Key":object_key,
            "data":downloaded_chunk,
            "chunk_range": f"bytes={start}--{end}"
        }
        print(response)
        print("--------DOWNLOADED FILE----------")
        return response

    except ClientError as e:
        print(f"Error downloading file: {e}")


def create_multipart_upload(file_name, file_size):

    key = file_name
    response = s3_client.create_multipart_upload(
        Bucket="my-bucket",
        Key=key
    )
    file_size_in_MBs = file_size / (1024 * 1024) # into MBs
    part_size = math.ceil(file_size_in_MBs / 50) # each part 50MB


    print("=============MULTIPART-UPLOAD===============")
    print(response)
    print("=============MULTIPART-UPLOAD===============")
    return {
        "upload_id": response.get("UploadId"),
        "key":key,
        "total_size":file_size,
        "part_size":part_size
        }


def generate_presigned_upload_url(key, upload_id, part_number):

#    unique_filename = f"{uuid.uuid4()}--{filename}"

    response = s3_client.generate_presigned_url(
        ClientMethod = "upload_part",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": key,
            "UploadId":upload_id,
            "PartNumber":part_number
        },
        ExpiresIn=3600,
    )

    return response


def complete_multipart_upload(key, upload_id, s3_parts):

    multipart_parts = [
        {
            "PartNumber": part["part_number"],
            "ETag": part["etag"],
        }
        for part in s3_parts
    ]

    response = s3_client.complete_multipart_upload(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        MultipartUpload={
            'Parts': multipart_parts
        },
        UploadId=upload_id,
    )

    print("=============COMPLETE MULTIPART-UPLOAD===============")
    print(response)
    print("=============COMPLETE MULTIPART-UPLOAD===============")
    return response


def abort_multipart_upload(key, upload_id):

    response = s3_client.abort_multipart_upload(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        UploadId=upload_id
    )
    print("=============ABORT MULTIPART-UPLOAD===============")
    print(response)
    print("=============ABORT MULTIPART-UPLOAD===============")
    return response


def list_parts_uploaded(key, upload_id):

    response = s3_client.list_parts(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        UploadId=upload_id
    )
    print("=============LIST PARTS-UPLOADED===============")
    print(response)
    print("=============LIST PARTS-UPLOADED===============")
    return response
