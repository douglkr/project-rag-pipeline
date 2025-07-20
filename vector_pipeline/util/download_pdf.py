import logging
import os
import boto3

logger = logging.getLogger(__name__)

def download_pdf_from_s3(bucket: str, key: str) -> str:
    if not bucket or not key:
        logger.exception("Missing S3_BUCKET or S3_KEY environment variables")
        raise

    s3 = boto3.client('s3')

    filename = os.path.basename(key)
    local_path = f"/tmp/{filename}"

    try:
        logger.info(f"Downloading s3://{bucket}/{key} to {local_path}")
        s3.download_file(bucket, key, local_path)
        logger.info("Download complete.")
        return local_path

    except Exception as e:
        logger.exception(f"Error downloading file from S3: {e}")
        raise

