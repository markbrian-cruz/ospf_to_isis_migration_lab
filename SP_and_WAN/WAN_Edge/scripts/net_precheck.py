import yaml
from netmiko import ConnectHandler

# 1. Load your hidden secrets
with open("secrets.yml", 'r') as f:
    secrets = yaml.safe_load(f)

# 2. Define your Customer A nodes
routers = [
    {"device_type": "cisco_ios", "host": "1.1.1.1", "name": "CustomerA1"},
    {"device_type": "cisco_ios", "host": "2.2.2.2", "name": "CustomerA2"},
    {"device_type": "cisco_ios", "host": "3.3.3.3", "name": "CustomerA3"},
    {"device_type": "cisco_ios", "host": "4.4.4.4", "name": "CustomerA4"},
]

print("--- Starting WAN Edge Connectivity Check ---")

for router in routers:
    connection_data = {
        "device_type": router["device_type"],
        "host": router["host"],
        "username": secrets["ansible_user"],
        "password": secrets["ansible_ssh_pass"],
        "secret": secrets["ansible_become_pass"],
    }
    
    try:
        print(f"Testing {router['name']} ({router['host']})...")
        net_connect = ConnectHandler(**connection_data)
        net_connect.enable()
        
        # Simple verification command
        output = net_connect.send_command("show version | inc uptime")
        print(f"  [SUCCESS] {router['name']} is REACHABLE.")
        print(f"  [INFO] {output.strip()}")
        
        net_connect.disconnect()
    except Exception as e:
        print(f"  [FAILED] {router['name']} is NOT REACHABLE.")
        print(f"  [ERROR] {e}")

print("--- Pre-check Complete ---")
