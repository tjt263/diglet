#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import csv
import dns.name
import dns.message
import dns.query
import dns.rdatatype
import dns.rcode
import socket

def parse_args():
    parser = argparse.ArgumentParser(description="Diglet: Parallel DNS querying with resolver rotation and retry logic")
    parser.add_argument("-d", "--domains", default="domains.txt", help="Path to domains file (default: domains.txt)")
    parser.add_argument("-r", "--resolvers", default="resolvers.txt", help="Path to resolvers file (default: resolvers.txt)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output to stdout")
    parser.add_argument("-t", "--types", default="A", help="Comma-separated list of DNS record types to fetch (e.g., A,MX,TXT)")
    parser.add_argument("-w", "--workers", type=int, default=100, help="Number of concurrent workers (default: 100)")
    parser.add_argument("-o", "--output", help="CSV output file path")
    return parser.parse_args()

def load_list(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

def fetch_dns(domain, resolver_ip, record_type='A', timeout=10):
    qname = dns.name.from_text(domain)
    qtype = dns.rdatatype.from_text(record_type)
    try:
        request = dns.message.make_query(qname, qtype)
        response = dns.query.udp(request, resolver_ip, timeout=timeout)
        if response.rcode() == dns.rcode.NXDOMAIN:
            return 'NXDOMAIN'
        if response.answer:
            return [r.to_text() for rrset in response.answer for r in rrset]
        return []
    except (dns.exception.Timeout, dns.exception.DNSException, socket.error):
        return None

def resolve_records(domains, resolvers, record_types, max_workers=100, max_retries=10):
    def task(domain, rtype):
        attempts = 0
        for resolver_ip in resolvers:
            result = fetch_dns(domain, resolver_ip, rtype)
            if result == 'NXDOMAIN':
                return domain, rtype, []  # stop retrying
            if result is not None:
                return domain, rtype, result  # successful fetch or empty (no retry)
            attempts += 1
            if attempts >= max_retries:
                break
        return domain, rtype, []  # all attempts failed

    jobs = []
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for domain in domains:
            for rtype in record_types:
                jobs.append(executor.submit(task, domain, rtype))

        for future in as_completed(jobs):
            domain, rtype, result = future.result()
            if domain not in results:
                results[domain] = {"domain": domain}
            results[domain][rtype] = result

    return list(results.values())

def print_results(results, record_types):
    for r in results:
        print(f"\n{r['domain']}")
        for rtype in record_types:
            if rtype in r:
                print(f"  {rtype:<4}: {r[rtype]}")

def write_csv(results, record_types, filename="diglet_output.csv"):
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["domain"] + record_types)
        for r in results:
            row = [r["domain"]]
            for rtype in record_types:
                row.append("; ".join(r.get(rtype, [])))
            writer.writerow(row)

def main():
    args = parse_args()
    domains = load_list(args.domains)
    resolvers = load_list(args.resolvers)
    record_types = [rtype.strip().upper() for rtype in args.types.split(",")]
    results = resolve_records(domains, resolvers, record_types, max_workers=args.workers)

    if args.output:
        write_csv(results, record_types, filename=args.output)
    elif not args.quiet:
        print_results(results, record_types)

if __name__ == "__main__":
    main()

