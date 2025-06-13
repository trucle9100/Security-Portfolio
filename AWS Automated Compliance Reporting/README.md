# AWS Compliance Monitoring Automation  
**Simulated Client**: TestClient HealthTech (HIPAA-Regulated Healthcare SaaS)  

---

## Mock Client Profile  
**Client**: TestClient HealthTech  

**Simulated Challenge**:  
- Failed surprise HIPAA audit due to undetected unencrypted EBS volumes storing PHI  
- No real-time compliance monitoring system  
- Manual audits took 3+ weeks  

**Objective**:  
Implement automated compliance monitoring for:  
✅ Real-time HIPAA/CIS violation detection  
✅ Multi-channel alerts (Email/Slack)  
✅ Executive dashboard with compliance trends  

---
## Test Environment Setup  
- Created intentionally non-compliant resources:  
  - Unencrypted EBS volumes (`testclient-phi-storage`)  
  - Disabled Config logging  
- Used AWS CLI + Console for scenario realism  

---
## Architecture  
![Compliance Monitoring Flow](images/Monitoring_Automation.png)  

---
## Key Achievements  

| Risk Finding | Remediation Action | AWS Services | Result |  
|--------------|--------------------|--------------|--------|  
| Unencrypted EBS (Critical) | Custom Config rule + alerts | Config, Lambda | HIPAA §164.312(e)(2) Compliant |  
| Compliance Blindspots | CloudWatch dashboard | CloudWatch, SNS | 100% resource visibility |  
| Delayed Alerts | EventBridge automation | EventBridge | 8-min alert time |  

---
## Compliance Monitoring & Mapping  
| AWS Service | Security Control | Compliance Standard |  
|-------------|------------------|---------------------|  
| Config | Continuous Monitoring | HIPAA §164.312(b), NIST SI-4 |  
| CloudWatch | Audit Logging | HIPAA §164.312(c) |  
| SNS | Incident Response | NIST IR-4 |  

---
## Security Posture Improvement  

**Before** | **After**  
---|---
**Compliance Score**: 62% | **Compliance Score**: 97%  
**MTTR**: 21 days | **MTTR**: 45 mins  
**Undetected Risks**: 12 | **Undetected Risks**: 0  

---
## Results  
| Scenario | Image |  
|----------|-------|  
| Non-Compliant EBS Volume | ![Config Finding](images/Noncompliant_Resources.png) |  
| CloudWatch Dashboard | ![Dashboard](images/CloudWatch_Dashboard.png) |  
| Lambda Test Alert | ![Alert](images/LambdaFunctionTest.png) |  
| Working SNS Email | ![Rule](images/Lambda_EventBridge_Trigger.png) |
| Config Rule Detail | ![Rule](images/ConfigRuleDetail.png) |

---
## Lessons Learned  
1. **Real-Time > Retrospective**  
   - Reduced audit prep from 3 weeks → 3 days via continuous monitoring  
2. **Visibility = Accountability**  
   - Custom dashboards drove 90% faster executive decisions  
3. **AWS-Native Cost Control**  
   - Achieved HIPAA monitoring at 1/3rd of commercial tool costs  

---
## Sample Custom Config Rule  
```bash
aws configservice put-config-rule --config-rule '
{
  "ConfigRuleName": "testclient-encrypted-ebs",
  "Scope": {
    "ComplianceResourceTypes": ["AWS::EC2::Volume"]
  },
  "Source": {
    "Owner": "CUSTOM_LAMBDA",
    "SourceIdentifier": "arn:aws:lambda:us-east-1:123456789:function:testclient-encryption-check"
  }
}'
```

---
*Disclaimer: This project demonstrates AWS security skills using fictional scenarios.
No real patient health information (PHI) or client data was used.*
