import subprocess
import time
from datetime import datetime
import speedtest
from urllib.error import HTTPError

# Define the IP addresses to ping
check_period = 55       # how many seconds between ping checks
print_success = 0       # print success msg if 1, just timestamp if 2, only "." if 3, and don't print if 0
warning_response = 50   # if greater than this value, the warning message is printed
speedtest_minute = 5    # runs a speed test every hour at this minute (e.g. "5" means 5 minutes after the hour, xx:05)
ip_addresses = {
    'main_router': '192.168.10.1',
    'office_closet_AP': '192.168.10.2',
    'master_bedroom_AP': '192.168.10.3',
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

def speed_test():
    # Create a Speedtest object
    st = speedtest.Speedtest()

    # Retry if get_best_server() returns None or a non-subscriptable object
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            # Get the best server based on ping
            st.get_best_server()

            # Perform the speed test
            st.download()
            st.upload()

            # Get the results
            download_speed = st.results.download / 1_000_000  # Convert to Mbps
            upload_speed = st.results.upload / 1_000_000  # Convert to Mbps
            ping_speed = st.results.ping

            return download_speed, upload_speed, ping_speed
        except (speedtest.ConfigRetrievalError, speedtest.SpeedtestException) as e:
            print(f"Error: {e}. Retrying speed test...")
            # Retry after a short delay
            retries += 1
            time.sleep(2)
        except HTTPError as e:
            if e.code == 403:
                print("Error: HTTP Error 403 - Forbidden. Speed test skipped due to server access issue.")
                return None, None, None
            else:
                print(f"Error: HTTP Error {e.code}. Retrying speed test...")
                retries += 1
                time.sleep(2)
     
    print("Error: Unable to perfom speed test.")
    return None, None, None

def ping_and_speed_test(ip_addresses):
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

        # Perform speed test once per hour
        
        if time.localtime().tm_min == speedtest_minute:    
            download_speed, upload_speed, ping_speed = speed_test()
            print(f"{formatted_time}          Speed Test Results: ")
            print(f"                                 Download Speed: {download_speed:.2f} Mbps")
            print(f"                                 Upload Speed: {upload_speed:.2f} Mbps")
            print(f"                                 Ping: {ping_speed:.2f} ms")

        # Wait for check_period seconds before pinging again
        time.sleep(check_period)

# Start pinging and periodic speed test
ping_and_speed_test(ip_addresses)
