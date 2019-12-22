import boto3
import json


def publish_it(msg, topic='arn:aws:sns:us-east-1:635405468376:newuser'):

    client = boto3.client('sns', region_name='us-east-1')
    txt_msg = json.dumps(msg)

    client.publish(TopicArn=topic,
                   Message=txt_msg)

def address(request_payload):
    lam = boto3.client('lambda',region_name='us-east-1')
    resp = lam.invoke(
             FunctionName='lambda_function_name',
             InvocationType='RequestResponse',
             LogType='Tail',
             Payload=json.dumps(request_payload))
    print("result from lambda")
    resp_data = resp['Payload'].read()

    resp_data = resp['Payload'].read()

    resp_data_decoded = json.loads(resp_data.decode())
    print(resp_data_decoded)

    return resp_data_decoded