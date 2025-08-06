# 🧹 AWS Lambda Script to Delete Unused EBS Snapshots

This AWS Lambda function identifies and deletes unused or orphaned EBS snapshots in your AWS account to help reduce storage costs.

---

## 📌 What It Does

- Lists all **running EC2 instances**
- Fetches all **EBS snapshots** owned by you
- Deletes snapshots that:
  - Are **not linked** to any volume
  - Are linked to a **volume that is not attached**
  - Are linked to a volume attached to an **EC2 instance that is not running**
  - Are linked to a volume that **no longer exists**

---

## 🚀 Deployment

### Prerequisites:
- AWS Lambda with an IAM role that has permissions:
  - `ec2:DescribeInstances`
  - `ec2:DescribeSnapshots`
  - `ec2:DescribeVolumes`
  - `ec2:DeleteSnapshot`

### How to Deploy:
1. Go to AWS Lambda Console.
2. Create a new Lambda function (choose Python 3.x as runtime).
3. Copy and paste the code from [`lambda_function.py`](lambda_function.py).
4. Attach an appropriate IAM Role.
5. Set the trigger (e.g., schedule with CloudWatch Events to run daily/weekly).

---

## 🧠 Notes

- This script uses `boto3` to interact with the AWS EC2 service.
- Make sure the Lambda has sufficient timeout and memory (recommended: 256MB+, 30s+).
- Always test on a non-production environment before enabling in production.
