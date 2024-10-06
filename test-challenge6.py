import requests
import re
import time
import sys
import argparse
import os

INGRESS_HOSTNAME = os.getenv('INGRESS_HOSTNAME', 'default-hostname')

# Function to send a simple request
def send_simple_request():
    url = f"http://{INGRESS_HOSTNAME}/random-code"
    # Sending a GET request
    response = requests.get(url)

    # Printing the response headers and body
    print("Response Headers:")
    print(response.headers)

    print("\nResponse Body:")
    print(response.text)

# Function to send high load
def send_high_load():
    url = f"http://{INGRESS_HOSTNAME}"

    for i in range(2000):
        response = requests.get(url)
        print(f"Request {i+1}: {response.status_code}")

    print("Completed 2000 requests.")

# Function to send a file to a URL
def send_file_to_url(file_path):
    url = f"http://{INGRESS_HOSTNAME}/upload"
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        print(f"File uploaded successfully: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Function to perform sequence of requests and match text
def test_load_balance():
    url = f"http://{INGRESS_HOSTNAME}"

    for i in range(1, 100):
        response = requests.get(url)
        
        matches = re.findall(r"Pod.*", response.text)
        print("Resquest #", i)
        for match in matches:
            print(match)
        time.sleep(0.2)  



# Main function to handle argument parsing
def main():
    parser = argparse.ArgumentParser(description="Execute different actions based on provided arguments.")
    
    parser.add_argument('--send_high_load', action='store_true', help='Send 2000 requests to the server.')
    parser.add_argument('--send_file', type=str, help='Send a file to the server. Provide the file path as an argument.')
    parser.add_argument('--test_load_balance', action='store_true', help='Perform a sequence of requests with matching.')
    parser.add_argument('--send_simple_request', action='store_true', help='Send a simple GET request and print headers and body.')

    args = parser.parse_args()

    if args.send_simple_request:
        send_simple_request()
    elif args.send_high_load:
        send_high_load()
    elif args.send_file:
        send_file_to_url(args.send_file)
    elif args.test_load_balance:
        test_load_balance()    
    else:
        print("Please specify one of the available options: --send_simple_request, --send_high_load, --send_file <file_path>, --test_load_balance")

if __name__ == "__main__":
    main()
