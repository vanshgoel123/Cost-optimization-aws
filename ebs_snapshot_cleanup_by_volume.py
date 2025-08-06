"""
AWS Lambda function for EBS snapshot cost optimization.

This function identifies and deletes orphaned EBS snapshots to reduce storage costs.
It removes snapshots that are:
1. Not associated with any volume (volume was deleted)
2. Associated with volumes that are not attached to any instance
3. Associated with volumes attached to non-running instances

Purpose: Reduce AWS storage costs by cleaning up unused EBS snapshots
"""

import boto3

def lambda_handler(event, context):
    """
    Main Lambda handler function for EBS snapshot cleanup.
    
    Args:
        event: AWS Lambda event object (not used in this function)
        context: AWS Lambda context object (not used in this function)
    
    Returns:
        None (prints deletion status to CloudWatch logs)
    """
    
    # Initialize EC2 client for AWS API interactions
    ec2 = boto3.client('ec2')
    
    # Get all currently running EC2 instances to identify active workloads
    instances_response=ec2.describe_instances(Filters=[{'Name':'instance-state-name','Values':['running']}])
    
    # Create a set to store IDs of all running instances for quick lookup
    active_instances_ids=set()
    
    # Extract instance IDs from the nested response structure (Reservations -> Instances)
    for reservation in instances_response['Reservations']:
        for instance in reservation['Instances']:
            active_instances_ids.add(instance['InstanceId'])
    
    # Get all EBS snapshots owned by this account
    response=ec2.describe_snapshots(OwnerIds=['self'])
    
    # Iterate through each snapshot to determine if it should be deleted
    for snapshot in response['Snapshots']:
        snapshot_id=snapshot['SnapshotId']
        volume_id=snapshot['VolumeId']
    
    # Check if the snapshot has an associated volume ID
    if not volume_id:
        # Delete snapshots that are not associated with any volume
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        print(f"Deleted EBS Snapshot {snapshot_id} as it was not attached to any volume")
    else :
        try:
            # Check the status of the volume associated with this snapshot
            volume_response=ec2.describe_volumes(VolumeIds=[volume_id])
            
            # Check if the volume is not attached to any instance
            if not volume_response['Volumes'][0]['Attachments']:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS Snapshot {snapshot_id} as it was taken from a volume not attached to any instance")
            
            # Get the instance ID that the volume is attached to (this line has a bug - should be volume_response)
            active_instance_id=volume_id['Attachments'][0]['InstanceId']
            
            # Check if the attached instance is currently running
            if active_instance_id not in active_instances_ids:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS Snapshot {snapshot_id} as its associated volume is not attached to any running instance")
        except ec2.exceptions.ClientError as e:
            # Handle the case where the volume no longer exists
            if e.response['Error']['Code']=='InvalidVolume.NotFound':
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS Snapshot {snapshot_id} as its associated volume is not found")
            
