import json
import boto3
import os
import requests
from requests.auth import HTTPBasicAuth

def lambda_handler(event, context):
    # Initialize the SSM client
    print(event)

    ssm_client = boto3.client('ssm')
    
    try:
        # Retrieve the parameters from SSM
        authname = ssm_client.get_parameter(Name=os.environ['AUTH_NAME_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
        authsecret = ssm_client.get_parameter(Name=os.environ['AUTH_SECRET_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
        
        # Extract specific data from the event
        name = event.get('name', 'Guest')
        message = event.get('message', 'Hello from Lambda!')

        # Make a request to the public API using Basic Auth
        response = requests.get(
          'https://httpbin.org/basic-auth/user/pass', 
          auth=HTTPBasicAuth(authname, authsecret)
        )
        
        # Check the response from the public API
        if response.status_code == 200:
            api_response = response.json()
        else:
            api_response = {'error': 'Failed to authenticate with the public API'}

        # Create a response
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'greeting': f'Hello, {name}!',
                'message': message,
                'api_response': api_response
            })
        }

    except Exception as e:
        # Handle any errors that occur
        response = {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

    return response