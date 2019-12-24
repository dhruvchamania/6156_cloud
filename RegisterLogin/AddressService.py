import Middleware.security as security
from Context.Context import Context
from CustomerInfo.Users import UsersService as user_svc
import boto3
import json


class AddressService():

    @classmethod
    def address(request_payload, context):
        lam = boto3.client('lambda', region_name='us-east-1')
        resp = lam.invoke(
            FunctionName='arn:aws:lambda:us-east-1:635405468376:function:verifyaddress',
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=json.dumps(context))
        print("result from lambda")
        resp_data = resp['Payload'].read()

        resp_data = resp['Payload'].read()

        resp_data_decoded = json.loads(resp_data.decode())
        print(resp_data_decoded)

        return resp_data_decoded