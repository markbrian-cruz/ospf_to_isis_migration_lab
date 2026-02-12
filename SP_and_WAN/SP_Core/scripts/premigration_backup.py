import csv
import os
from netmiko import ConnectHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(script_dir, "..", 'devices.csv')

with open(database_path, mode='r') as f:
    reader = csv.DictReader(f)
    for dev in reader:
        print("Connecting to " + dev['hostname'] + "...")
        try:
            device = {
                'device_type': 'cisco_ios',
                'host': dev['ip'],
                'username': dev['username'],
                'password': dev['password'],
                'global_delay_factor': 2,
                'fast_cli': False,
                'session_log': 'ssh_debug.log'
            }
            with ConnectHandler(**device) as net_connect:
                output = net_connect.send_command("show run")
                filename = dev['hostname'] + ".txt"
                with open(filename, "w") as out:
                    out.write(output)
                print("SUCCESS: Saved " + filename)
        except Exception as e:
            print(f"ERROR: Could not connect to {dev['hostname']}. Reason: {e}")
