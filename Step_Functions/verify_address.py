from botocore.vendored import requests
import logging
import json

logger = logging.getLogger()
import json
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_address(address):
    params = {}
    params['auth-token'] = "BNMH4FYUQklImJOLJWLd"
    params['auth-id'] = "c54345c7-8c41-476f-9b14-8eea4021c26f"
    url = "https://us-street.api.smartystreets.com/street-address"

    if (params['auth-id'] is None) or (params['auth-token'] is None) or (url is None):
        logger.error("Couldn't get security info or environment")
        return 500
    try:
        street = address.get('street', None)
        params['street'] = street

        state = address.get('state', None)
        if state is not None:
            params['state'] = state

        city = address.get('city', None)
        if city is not None:
            params['city'] = city

        zipcode = address.get('zipcode', None)
        if zipcode is not None:
            params['zipcode'] = zipcode
    except KeyError as ke:
        logger.info("Input was not valid")
        return 442

    result = requests.get(url, params=params)

    if result.status_code == 200:
        j_data = result.json()

        if len(j_data) > 1:
            rsp = None
        else:
            rsp = j_data[0]['components']
            rsp['deliver_point_barcode'] = j_data[0]['delivery_point_barcode']
    else:
        rsp = None

    return rsp


def lambda_handler(event, context):
    address = event['body']
    valid_address = validate_address(address)

    return valid_address