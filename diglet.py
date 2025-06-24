#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import csv
import random
import dns.name
import dns.message
import dns.query
import dns.rdatatype
import dns.exception

# ---------- Argument parsing ----------
def parse_args():
    parser = argparse.ArgumentParser(description="Diglet: Simple parallel DNS querying with resolver rotation")
    parser.add_argument("-d", "--domains", default="domains.txt", help="Path to domains file (default: domains.txt)")
    parser.add_argument("-r", "--resolvers", default="resolvers.txt", help="Path to resolvers file (default: resolvers.txt)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output to stdout")
    parser.add_argument("-t", "--types", default="A", help="Comma-separated list of DNS record types to fetch (e.g., A,MX,TXT)")
    parser.add_argument("-w", "--workers", type=int, default=100, help="Number of concurrent workers (default: 100)")
    parser.add_argument("-o", "--output", choices=["csv"], help="Output format (csv)")
    return parser.parse_args()

# ---------- File loading ----------
def load_list(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

# ---------- DNS fetching ----------
def fetch_dns(domain, resolver_ip, record_type='A', timeout=10, retries=2):
    qname = dns.name.from_text(domain)
    qtype = dns.rdatatype.from_text(record_type)

    for attempt in range(retries + 1):
        try:
            request = dns.message.make_query(qname, qtype)
            response = dns.query.udp(request, resolver_ip, timeout=timeout)
            if response.answer:
                return [r.to_text() for rrset in response.answer for r in rrset]
            return []
        except Exception:
            if attempt == retries:
                return None  # fail indicator
    return None

# ---------- Fetchers ----------
def fetch_generic(domain, resolver_ip, rtype):
    return fetch_dns(domain, resolver_ip, rtype)

# ---------- Dynamic fetcher registry ----------
def get_fetchers():
    return {
        name.split("fetch_")[1].upper(): func
        for name, func in globals().items()
        if callable(func) and name.startswith("fetch_") and name != "fetch_dns"
    }

FETCHERS = {}  # unused in this version

# ---------- Resolver (Parallelized) ----------
def resolve_records(domains, resolvers, record_types, max_workers=100):
    def task(domain, rtype):
        tried = set()
        for _ in range(len(resolvers)):
            resolver_ip = random.choice(resolvers)
            if resolver_ip in tried:
                continue
            tried.add(resolver_ip)
            result = fetch_generic(domain, resolver_ip, rtype)
            if result is not None:
                return domain, rtype, result
        return domain, rtype, []  # fallback if all resolvers fail

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

# ---------- Printing ----------
def print_results(results, record_types):
    for r in results:
        print(f"\n{r['domain']}")
        for rtype in record_types:
            if rtype in r:
                print(f"  {rtype:<4}: {r[rtype]}")

# ---------- CSV Output ----------
def write_csv(results, record_types, filename="diglet_output.csv"):
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["domain"] + record_types)
        for r in results:
            row = [r["domain"]]
            for rtype in record_types:
                row.append("; ".join(r.get(rtype, [])))
            writer.writerow(row)

# ---------- Main execution ----------
def main():
    args = parse_args()
    domains = load_list(args.domains)
    resolvers = load_list(args.resolvers)
    record_types = [rtype.strip().upper() for rtype in args.types.split(",")]
    results = resolve_records(domains, resolvers, record_types, max_workers=args.workers)

    if args.output == "csv":
        write_csv(results, record_types)
    elif not args.quiet:
        print_results(results, record_types)

# ---------- Entry point ----------
if __name__ == "__main__":
    main()

