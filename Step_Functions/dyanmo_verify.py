from botocore.vendored import requests
import logging
import json

logger = logging.getLogger()
import json
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

global table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('addressTable')


def update_database(address, user_id):
    global table
    table.put_item(
        Item={
            'address_id': address['deliver_point_barcode'],
            'primary_number': address['primary_number'],
            'street_name': address['street_name'],
            'street_suffix': address['street_suffix'],
            'city_name': address['city_name'],
            'state': address['state_abbreviation'],
            'zipcode': address['zipcode']
        }
    )

    pass


def lambda_handler(event, context):
    valid_address = event

    update_database(valid_address, "id")
    # post_profile_service(valid_address)
    print(valid_address)

    res = {

        "statusCode": '200',

        "headers": {
            "content-type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },

        "body": json.dumps(valid_address['deliver_point_barcode'], indent=2)
    }

    return res