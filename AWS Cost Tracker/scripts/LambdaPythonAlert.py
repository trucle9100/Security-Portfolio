import json
import boto3

def lambda_handler(event, context):
    sns = boto3.client('sns')
    alert = f"""
    🚨 AWS BUDGET ALERT 🚨
    {json.dumps(event, indent=2)}
    """
    sns.publish(
        TopicArn='arn:aws:sns:us-east-1:726648044823:budget-alert-topic',
        Message=alert,
        Subject='AWS Budget Alert!'
    )
    return {'statusCode': 200}