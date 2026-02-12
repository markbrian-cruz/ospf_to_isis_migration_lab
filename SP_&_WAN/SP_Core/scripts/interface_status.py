import os
import csv
from netmiko import ConnectHandler

def get_status():
    # 1. Finds directory of devices.csv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(script_dir, "..", "devices.csv")

    # 2. Start the file operation
    try:
        with open(database_path, mode='r') as f:
            reader = csv.DictReader(f)
            for device in reader:
                print(f"\n--- [ {device['hostname']} STATUS ] ---")
                try:
                    # 3. SSH connection
                    net_connect = ConnectHandler(
                        device_type="cisco_ios",
                        host=device['ip'],
                        username=device['username'],
                        password=device['password']
                    )

                    # 4. Send CLI command
                    command = "show ip interface brief | exclude unassigned"
                    output = net_connect.send_command(command)

                    # 5. Print output
                    print(output)
                    net_connect.disconnect()

                except Exception as e:
                    print(f"Could not reach {device['ip']}: {e}")
    except FileNotFoundError:
        print(f"File not found at: {database_path}")

if __name__ == "__main__":
    get_status()
