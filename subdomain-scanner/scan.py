import requests
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, init

init(autoreset=True)

lock = threading.Lock()


def load_wordlist(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        print(Fore.RED + "[!] Wordlist not found.")
        exit(1)


def build_proxies(proxy):
    if proxy:
        return {
            "http": proxy,
            "https": proxy
        }
    return None


def check_subdomain(subdomain, args, proxies, log_file):
    url = f"http://{subdomain}"

    try:
        response = requests.get(
            url,
            timeout=3,
            proxies=proxies,
            allow_redirects=True
        )

        output = f"{subdomain} -> {response.status_code}"

        with lock:
            print(Fore.GREEN + "[FOUND] " + output)
            if log_file:
                log_file.write(output + "\n")

    except requests.RequestException:
        pass


def main():
    parser = argparse.ArgumentParser(description="Multithreaded Subdomain Scanner")
    parser.add_argument("-d", "--domain", required=True, help="Target domain (example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Wordlist path")
    parser.add_argument("-t", "--threads", type=int, default=10)
    parser.add_argument("--proxy", help="Proxy (example: http://127.0.0.1:8080)")
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()

    subdomains = load_wordlist(args.wordlist)
    proxies = build_proxies(args.proxy)
    log_file = open(args.output, "w") if args.output else None

    print(Fore.CYAN + f"[*] Scanning {args.domain} with {args.threads} threads...\n")

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for sub in subdomains:
            full_domain = f"{sub}.{args.domain}"
            executor.submit(
                check_subdomain,
                full_domain,
                args,
                proxies,
                log_file
            )

    if log_file:
        log_file.close()

    print(Fore.CYAN + "\n[*] Scan completed.")


if name == "__main__":
    main()
