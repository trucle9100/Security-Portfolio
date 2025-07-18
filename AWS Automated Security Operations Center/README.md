# AWS Automated Security Operations Center (SOC)

##### *Automated Security Incident Response with Config Compliance Monitoring & GuardDuty Threat Detection*

---

**Skills Demonstrated:** `Security Automation` `Compliance Monitoring` `Incident Response` `Cloud Governance` `Risk Assessment` `Python Development` `Event-Driven Architecture`

## Executive Summary

**Business Challenge**: Manual security monitoring costs enterprises $300K+ annually in 24/7 SOC staffing while missing critical security threats due to human limitations and alert fatigue.

**Solution Impact**: Architected and deployed an automated Security Operations Center using AWS Config, GuardDuty, Lambda, and EventBridge to achieve real-time threat detection, automated incident response, and continuous compliance monitoring - demonstrating potential to prevent millions in security breach costs.

**Key Achievements**:
- **Automated threat detection and response** using cloud-native security services
- **Sub-5-minute incident response time** through event-driven automation
- **$300K+ potential annual savings** in SOC operational costs

---

## Architecture Overview

![Architecture Diagram](images/AutomatedSecurityOperation.png)

**High-Level System Design:**
* **AWS Config** continuously monitors resource configurations against security compliance rules
* **Amazon GuardDuty** provides threat detection for AWS environment protection
* **EventBridge** orchestrates real-time security event routing to automated response systems
* **Lambda Functions** execute automated remediation for security violations and compliance issues
* **CloudWatch** delivers centralized monitoring dashboards and security metrics visibility
* **SNS** enables multi-channel stakeholder notifications for incident escalation
* **Step Functions** manage incident response workflows for complex security events

**AWS Security Automation Pipeline:**
```
├── AWS Config (Compliance Detection): Continuous monitoring
│   ├── s3-bucket-public-read-prohibited
│   ├── restricted-ssh
│   └── root-access-key-check
├── GuardDuty (Threat Detection): Security monitoring
│   └── High-severity findings (severity > 7.0)
├── EventBridge (Orchestration): Event-driven automation
│   ├── Config Rules Compliance Change
│   └── GuardDuty Finding Events
├── Lambda (Auto-Remediation): Python-based security response
│   ├── S3 Public Access Block
│   ├── S3 Default Encryption
│   ├── Security Group SSH Restriction
│   └── EC2 Instance Quarantine
└── CloudWatch (Monitoring): Real-time security dashboards
    ├── Compliance Rate Metrics
    ├── GuardDuty Findings Trends
    └── Remediation Success Rate
```

---

## Technical Scripts

### 1. Security Auto-Remediation Lambda Function
<details>
<summary><strong>Python Lambda Handler for Automated Security Response</strong></summary>

```python
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
```
</details>

### 2. Security Group Remediation
<details>
<summary><strong>Remove Overly Permissive Security Group Rules</strong></summary>

```python
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
```
</details>

### 3. S3 Bucket Security Remediation
<details>
<summary><strong>Enable Encryption and Block Public Access</strong></summary>

```python
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
```
</details>

### 4. EC2 Instance Quarantine
<details>
<summary><strong>Isolate Suspicious EC2 Instances</strong></summary>

```python
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
```
</details>

### 5. EventBridge Rule Configuration
<details>
<summary><strong>Config Compliance Event Pattern</strong></summary>

```json
{
  "source": ["aws.config"],
  "detail-type": ["Config Rules Compliance Change"],
  "detail": {
    "newEvaluationResult": {
      "complianceType": ["NON_COMPLIANT"]
    }
  }
}
```
</details>

### 6. Step Functions Workflow Definition
<details>
<summary><strong>Simplified Security Incident Response</strong></summary>

```json
{
  "Comment": "Simplified security incident response workflow",
  "StartAt": "AssessIncident",
  "States": {
    "AssessIncident": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "SecurityAutoRemediation",
        "Payload.$": "$"
      },
      "Next": "LogIncident"
    },
    "LogIncident": {
      "Type": "Pass",
      "Result": "Incident logged successfully",
      "End": true
    }
  }
}
```
</details>

---

## Implementation Evidence

**Security Automation in Action**

| Component | Screenshot |
|-----------|------------|
| Security Operations Dashboard | ![Dashboard](images/CloudWatchPhase5.jpg) |
| Config Rules Compliance | ![Compliance](images/ConfigStatusBefore.jpg) |
| Lambda Remediation Logs | ![CloudWatch Logs](images/CloudwatchLog.jpg) |
| EventBridge Automation | ![EventBridge Rules](images/EventBridgeRules.jpg) |
| Step Functions Workflow | ![Step Functions](images/StepFunctions.jpg) |

---

## Business Value Delivered

### Risk Mitigation and Compliance Assurance
- **Continuous Compliance**: Enabled 24/7 automated compliance monitoring
- **Automated Incident Response**: Reduced security incident impact through rapid remediation
- **Audit Readiness**: Established automated compliance tracking for audit requirements

### Operational Cost Optimization
- **L1/L2 Support Automation**: $300K potential annual savings in security staffing costs
- **Reduced Alert Fatigue**: Automated filtering and prioritization of security events
- **Scalable Security**: Zero marginal cost for monitoring additional resources

### Enterprise Security Posture
- **Real-time Threat Detection**: Sub-5-minute response to security violations
- **Proactive Risk Management**: Continuous security assessment capabilities
- **Cloud Governance**: Automated enforcement of security best practices

---

## Technical Implementation

### AWS Config Rules Deployment
- **s3-bucket-public-read-prohibited**: Prevents unauthorized public access to S3 buckets
- **restricted-ssh**: Ensures SSH access is limited to specific IP ranges
- **root-access-key-check**: Monitors root account access key usage

### GuardDuty Integration
- Enabled threat detection for the AWS environment
- Configured to detect high-severity findings (severity > 7.0)
- Integrated with EventBridge for automated response triggering

### EventBridge Automation
- **ConfigComplianceRule**: Triggers on Config non-compliance events
- **GuardDutyFindingsRule**: Responds to high-severity security findings
- Routes events to Lambda for automated remediation

### Lambda Security Functions
- **SecurityAutoRemediation**: Main handler for security event processing
- Implements remediation for S3, EC2, and Security Group violations
- Provides logging and notification for all security actions

---

## Infrastructure Monitoring Code Sample

<details>
<summary><strong>CloudWatch Security Dashboard Creation</strong></summary>

```python
# CloudWatch Dashboard widgets for security monitoring
dashboard_widgets = [
    {
        "type": "number",
        "properties": {
            "metrics": [
                ["AWS/Config", "ComplianceByConfigRule", {"stat": "Average"}]
            ],
            "period": 300,
            "stat": "Average",
            "region": "us-east-1",
            "title": "Config Compliance Rate"
        }
    },
    {
        "type": "line",
        "properties": {
            "metrics": [
                ["AWS/GuardDuty", "FindingCount", {"stat": "Sum"}]
            ],
            "period": 300,
            "stat": "Sum",
            "region": "us-east-1",
            "title": "GuardDuty Findings Over Time"
        }
    },
    {
        "type": "number",
        "properties": {
            "metrics": [
                ["AWS/Lambda", "Invocations", {"FunctionName": "SecurityAutoRemediation"}],
                [".", "Errors", {"FunctionName": "SecurityAutoRemediation"}]
            ],
            "period": 300,
            "stat": "Sum",
            "region": "us-east-1",
            "title": "Remediation Success Rate"
        }
    }
]
```
</details>

---

## Performance Metrics

| Metric | Manual Process | Automated SOC | Improvement |
|--------|----------------|---------------|-------------|
| **Incident Response Time** | 4+ hours | <5 minutes | 95% faster |
| **Compliance Monitoring** | Weekly audits | Continuous 24/7 | Real-time visibility |
| **Security Coverage** | Business hours | 24/7 automated | 100% availability |
| **Operational Cost** | $25K/month | $3K/month | 88% reduction |

### Security Automation KPIs
- **Event Processing**: Automated handling of Config and GuardDuty events
- **Remediation Success**: Lambda functions successfully remediate violations
- **Notification Delivery**: SNS alerts sent for all security incidents
- **Compliance Status**: Real-time tracking via Config rules

---

## Key Challenges & Solutions

### IAM Permission Configuration
**Challenge:** Lambda execution failed due to insufficient permissions for cross-service operations.

<details>
<summary><strong>Solution</strong></summary>

- Created SecurityRemediationRole with specific service permissions
- Added policies for EC2, S3, Config, and CloudWatch access
- Implemented least-privilege principle for security best practices
- Tested permissions before production deployment
</details>

### EventBridge Rule Filtering
**Challenge:** Initial event patterns captured too many events, causing unnecessary Lambda invocations.

<details>
<summary><strong>Solution</strong></summary>

- Refined event patterns to filter only NON_COMPLIANT status
- Added severity thresholds for GuardDuty findings
- Tested patterns with sample events before deployment
- Monitored CloudWatch metrics for optimization
</details>

### Test Resource Cleanup
**Challenge:** Test resources created for validation needed careful tracking for complete cleanup.

<details>
<summary><strong>Solution</strong></summary>

- Documented all test resources with clear naming conventions
- Created comprehensive cleanup checklist
- Verified zero ongoing costs after lab completion
- Used Cost Explorer to confirm resource deletion
</details>

---

## Lessons Learned

**Automation Reduces Human Error**: Manual security responses are inconsistent and slow. Automated Lambda remediation ensures uniform, rapid responses to security violations across the entire infrastructure.

**Event-Driven Architecture Scales**: Using EventBridge for security orchestration allows the system to handle security events efficiently without manual intervention.

**Testing is Critical**: Always test automation by intentionally creating security violations. This lab taught the importance of validating both detection and remediation before production deployment.

**AWS Services Integration**: Learned how AWS Config, GuardDuty, EventBridge, and Lambda work together to create a complete security automation pipeline.

---

## Future Enhancements

- **Advanced Threat Intelligence**: Integrate additional threat feeds for enhanced detection
- **SIEM Integration**: Connect with enterprise security information and event management platforms
- **Machine Learning**: Add anomaly detection for behavioral analysis
- **Multi-Account Security**: Extend to AWS Organizations for enterprise-scale security
- **Automated Forensics**: Implement evidence collection for security investigations

---

## Lab Environment Disclaimer

This project represents a hands-on AWS security automation laboratory exercise designed to demonstrate automated incident response and compliance monitoring techniques. Key clarifications:

- **Metrics**: The "before" and "after" business impact metrics represent potential improvements based on industry security automation practices and common SOC challenges
- **Environment**: Single-account AWS learning environment demonstrating patterns applicable to enterprise security operations centers
- **Scope**: AWS Config compliance monitoring with GuardDuty threat detection, showcasing automated remediation techniques used in production security systems
- **Business Impact**: Cost savings and efficiency gains represent demonstrated capabilities of automated security operations
- **Security Coverage**: Current implementation covers foundational security controls; enterprise deployments would include additional threat intelligence and SIEM integration

The technical implementation follows AWS security best practices and demonstrates real-world SOC automation patterns suitable for enterprise environments.

---

*This implementation demonstrates enterprise AWS security automation using event-driven incident response patterns. All resources configured following AWS Well-Architected security pillar guidelines with automated compliance monitoring and threat remediation best practices.*
