# 💸 AWS EBS Snapshot Cleanup Automation

This repository contains **two AWS Lambda functions** that help you automatically delete unused or old Amazon EBS snapshots to **optimize AWS costs**. It ensures your environment stays clean by removing snapshots that are either:

- Too old (based on a defined retention period)
- Not associated with any active volume or instance

---

## 📂 Table of Contents

- [Features](#features)  
- [Functions Included](#functions-included)  
- [Prerequisites](#prerequisites)  
- [Deployment](#deployment)  
- [IAM Permissions](#iam-permissions)  
- [Contributing](#-contributing)  
- [License](#license)  
- [Author](#author)  

---

## ✨ Features

✅ Automatically deletes unnecessary EBS snapshots  
✅ Two cleanup modes: by **volume attachment** or by **snapshot age**  
✅ Cost-effective solution for EBS snapshot management  
✅ Written in Python using AWS SDK (`boto3`)  
✅ Safe with built-in error handling and logging  
✅ Easily schedulable via CloudWatch Events or EventBridge  

---

## 🛠️ Functions Included

### 1. `ebs_snapshot_cleanup_by_volume.py`

🔍 **Logic:**
- Identifies all currently running EC2 instances
- Checks each EBS snapshot owned by your AWS account
- Deletes snapshots that:
  - Are not attached to any volume  
  - Belong to volumes not attached to any EC2 instance  
  - Are from volumes not attached to running instances  
  - Are linked to volumes that no longer exist  

📌 **Use Case:**  
Ideal for dynamic infrastructure environments where cleanup is based on resource usage.

---

### 2. `ebs_snapshot_cleanup_by_time.py`

🔍 **Logic:**
- Scans all EBS snapshots owned by your account
- Deletes those **older than a specified number of days (e.g., 30)**

📌 **Use Case:**  
Best for organizations with fixed snapshot retention policies (e.g., 7, 30, or 90 days).

---

## ⚙️ Prerequisites

- AWS Account with Lambda permissions
- Python 3.8+ runtime for Lambda
- IAM role with required EC2 and snapshot permissions

---

## 🚀 Deployment

1. **Create a Lambda function** in AWS Console
2. **Paste the relevant Python script** (`ebs_snapshot_cleanup_by_volume.py` or `ebs_snapshot_cleanup_by_time.py`)
3. Attach an **IAM role** with the required permissions (see below)
4. Optionally configure a **CloudWatch Event rule** to run it on a schedule (e.g., daily or weekly)

---

## 🔐 IAM Permissions

Both Lambda functions need the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeSnapshots",
        "ec2:DeleteSnapshot"
      ],
      "Resource": "*"
    }
  ]
}
