import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    instances_response=ec2.describe_instances(Filters=[{'Name':'instance-state-name','Values':['running']}])
    active_instances_ids=set()
    for reservation in instances_response['Reservations']:
        for instance in reservation['Instances']:
            active_instances_ids.add(instance['InstanceId'])
    response=ec2.describe_snapshots(OwnerIds=['self'])
    for snapshot in response['Snapshots']:
        snapshot_id=snapshot['SnapshotId']
        volume_id=snapshot['VolumeId']
    if not volume_id:
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        print(f"Deleted EBS Snapshot {snapshot_id} as it was not attached to any volume")
    else :
        try:
            volume_response=ec2.describe_volumes(VolumeIds=[volume_id])
            if not volume_response['Volumes'][0]['Attachments']:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS Snapshot {snapshot_id} as it was taken from a volume not attached to any instance")
            active_instance_id=volume_id['Attachments'][0]['InstanceId']
            if active_instance_id not in active_instances_ids:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS Snapshot {snapshot_id} as its associated volume is not attached to any running instance")
        except ec2.exceptions.ClientError as e:
            if e.response['Error']['Code']=='InvalidVolume.NotFound':
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS Snapshot {snapshot_id} as its associated volume is not found")
            
