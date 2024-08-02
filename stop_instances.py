#!/usr/bin/env python3
import boto3

ec2 = boto3.resource('ec2')
rds = boto3.client('rds')
sns = boto3.client('sns')

include_rds = False
topic = ''
message = []

def lambda_handler(event, context):
    # Stop EC2 instances
    running_instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    for instance in running_instances:
        # get instance Name tag
        instance_name = ''
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                instance_name = tag['Value']
                break
        print('Stopping EC2 instance:', instance.id, ' Name:', instance_name)
        message = [
            'Stopping EC2 instance: ' + instance.id + ', Name: ' + instance_name
        ]

        try:
            instance.stop()
        except Exception as e:
            print('Error stopping instance:', instance.id, ' Error:', e)

    # Stop RDS instances if include_rds is True
    if include_rds:
        rds_instances = rds.describe_db_instances()
        for instance in rds_instances['DBInstances']:
            # Get DB instance Name tag
            instance_name = ''
            for tag in instance['TagList']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
            print('RDS instance:', instance['DBInstanceIdentifier'], ', Name:', instance_name,  ', Status:', instance['DBInstanceStatus'])
            if instance['DBInstanceStatus'] == 'available':
                print('Stopping RDS instance:', instance['DBInstanceIdentifier'])
                try:
                    rds.stop_db_instance(DBInstanceIdentifier=instance['DBInstanceIdentifier'])
                except Exception as e:
                    print('Error stopping RDS instance:', instance['DBInstanceIdentifier'], ' Error:', e)

    if include_rds:
        print('All running EC2 and RDS instances are stopped')
        return 'All running EC2 and RDS instances are stopped'
    else:
        print('All running EC2 instances are stopped')
        return 'All running EC2 instances are stopped'

def alert(message):
    if topic:
        try:
            sns.publish(TopicArn=topic, Message=message)
        except Exception as e:
            print('Error publishing to SNS:', e)
    print(message)

if __name__ == '__main__':
    # include_rds = True
    topic = 'arn:aws:sns:us-east-1:123456789012:StopEC2RDS'

    # Ask for confirmation
    print('This script will stop all running EC2 (and if include_rds = True, RDS) instances.')
    print('Do you want to continue? (y/n) [n]:')
    response = input()
    if response.lower == 'y':
        lambda_handler(None, None)
    else:
        print('Aborted')
        exit(0)
