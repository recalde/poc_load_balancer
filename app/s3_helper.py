import boto3

def get_file_size(bucket_name, file_key):
    """
    Fetches the file size from the S3 bucket based on the input file key.
    """
    s3 = boto3.client('s3')
    response = s3.head_object(Bucket=bucket_name, Key=file_key)
    return response['ContentLength']
