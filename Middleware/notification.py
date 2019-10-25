import boto3
import json


def publish_it(msg):

    client = boto3.client('sns')
    txt_msg = json.dumps(msg)

    client.publish(TopicArn="arn:aws:sns:us-east-1:635405468376:newuser",
                   Message=txt_msg)