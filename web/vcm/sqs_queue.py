
import boto3
from decouple import config

def sendMessageToQueue(message):
    CLOUD_FRONT = config('CLOUD_FRONT', default='')
    AWS_MEDIA = '/media/'
    MEDIA_URL = 'http://' + CLOUD_FRONT + AWS_MEDIA


    region_name = 'us-east-1'
    queue_name = config('AWS_SQS_QUEUE_NAME', default='')
    aws_access_key_id = config('AWS_ACCESS_KEY_ID', default='')
    aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY', default='')


    sqs = boto3.resource('sqs', region_name=region_name,
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key)

    queue = sqs.get_queue_by_name(QueueName=queue_name)


    resp = MEDIA_URL + message
    queue.send_message(MessageBody=resp)

