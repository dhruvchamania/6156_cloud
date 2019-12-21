import boto3
import json


def publish_it(msg, topic='arn:aws:sns:us-east-1:635405468376:newuser'):

    client = boto3.client('sns', region_name='us-east-1')
    txt_msg = json.dumps(msg)

    client.publish(TopicArn=topic,
                   Message=txt_msg)
