import boto3
from botocore.exceptions import ClientError

def download_from_localstack_s3(bucket_name, object_key, destination_path):
    # Initialize the S3 client targeting LocalStack
    s3_client = boto3.client(
        's3',
        endpoint_url='http://localstack:4566',
        aws_access_key_id='test',          # LocalStack accepts dummy credentials
        aws_secret_access_key='test',
        region_name='us-east-1'
    )
    
    try:
        # Download the file to your specified local directory
        s3_client.download_file(bucket_name, object_key, destination_path)
        print(f"Successfully downloaded {object_key} to {destination_path}")
    except ClientError as e:
        print(f"Error downloading file: {e}")
