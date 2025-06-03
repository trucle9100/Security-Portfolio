import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Initialize SNS client
        sns = boto3.client('sns')
        
        # Extract compliance details (with error handling)
        detail = event.get('detail', {})
        resource_id = detail.get('resourceId', 'UNKNOWN_RESOURCE')
        
        # Get compliance result (handling both old and new event formats)
        evaluation_result = detail.get('newEvaluationResult', {}) or detail.get('evaluationResult', {})
        compliance_type = evaluation_result.get('complianceType', 'UNKNOWN_STATUS')
        
        # Construct alert message
        message = f"""
        [HIPAA Compliance Alert]
        Unencrypted EBS Volume Detected!
        Resource: {resource_id}
        Status: {compliance_type}
        Rule: {detail.get('configRuleName', 'UNKNOWN_RULE')}
        Account: {event.get('account', 'UNKNOWN_ACCOUNT')}
        Region: {event.get('region', 'UNKNOWN_REGION')}
        Event Time: {event.get('time', 'UNKNOWN_TIME')}
        Action Required: Encrypt or delete within 24 hours.
        """
        
        # Publish to SNS
        response = sns.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:hipaa-compliance-alerts',
            Message=message,
            Subject='HIPAA Compliance Violation Alert'
        )
        
        logger.info(f"Successfully sent alert for {resource_id}. SNS MessageId: {response['MessageId']}")
        return {
            'statusCode': 200,
            'body': 'Alert processed successfully'
        }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        logger.error(f"Full event: {event}")
        raise