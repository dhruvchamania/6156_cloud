import json
import jwt
import time
from botocore.vendored import requests

import boto3
from botocore.exceptions import ClientError

SENDER = "Info <ac4640@columbia.edu>"
RECIPIENT = "ac4640@columbia.edu"

CONFIGURATION_SET = "ConfigSet"

AWS_REGION = "us-east-1"
SUBJECT = "Cool Message from Team Yankees Suck!"

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
             )

# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Amazon SES Test (SDK for Python)</h1>
  <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    <a href='https://aws.amazon.com/sdk-for-python/'>
      AWS SDK for Python (Boto)</a>.</p>

    <p><a href='https://7chrhg2q23.execute-api.us-east-1.amazonaws.com/default/verifyemail/?token={}'>Verify email</a>
    </p>
</body>
</html>
            """

# The character encoding for the email.
CHARSET = "UTF-8"

# Create a new SES resource and specify a region.
client = boto3.client('ses', region_name=AWS_REGION)


# Try to send the email.
def send_email(em):
    try:
        print("em = ", em)
        initial_dictionary = {'time': time.time(), "em": em}
        JWT_ENCODED = (jwt.encode(initial_dictionary, 'secret')).decode("utf-8")
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    em
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML.format(JWT_ENCODED),
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def handle_sns_event(records):
    sns_event = records[0]['Sns']
    topic_arn = sns_event.get("TopicArn", None)
    topic_subject = sns_event.get("Subject", None)
    topic_msg = sns_event.get("Message", None)

    print("SNS Subject = ", topic_subject)
    if topic_msg:
        json_msg = None
        try:
            json_msg = json.loads(topic_msg)
            print("Message = ", json.dumps(json_msg, indent=2))
        except:
            print("Could not parse message.")

        em = json_msg["customers_email"]
        send_email(em)


def lambda_handler(event, context):
    print("Event = ", json.dumps(event, indent=2))

    records = event.get("Records", None)
    print("Records = ", json.dumps(records, indent=2))

    if records:
        handle_sns_event(records)
    else:
        p = event.get("path", None)
        if p is not None:
            print("Got a gateway event!")
            token = event['multiValueQueryStringParameters']['token'][0]
            print('token received:', token)
            try:
                email = jwt.decode(token, 'secret')['em']
                r = requests.put(
                    "http://baseball.9x2apnhkjg.us-east-1.elasticbeanstalk.com/api/user/%s" % email,
                    data=json.dumps({'status':'ACTIVE'}))
                print('PUT email:', email)
                print('PUT data:', r.request.body)
                verification_msg = 'Verification was successful!'
            except Exception as e:
                verification_msg = 'Verification failed!'
                print('verification exception:', e)
        else:
            print("Doing a simple test.")
            em = event.get("customers_email", None)
            if em is not None:
                send_email(em)
            else:
                print("Nothing to do.")

        # TODO implement
        return {
            "statusCode": 200,
            "body": json.dumps(verification_msg)
        }