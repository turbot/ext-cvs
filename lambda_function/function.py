import json
import boto3
import os
import requests
from requests.auth import HTTPBasicAuth

def check_existing_tasks(session, sn_instance, azure_vm_id, proxies):
    api_endpoint = get_sn_turbot_endpoint(sn_instance)
    endpoint = f"{api_endpoint}?sysparm_query=object_id={azure_vm_id}"
    response = session.get(endpoint, proxies=proxies)
    if response.status_code == 200:
        results = response.json().get('result', [])
        return results
    else:
        print(f"Failed to query existing tasks: {response.status_code}")
        return []

def close_task(session, sn_instance, task_sys_id, proxies):
    close_endpoint = f"{sn_instance}/api/now/table/task/{task_sys_id}"
    payload = {
        "state": "7",  # Assuming '7' is the state for 'Closed'
        "close_code": "Closed/Resolved by Caller",
        "close_notes": "The problem has been resolved."
    }
    response = session.patch(close_endpoint, json=payload, proxies=proxies)

    if response.status_code == 200:
        result = {
            'status_code': 200,
            'body': f"Task {task_sys_id} successfully closed."
        }
        
    else:
        result = {
            'status_code': response.status_code,
            'body': f"Failed to close task {task_sys_id}: {response.status_code}"
        }
    
    return result

def close_tasks(session, sn_instance, existing_tasks, proxies):
    for task in existing_tasks:
        close_task(session, sn_instance, task['sys_id'], proxies)

def get_sn_turbot_endpoint(sn_instance):
    return f'{sn_instance}/api/aelim/turbot_follow_on_task'

def open_task(session, sn_instance, azure_vm_id, proxies, resource_owner='Unknown'):
    api_endpoint = get_sn_turbot_endpoint(sn_instance)
    description = (
        "There is a problem with the 'costcenter' tag on this resource. "
        f"The tag value is {pay_load['resource_owner']} which is invalid. "
        "Please update the costcenter tag to a valid value.\n\n"
        "Suggested Action:\n"
        "- Check the current cost center tag value.\n"
        "- Update the cost center tag with the correct value.\n"
        "- Verify the tag update by checking the resource in the Azure portal.\n\n"
        "For more information, refer to the Azure documentation on managing tags: "
        "[Azure Tag Management](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources)\n"
    )

    payload = {
        "short_description": "Problems with Cost Center tag",
        "description": description,
        "object_id": azure_vm_id,
        "resource_owner": pay_load['resource_owner']
    }

    try:
        response = session.post(api_endpoint, json=payload, proxies=proxies)

        if response.status_code == 200:
            result = {
                'status_code': 200,
                'body': f"Successfully added task for Azure VM: {azure_vm_id}"
            }
            
        else:
            result = {
                'status_code': response.status_code,
                'body': f"SNow Error creating task: {response.status_code}"
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        result = {
            'status_code': 500,
            'body': f'Error: {str(e)}'
        }
    
    return result

def lambda_handler(event, context):
    print("Initialize the SSM client")
    ssm_client = boto3.client('ssm')
    
    try:
        print("Retrieve the parameters from SSM")
        authname = ssm_client.get_parameter(Name=os.environ['AUTH_NAME_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
        authsecret = ssm_client.get_parameter(Name=os.environ['AUTH_SECRET_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
        sn_instance = ssm_client.get_parameter(Name=os.environ['SN_INSTANCE_SSM_PARAM'], WithDecryption=False)['Parameter']['Value']
        turbot_key = ssm_client.get_parameter(Name=os.environ['TURBOT_KEY_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
        turbot_secret = ssm_client.get_parameter(Name=os.environ['TURBOT_SECRET_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
        turbot_workspace = ssm_client.get_parameter(Name=os.environ['WORKSPACE_SSM_PARAM'], WithDecryption=False)['Parameter']['Value']
        polling_window = os.environ['POLLING_WINDOW']

        https_proxy = os.environ['HTTPS_PROXY']
        http_proxy = os.environ['HTTP_PROXY']
        proxies = {
            'http': proxy_url,
            'https': proxy_url,
        }
        
        print("Get SN Session")
        snow_session = requests.Session()
        snow_session.auth = (sn_username, sn_password)
        snow_session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})

        print("Get Guardrails Session")
        turbot_session = requests.Session()
        turbot_session.headers.update({'Content-Type': 'application/json'})
        turbot_session.auth = HTTPBasicAuth(turbot_key, turbot_secret)
        query_endpoint = f"{turbot_workspace}/api/latest/graphql"
        health_endpoint = f"{turbot_workspace}/api/latest/turbot/health"
        try:
            response = turbot_session.get(health_endpoint)
            if response.status_code != 200:
                print('Health Check: Success!')
            else:
                print(f'Failed to perform health check: {response.status_code}')
                print(response.text)
                exit()
        except requests.exceptions.ConnectionError:
            print("Failed to connect to workspace, exiting.")
            exit()
        
        print("Get latest notifications"):
            query = '''
                
            '''

        for alert in event.get('alerts'):
            print(f"Processing alert: {alert}")
            existing_tasks = check_existing_task(session, sn_instance, alert.get('vmId'), proxies)
            if existing_tasks:
                if alert.get('status') == "ok":
                    print("Tags in ok state, removing existing tasks.")
                    close_tasks(session, sn_instance, existing_tasks, proxies)
                elif alert.get('status') == "alarm":
                    print("Tagging task already exists, taking no action.")
                else:
                    print("Error! unknown status type: {}".format(alert.get('status')))
            else:
                if alert.get('ok') == "alarm":
                    print("Tags in ok state, taking no action.")
                elif alert.get('status') == "alarm":
                    print("Opening task for alarm.")
                    open_task(session, sn_instance, alert.get('vmId'), alert.get('owner'), proxies)
                else:
                    print("Error! unknown status type: {}".format(alert.get('status')))

        if response.status_code == 200:
            print(response.body)
            status = 200
            api_response = "ok"
        else:
            print(response.body)
            status = response.status_code
            api_response = response.body

        response = {
            'statusCode': status,
            'headers': {"content-type": "text/html"},
            'body': api_response
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