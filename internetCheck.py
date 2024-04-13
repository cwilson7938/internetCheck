import subprocess
import time
from datetime import datetime
import sys

# Define the IP addresses to ping
check_period = 30       # how many seconds between ping checks
print_success = 0      # print success msg if 1, just timestamp if 2, only "." if 3, and don't print if 0
warning_response = 100   # if greater than this value, the warning message is printed
ip_addresses = {
    'main_router': '192.168.10.1',
    'officecloset_AP': '192.168.10.2',
    'maste_bedroom_AP': '192.168.10.3',
    'back_bedroom_AP': '192.168.10.4'
}

def ping_host(ip):
    try:
        # Run the ping command and capture output
        result = subprocess.run(['ping', '-A', '-c', '5', ip], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Parse the output to get the average response time
            lines = result.stdout.splitlines()
            for line in lines:
                if 'rtt min/avg/max/mdev' in line:
                    avg_time = float(line.split('/')[4])
                    return avg_time
        else:
            return None
    except subprocess.TimeoutExpired:
        return None

def ping_devices(ip_addresses):
    while True:
    # Initialize variables for average response time and unreachable devices
        avg_response_time = {}
        unreachable_devices = []

        # Ping each device and calculate average response time
        for device, ip_address in ip_addresses.items():
            avg_time = ping_host(ip_address)
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            if avg_time is not None:
                avg_response_time[device] = avg_time
                if avg_time <= warning_response:
                    if print_success == 1:
                        print(f"{formatted_time}       Great! {device} average response time is {avg_time}ms.")
                    elif print_success == 2:
                        print(formatted_time)
                    elif print_success ==3:
                        print(".", end="", flush=True)
                elif avg_time > warning_response:
                    print(f"{formatted_time}  Warning: {device} average response time of {avg_time}ms is greater than {warning_response}ms.")
            else:
                unreachable_devices.append(device)
 
        # Display errors for unreachable devices
        if unreachable_devices:
            print(f"{formatted_time}  Error: The following devices are unreachable: {', '.join(unreachable_devices)}")

        # Wait for 10 seconds before pinging again
        time.sleep(check_period)

# Start pinging devices
ping_devices(ip_addresses)
