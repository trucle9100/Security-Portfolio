import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Auto-remediation function for security violations
    """
    try:
        # Parse the incoming event
        detail = event.get('detail', {})
        config_item = detail.get('configurationItem', {})
        resource_type = config_item.get('resourceType')
        resource_id = config_item.get('resourceId')
        compliance_type = detail.get('newEvaluationResult', {}).get('complianceType')
        
        logger.info(f"Processing compliance event: {resource_type} - {resource_id} - {compliance_type}")
        
        if compliance_type == 'NON_COMPLIANT':
            if resource_type == 'AWS::EC2::SecurityGroup':
                remediate_security_group(resource_id)
            elif resource_type == 'AWS::S3::Bucket':
                remediate_s3_bucket(resource_id)
            elif resource_type == 'AWS::EC2::Instance':
                quarantine_ec2_instance(resource_id)
        
        # Send notification
        send_notification(event, resource_type, resource_id, compliance_type)
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Processed {resource_type} remediation')
        }
        
    except Exception as e:
        logger.error(f"Error in auto-remediation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def remediate_security_group(sg_id):
    """Remove overly permissive rules from security groups"""
    ec2 = boto3.client('ec2')
    
    try:
        response = ec2.describe_security_groups(GroupIds=[sg_id])
        sg = response['SecurityGroups'][0]
        
        # Remove rules that allow 0.0.0.0/0 access
        for rule in sg.get('IpPermissions', []):
            for ip_range in rule.get('IpRanges', []):
                if ip_range.get('CidrIp') == '0.0.0.0/0':
                    ec2.revoke_security_group_ingress(
                        GroupId=sg_id,
                        IpPermissions=[rule]
                    )
                    logger.info(f"Removed permissive rule from {sg_id}")
                    
    except Exception as e:
        logger.error(f"Failed to remediate security group {sg_id}: {str(e)}")

def remediate_s3_bucket(bucket_name):
    """Enable S3 bucket encryption and block public access"""
    s3 = boto3.client('s3')
    
    try:
        # Enable default encryption
        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
        )
        
        # Block public access
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        logger.info(f"Remediated S3 bucket {bucket_name}")
        
    except Exception as e:
        logger.error(f"Failed to remediate S3 bucket {bucket_name}: {str(e)}")

def quarantine_ec2_instance(instance_id):
    """Isolate suspicious EC2 instance"""
    ec2 = boto3.client('ec2')
    
    try:
        # Create quarantine security group
        response = ec2.create_security_group(
            GroupName=f'quarantine-{instance_id}',
            Description='Quarantine security group for suspicious instance'
        )
        quarantine_sg_id = response['GroupId']
        
        # Attach quarantine security group to instance
        ec2.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[quarantine_sg_id]
        )
        
        # Tag the instance
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[
                {'Key': 'SecurityStatus', 'Value': 'Quarantined'},
                {'Key': 'QuarantineDate', 'Value': str(datetime.now())}
            ]
        )
        
        logger.info(f"Quarantined EC2 instance {instance_id}")
        
    except Exception as e:
        logger.error(f"Failed to quarantine EC2 instance {instance_id}: {str(e)}")

def send_notification(event, resource_type, resource_id, compliance_type):
    """Send SNS notification about security event"""
    sns = boto3.client('sns')
    
    message = {
        'timestamp': str(datetime.now()),
        'event_type': 'Security Remediation',
        'resource_type': resource_type,
        'resource_id': resource_id,
        'compliance_status': compliance_type,
        'action_taken': 'Automated remediation applied',
        'raw_event': event
    }
    
    try:
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:ACCOUNT:security-alerts',
            Subject=f'Security Alert: {resource_type} Remediation',
            Message=json.dumps(message, indent=2)
        )
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
