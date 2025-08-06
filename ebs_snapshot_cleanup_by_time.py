import boto3
from datetime import datetime,timezone,timedelta
import botocore
 
def lambda_handler(event,context):
    ec2=boto3.client('ec2')
    retention_days=30
    cutoff_date=datetime.now(timezone.utc) - timedelta(days=retention_days)
    active_instances_ids=set()
    next_token=None
    while True:
        try:
            if next_token:
                instances_response=ec2.describe_instances(
                    Filters=[{'Name':'instance-state-name','Values':['running']}],
                    NextToken=next_token
                )
            else:
                instances_response=ec2.describe_instances(
                    Filters=[{'Name':'instance-state-name','Values':['running']}]
                )
            for reservation in instances_response['Reservations']:
                for instance in reservation['Instances']:
                    active_instances_ids.add(instance['InstanceId'])
            
            next_token = instances_response.get('NextToken')
            if not next_token:
               break

        except botocore.exceptions.ClientError as e:
            print(f"Error fetching instances")
            return
    
    snapshots=[]
    next_token=None
    while True:
        try:
            if next_token:
                response=ec2.describe_snapshots(OwnerIds=['self'],NextToken=next_token)
            else:
                response=ec2.describe_snapshots(OwnerIds=['self'])
                
            snapshots.extend(response['Snapshots'])
            
            if 'NextToken' in response:
                next_token=response['NextToken']
            else:
                break
        except botocore.exceptions.ClientError as e:
            print(f"Error fetching snapshots: {e}")
            return
    
    for snapshot in snapshots:
        try:
            snapshot_id=snapshot['SnapshotId']
            volume_id=snapshot.get('VolumeId')
            start_time=snapshot['StartTime']
            
            if start_time>cutoff_date:
                print(f"Skipping snapshot {snapshot_id } (created within the last {retention_days} days)")
                continue
            if not volume_id:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS Snapshot {snapshot_id} as it was not attached to any volume")
                continue
            volume_response=ec2.describe_volumes(VolumeIds=[volume_id]) 
            volume=volume_response['Volumes'][0]
            
            if not volume['Attachments']:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS Snapshot {snapshot_id} as it was taken from a volume not attached to any instance")
                continue
            
            attached_instance_id=volume['Attachments'][0]['InstanceId']
            if attached_instance_id not in active_instances_ids:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS Snapshot {snapshot_id} as its associated volume is not attached to any running instance")
            
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidSnapshot.NotFound':
                print(f"EBS Snapshot not found")
            elif e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted snapshot {snapshot_id}: associated volume not found")
            else:
                print(f"Error processing snapshot {snapshot_id}: {e}")
        except Exception as e:
            print(f"Unexpected error for snapshot {snapshot.get('SnapshotId','Unknown')}: {e}")
    return {
                        "status": "completed",
                        "snapshots_checked": len(snapshots),
                        "instances_running": len(active_instances_ids)
                }