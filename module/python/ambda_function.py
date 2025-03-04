import boto3
import json
import logging

# Initialize the AWS SDK clients
sqs_client = boto3.client('sqs')
kms_client = boto3.client('kms')
ec2_client = boto3.client('ec2')
sns_client = boto3.client('sns')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# SNS Topic ARN for sending the alarm
SNS_TOPIC_ARN = 'arn:aws:sns:region:account-id:your-sns-topic'  # Replace with your SNS Topic ARN

def send_sns_alarm(message):
    """Send an SNS message in case of failure"""
    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject='SQS Queue Security Check Failed'
    )

def check_vpc_endpoint(queue_url):
    """Check if there is a VPC endpoint for SQS"""
    # Get VPC endpoints for SQS
    response = ec2_client.describe_vpc_endpoints(Filters=[{'Name': 'service-name', 'Values': ['com.amazonaws.us-east-1.sqs']}])  # Update region if necessary
    if not response['VpcEndpoints']:
        logger.error('No VPC endpoint for SQS found')
        return False
    logger.info('VPC endpoint for SQS exists')
    return True

def check_encryption(queue_url):
    """Ensure that the SQS queue has encryption enabled"""
    response = sqs_client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['QueueArn', 'Policy', 'All']
    )
    if 'QueueArn' in response and response['QueueArn']:
        # Check encryption
        if 'Encryption' not in response:
            logger.error('SQS queue does not have encryption enabled')
            return False
        logger.info('SQS queue encryption enabled')
        return True
    else:
        logger.error('Unable to retrieve queue attributes')
        return False

def check_customer_managed_key(queue_url):
    """Check that the queue uses a Customer-Managed Key (CMK)"""
    response = sqs_client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['KmsMasterKeyId']
    )
    if 'KmsMasterKeyId' in response and response['KmsMasterKeyId']:
        key_id = response['KmsMasterKeyId']
        # Check if the key is a customer-managed key
        key_response = kms_client.describe_key(KeyId=key_id)
        if key_response['KeyMetadata']['KeyManager'] == 'AWS':
            logger.error('SQS queue is using an AWS-managed KMS key')
            return False
        logger.info('SQS queue is using a customer-managed KMS key')
        return True
    else:
        logger.error('SQS queue does not have a KMS key associated')
        return False

def check_tags(queue_url):
    """Check that the SQS queue has specific tags"""
    required_tags = ['Name', 'Created By', 'Cost Center']
    response = sqs_client.list_queue_tags(QueueUrl=queue_url)
    
    if 'Tags' not in response:
        logger.error('SQS queue does not have any tags')
        return False
    
    tags = response['Tags']
    for tag in required_tags:
        if tag not in tags:
            logger.error(f'Missing required tag: {tag}')
            return False
    
    logger.info('SQS queue has the required tags')
    return True

def lambda_handler(event, context):
    """Lambda function handler"""
    # For testing, let's assume the queue URL is passed in the event
    queue_url = event['queue_url']  # Assume that the event includes the queue URL
    
    failure_messages = []
    
    # Check each requirement
    if not check_vpc_endpoint(queue_url):
        failure_messages.append('VPC Endpoint Check Failed')
    
    if not check_encryption(queue_url):
        failure_messages.append('Encryption-at-Rest Check Failed')
    
    if not check_customer_managed_key(queue_url):
        failure_messages.append('Customer-Managed Key (CMK) Check Failed')
    
    if not check_tags(queue_url):
        failure_messages.append('Tag Verification Failed')
    
    # If there are failures, send an SNS message
    if failure_messages:
        message = "The following checks failed for the SQS queue:\n" + "\n".join(failure_messages)
        send_sns_alarm(message)
        return {
            'statusCode': 500,
            'body': json.dumps(failure_messages)
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps('All checks passed')
    }

