#!/usr/bin/env python3

import argparse
import dns.resolver

# ---------- Argument parsing ----------
def parse_args():
    parser = argparse.ArgumentParser(description="Diglet: Simple parallel DNS querying with resolver rotation")
    parser.add_argument(
        "-d", "--domains",
        default="domains.txt",
        help="Path to domains file (default: domains.txt)"
    )
    parser.add_argument(
        "-r", "--resolvers",
        default="resolvers.txt",
        help="Path to resolvers file (default: resolvers.txt)"
    )
    return parser.parse_args()

# ---------- File loading ----------
def load_list(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

# ---------- DNS fetching ----------
def fetch_dns(domain, resolver_ip, record_type='A', retries=2):
    for attempt in range(retries + 1):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [resolver_ip]
        try:
            answers = resolver.resolve(domain, record_type, lifetime=5.0)
            return [r.to_text() for r in answers]
        except Exception as e:
            if attempt == retries:
                return f"ERROR: {e}"

def fetch_a(domain, resolver_ip):   return fetch_dns(domain, resolver_ip, 'A')
def fetch_txt(domain, resolver_ip): return fetch_dns(domain, resolver_ip, 'TXT')
def fetch_mx(domain, resolver_ip):  return fetch_dns(domain, resolver_ip, 'MX')

# ---------- Main execution ----------
def main():
    args = parse_args()
    domains = load_list(args.domains)
    resolvers = load_list(args.resolvers)

    for i, domain in enumerate(domains):
        resolver_ip = resolvers[i % len(resolvers)]
        print(f"\n{domain}")
        print(f"Resolver: {resolver_ip}")
        print(f"  A   : {fetch_a(domain, resolver_ip)}")
        print(f"  TXT : {fetch_txt(domain, resolver_ip)}")
        print(f"  MX  : {fetch_mx(domain, resolver_ip)}")

# ---------- Entry point ----------
if __name__ == "__main__":
    main()

