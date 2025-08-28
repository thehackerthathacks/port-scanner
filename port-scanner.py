import socket
import concurrent.futures
import random
import re
import argparse
import colorama
from colorama import Fore, Style
import time
import math
import sys

colorama.init(autoreset=True)

def parse_proxies(proxy_input):
    if not proxy_input:
        return []
    return [p.strip() for p in proxy_input.split(',') if p.strip()]

def parse_ports(port_input):
    ports = []
    parts = port_input.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return sorted(set(ports))  # Remove duplicates and sort

def scan_port(target, port, proxies):
    if proxies:
        return scan_port_with_proxy(target, port, random.choice(proxies))
    else:
        return scan_port_direct(target, port)

def scan_port_direct(target, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        sock.close()
        return port if result == 0 else None
    except:
        return None

def scan_port_with_proxy(target, port, proxy):
    try:
        # Parse proxy: assume http://ip:port or ip:port
        proxy = proxy.replace('http://', '')
        proxy_host, proxy_port = proxy.split(':')
        proxy_port = int(proxy_port)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((proxy_host, proxy_port))
        
        connect_request = f"CONNECT {target}:{port} HTTP/1.1\r\nHost: {target}:{port}\r\n\r\n"
        sock.sendall(connect_request.encode())
        
        response = sock.recv(4096).decode()
        if '200 Connection established' in response:
            sock.close()
            return port
        else:
            sock.close()
            return None
    except:
        return None

def main():
    parser = argparse.ArgumentParser(description="Port Scanner with optional proxies and colored output.")
    parser.add_argument('--target', required=True, help='The IP or hostname to scan.')
    parser.add_argument('--proxies', help='Comma-separated list of proxies (e.g., http://proxy1:8080,http://proxy2:8080). Optional.')
    parser.add_argument('--all', action='store_true', help='Scan all ports (1-65535).')
    parser.add_argument('--ports', help='Custom ports or ranges (e.g., 80,443 or 1-100,8080).')

    args = parser.parse_args()

    if not args.all and not args.ports:
        parser.error("You must specify either --all or --ports.")

    target = args.target.strip()
    proxies = parse_proxies(args.proxies) if args.proxies else []

    if args.all:
        ports_to_scan = list(range(1, 65536))
    else:
        ports_to_scan = parse_ports(args.ports)

    max_workers = 100
    timeout = 2 if proxies else 1
    estimated_seconds = math.ceil(len(ports_to_scan) / max_workers) * timeout
    estimated_minutes = estimated_seconds / 60

    print(f"Scanning {Fore.CYAN}{target}{Style.RESET_ALL} for open ports...")
    if proxies:
        print(f"Using proxies: {Fore.YELLOW}{', '.join(proxies)}{Style.RESET_ALL}")
    print(f"Estimated time to complete: {Fore.YELLOW}{estimated_minutes:.2f} minutes{Style.RESET_ALL} (conservative estimate based on parallel scanning)")

    open_ports = []
    start_time = time.time()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_port = {executor.submit(scan_port, target, port, proxies): port for port in ports_to_scan}
            for future in concurrent.futures.as_completed(future_to_port):
                result = future.result()
                if result:
                    open_ports.append(result)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Scan interrupted by user.{Style.RESET_ALL}")
        executor.shutdown(wait=False)
        duration = time.time() - start_time
        if open_ports:
            print(f"{Fore.GREEN}Open ports found so far:{Style.RESET_ALL}")
            for port in sorted(open_ports):
                print(f"{Fore.GREEN}Port {port}: Open{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}No open ports found so far.{Style.RESET_ALL}")
        print(f"Partial scan duration: {duration:.2f} seconds")
        sys.exit(0)

    duration = time.time() - start_time

    if open_ports:
        print(f"{Fore.GREEN}Open ports:{Style.RESET_ALL}")
        for port in sorted(open_ports):
            print(f"{Fore.GREEN}Port {port}: Open{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}No open ports found.{Style.RESET_ALL}")

    print(f"Scan completed in {duration:.2f} seconds")

if __name__ == "__main__":
    main()
