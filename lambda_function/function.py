import json
import boto3
import os
import requests
from requests.auth import HTTPBasicAuth

def check_existing_task(session, sn_instance, azure_vm_id, proxies, mode):
    api_endpoint = get_sn_turbot_endpoint(sn_instance)
    endpoint = f"{api_endpoint}?sysparm_query=object_id={azure_vm_id}"
    if mode == "TESTING":
        print(f"Mock call to check existing task: {endpoint}")
        return []
    else:
        response = session.get(endpoint, proxies=proxies)
        if response.status_code == 200:
            results = response.json().get('result', [])
            return results
        else:
            print(f"Failed to query existing tasks: {response.status_code}")
            return []

def close_task(session, sn_instance, task_sys_id, proxies, mode):
    close_endpoint = f"{sn_instance}/api/now/table/task/{task_sys_id}"
    payload = {
        "state": "7",  # Assuming '7' is the state for 'Closed'
        "close_code": "Closed/Resolved by Caller",
        "close_notes": "The problem has been resolved."
    }
    
    if mode == "TESTING":
        print(f"Mock call to close task: {close_endpoint}")
        print(f"Mock Payload: {payload}")
        return True
    else:
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

def close_tasks(session, sn_instance, existing_tasks, proxies, mode):
    for task in existing_tasks:
        close_task(session, sn_instance, task['sys_id'], proxies, mode)

def get_sn_turbot_endpoint(sn_instance):
    return f'{sn_instance}/api/aelim/turbot_follow_on_task'

def open_task(session, sn_instance, azure_vm_id, proxies, resource_owner, mode):
    api_endpoint = get_sn_turbot_endpoint(sn_instance)
    description = (
        "There is a problem with the 'costcenter' tag on this resource. "
        f"The tag value is {resource_owner} which is invalid. "
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
        "resource_owner": resource_owner
    }

    if mode == "TESTING":
        print(f"Mock call to open task: {api_endpoint}")
        print(f"Mock Payload: {payload}")
        return True
    else:
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

def graphql_query(session, endpoint, query, vars):
    response = session.post(endpoint, json={'query': query, 'variables': vars})
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Failed to query GraphQL endpoint: {response.status_code}')
        print(response.text)
        return None

def lambda_handler(event, context):
    print("Initialize the SSM client")
    ssm_client = boto3.client('ssm')
    
    print("Retrieve the parameters from SSM")
    sn_authname = ssm_client.get_parameter(Name=os.environ['AUTH_NAME_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
    sn_authsecret = ssm_client.get_parameter(Name=os.environ['AUTH_SECRET_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
    sn_instance = ssm_client.get_parameter(Name=os.environ['SN_INSTANCE_SSM_PARAM'], WithDecryption=False)['Parameter']['Value']
    turbot_key = ssm_client.get_parameter(Name=os.environ['TURBOT_KEY_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
    turbot_secret = ssm_client.get_parameter(Name=os.environ['TURBOT_SECRET_SSM_PARAM'], WithDecryption=True)['Parameter']['Value']
    turbot_workspace = ssm_client.get_parameter(Name=os.environ['WORKSPACE_SSM_PARAM'], WithDecryption=False)['Parameter']['Value']
    polling_window = os.environ['POLLING_WINDOW']
    execution_mode = os.environ['EXECUTION_MODE']
    ssl_verify = True if os.environ['VERIFY_CERTIFICATE'] not in ["False","false","no","0"] else False  

    https_proxy = os.environ['HTTPS_PROXY']
    http_proxy = os.environ['HTTP_PROXY']

    if http_proxy != "":
        proxies = {
            'http': https_proxy,
            'https': http_proxy,
        }
    else:
        proxies = None
    
    print("Get SN Session")
    snow_session = requests.Session()
    snow_session.auth = (sn_authname, sn_authsecret)
    snow_session.verify = ssl_verify
    snow_session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})

    print("Get Guardrails Session")
    turbot_session = requests.Session()
    turbot_session.verify = ssl_verify
    turbot_session.headers.update({'Content-Type': 'application/json'})
    turbot_session.auth = HTTPBasicAuth(turbot_key, turbot_secret)
    query_endpoint = f"{turbot_workspace}/api/latest/graphql"
    health_endpoint = f"{turbot_workspace}/api/latest/turbot/health"

    try:
        response = turbot_session.get(health_endpoint)
        if response.status_code == 200:
            print('Health Check: Success!')
        else:
            print('Failed to perform health check')
            print(f'status code: {response.status_code}')
            print(f'response: {response.text}')
            print(f'endpoint: {health_endpoint}')
            return { 
                'message' : "Error, Exiting."
            }
    except requests.exceptions.ConnectionError as e:
        print(f'ConnectionError: {e}')
        return { 
            'message' : "Error, Exiting."
        }

    print("Get latest notifications")

    query = '''
        query recentNotifications($filter: [String!], $paging: String) {
            notifications(
                filter: $filter
                paging: $paging
                dataSource: DB
            ) {
                items {
                control {
                    state
                }
                resource {
                    data
                    tags
                }
                notificationType
                }
                paging {
                next
                }
            }
        }
    '''

    filter = [
        "controlTypeId:'tmod:@turbot/azure-compute#/control/types/virtualMachineApproved'", 
        f"timestamp:>=T-{polling_window}m", 
        "sort:-createTimestamp", 
        "limit:20",
        "state:ok,alarm"
        "notificationType:'control_updated'"
    ]

    paging = None
    
    alerts = {}

    while True:
        vars = {
            "filter": filter,
            "paging": paging
        }
        response = graphql_query(turbot_session, query_endpoint, query, vars)
        for notification in response.get("data").get("notifications").get("items"):
            print(f"Found Alert: {notification}")
            vmId = notification.get("resource",{}).get("data",{}).get("vmId","")
            state = notification.get("control").get("state")
            owner = notification.get("resource").get("tags").get("resourceowner", "unknown")
            if vmId and state:
                if vmId in alerts:
                    print("Duplicate VM, Skipping")
                else:
                    print(f"Found Alert for vm: {vmId}")
                    alerts[vmId] = {
                        "state": state,
                        "owner": owner
                    }
        paging = response.get("data").get("notifications").get("paging").get("next")
        if not paging:
            #no more notifications
            break    
    
    for vmId, alert in alerts.items():
        print(f"Processing alert for vm: {vmId}")
        existing_tasks = check_existing_task(snow_session, sn_instance, vmId, proxies, execution_mode)
        if existing_tasks:
            if alert.get('state') == "ok":
                print("Tags in ok state, removing existing tasks.")
                close_tasks(snow_session, sn_instance, existing_tasks, proxies, execution_mode)
            elif alert.get('state') == "alarm":
                print("Tagging task already exists, taking no action.")
            else:
                print("Error! unknown status type: {}".format(alert.get('status')))
        else:
            if alert.get('state') == "ok":
                print("Tags in ok state, taking no action.")
            elif alert.get('state') == "alarm":
                print("Opening task for alarm.")
                open_task(snow_session, sn_instance, vmId, alert.get('owner'), proxies, execution_mode)
            else:
                print("Error! unknown status type: {}".format(alert.get('status')))

    print("Success: {} Notifications processed".format(len(alerts)))
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message" : "Success",
            "alerts"  : alerts
        })
    }
