import yaml
from netmiko import ConnectHandler

# Load hidden secrets from secrets.yml
with open("secrets.yml", 'r') as f:
    secrets = yaml.safe_load(f)

# Define the Customer A Loopback Management IPs
routers = [
    {"name": "CustomerA1 (Left)", "host": "1.1.1.1"},
    {"name": "CustomerA3 (Left)", "host": "3.3.3.3"},
    {"name": "CustomerA2 (Right)", "host": "2.2.2.2"},
    {"name": "CustomerA4 (Right)", "host": "4.4.4.4"}
]

print(f"{'Router Name':<20} | {'Management IP':<15} | {'Status'}")
print("-" * 50)

for r in routers:
    device = {
        "device_type": "cisco_ios",
        "host": r["host"],
        "username": secrets["ansible_user"],
        "password": secrets["ansible_ssh_pass"],
        "secret": secrets["ansible_become_pass"],
    }
    
    try:
        # Connect and verify we hit privilege 15 directly
        with ConnectHandler(**device) as ssh:
            prompt = ssh.find_prompt()
            print(f"{r['name']:<20} | {r['host']:<15} | [UP] {prompt}")
    except Exception as e:
        print(f"{r['name']:<20} | {r['host']:<15} | [FAILED] {str(e)[:25]}...")
