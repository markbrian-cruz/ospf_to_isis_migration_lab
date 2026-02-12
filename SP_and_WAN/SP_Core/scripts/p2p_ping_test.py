import os
import csv
import ipaddress
import re
from netmiko import ConnectHandler

def p2p_ping_test():
    # finding directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(script_dir, "..", "devices.csv")

    try:
        with open(database_path, mode='r') as f:
            reader = list(csv.DictReader(f))
            ip_to_name = {row['ip']: row['hostname'] for row in reader}

            for device in reader:
                print(f"\n{device['hostname']}")

                try:
                    net_connect = ConnectHandler(
                        device_type='cisco_ios',
                        host=device['ip'],
                        username=device['username'],
                        password=device['password'],
                        fast_cli=False
                    )

                    # finding p2p address
                    output = net_connect.send_command("show ip interface")
                    interface_blocks = re.split(r'\n(?=\S)', output)

                    for block in interface_blocks:
                        intf_match = re.search(r"^(\S+) is", block)
                        ip_match = re.search(r"Internet address is (\d+\.\d+\.\d+\.\d+)/(\d+)", block)

                        if intf_match and ip_match:
                            intf_name = intf_match.group(1)
                            ip = ip_match.group(1)
                            prefix = int(ip_match.group(2))

                            # Keep /31 logic as the primary filter
                            if prefix == 31:
                                addr = ipaddress.IPv4Address(ip)
                                # finding p2p address (math for /31 neighbor)
                                neighbor_ip = str(addr + 1 if int(addr) % 2 == 0 else addr - 1)

                                # additional identification via CDP
                                cdp_out = net_connect.send_command(f"show cdp neighbors {intf_name} detail")
                                neighbor_match = re.search(r"Device ID: (\S+)", cdp_out)

                                if neighbor_match:
                                    # Finding name of neighbor from CDP
                                    neighbor_id = neighbor_match.group(1).split('(')[0].split('.')[0]
                                else:
                                    # Fallback to CSV name or IP if CDP is not active
                                    neighbor_id = ip_to_name.get(neighbor_ip, neighbor_ip)

                                # send ping in cli
                                ping_res = net_connect.send_command(f"ping {neighbor_ip} size 1500 repeat 100 df-bit")

                                # output of ping result/rtt
                                match_stats = re.search(r"\((\d+/\d+)\)", ping_res)
                                stats = match_stats.group(1) if match_stats else "0/100"

                                rtt_line = "round-trip min/avg/max = N/A"
                                for line in ping_res.splitlines():
                                    if "round-trip" in line:
                                        rtt_line = line.strip()

                                print(f"\nvia {intf_name} to {neighbor_id} ({neighbor_ip}):")
                                print(f"success rate {stats}")
                                print(f"{rtt_line}")

                    net_connect.disconnect()
                except Exception:
                    continue

    except FileNotFoundError:
        print(f"File not found: {database_path}")

if __name__ == "__main__":
    p2p_ping_test()
