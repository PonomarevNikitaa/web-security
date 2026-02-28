import requests
import argparse
import sys
from colorama import Fore, Style, init

init(autoreset=True)

def load_payloads(wordlist_path):
    try:
        with open(wordlist_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + "[!] Wordlist not found.")
        sys.exit(1)


def send_request(url):
    try:
        response = requests.get(url, timeout=5)
        return response
    except requests.RequestException as e:
        print(Fore.YELLOW + f"[!] Request error: {e}")
        return None


def analyze_response(response, baseline_length):
    suspicious = False

    if response.status_code >= 500:
        suspicious = True

    if abs(len(response.text) - baseline_length) > 50:
        suspicious = True

    error_patterns = ["sql", "syntax", "error", "exception", "warning"]
    for pattern in error_patterns:
        if pattern in response.text.lower():
            suspicious = True

    return suspicious


def main():
    parser = argparse.ArgumentParser(description="Simple HTTP Fuzzer")
    parser.add_argument("-u", "--url", required=True, help="Target URL with FUZZ keyword")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to payload wordlist")

    args = parser.parse_args()

    if "FUZZ" not in args.url:
        print(Fore.RED + "[!] URL must contain FUZZ keyword.")
        sys.exit(1)

    payloads = load_payloads(args.wordlist)

    print(Fore.CYAN + "[*] Getting baseline response...")
    baseline_response = send_request(args.url.replace("FUZZ", "test"))
    if not baseline_response:
        sys.exit(1)

    baseline_length = len(baseline_response.text)

    print(Fore.GREEN + f"[*] Baseline length: {baseline_length}")
    print(Fore.CYAN + "[*] Starting fuzzing...\n")

    for payload in payloads:
        fuzzed_url = args.url.replace("FUZZ", payload)
        response = send_request(fuzzed_url)

        if response:
            suspicious = analyze_response(response, baseline_length)

            if suspicious:
                print(Fore.RED + f"[!] Suspicious response for payload: {payload}")
                print(f"    Status: {response.status_code}")
                print(f"    Length: {len(response.text)}\n")
            else:
                print(Fore.GREEN + f"[OK] {payload} -> {response.status_code}")


if name == "__main__":
    main()
