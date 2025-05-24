import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # 1. Log the full event for debugging
        logger.info(f"Received event: {event}")
        
        # 2. Extract bucket name with multiple fallback options
        bucket = None
        
        # Option 1: Standard EventBridge format
        if 'detail' in event and 'resourceId' in event['detail']:
            bucket = event['detail']['resourceId']
        # Option 2: Direct S3 event format
        elif 'Records' in event and len(event['Records']) > 0:
            bucket = event['Records'][0]['s3']['bucket']['name']
        # Option 3: Manual test format
        elif 'bucket' in event:
            bucket = event['bucket']
        
        if not bucket:
            error_msg = "Could not find bucket name in event. Expected formats:\n" \
                       "1. {'detail': {'resourceId': 'bucket-name'}}\n" \
                       "2. {'Records': [{'s3': {'bucket': {'name': 'bucket-name'}}]}\n" \
                       "3. {'bucket': 'bucket-name'}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Processing bucket: {bucket}")
        
        # 3. Remediation logic
        s3 = boto3.client('s3')
        
        # Enable public access block
        s3.put_public_access_block(
            Bucket=bucket,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        
        # Enable default encryption
        s3.put_bucket_encryption(
            Bucket=bucket,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
        )
        
        return {
            "status": "success",
            "bucket": bucket,
            "actions": ["enabled_public_access_block", "enabled_encryption"]
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "event_received": event  # This helps debugging
        }