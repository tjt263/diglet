#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
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
    return parser.parse_args()

# ---------- File loading ----------
def load_list(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

# ---------- DNS fetching ----------
def fetch_dns(domain, resolver_ip, record_type='A', retries=2):
    qname = dns.name.from_text(domain)
    qtype = dns.rdatatype.from_text(record_type)

    for attempt in range(retries + 1):
        try:
            request = dns.message.make_query(qname, qtype)
            response = dns.query.udp(request, resolver_ip, timeout=5)
            if response.answer:
                return [r.to_text() for rrset in response.answer for r in rrset]
            return []
        except Exception:
            if attempt == retries:
                return []

# ---------- Fetchers ----------
def fetch_a(domain, resolver_ip):           return fetch_dns(domain, resolver_ip, 'A')
def fetch_aaaa(domain, resolver_ip):        return fetch_dns(domain, resolver_ip, 'AAAA')
def fetch_afsdb(domain, resolver_ip):       return fetch_dns(domain, resolver_ip, 'AFSDB')
def fetch_apl(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'APL')
def fetch_caa(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'CAA')
def fetch_cdnskey(domain, resolver_ip):     return fetch_dns(domain, resolver_ip, 'CDNSKEY')
def fetch_cds(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'CDS')
def fetch_cert(domain, resolver_ip):        return fetch_dns(domain, resolver_ip, 'CERT')
def fetch_cname(domain, resolver_ip):       return fetch_dns(domain, resolver_ip, 'CNAME')
def fetch_dhcid(domain, resolver_ip):       return fetch_dns(domain, resolver_ip, 'DHCID')
def fetch_dlv(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'DLV')
def fetch_dname(domain, resolver_ip):       return fetch_dns(domain, resolver_ip, 'DNAME')
def fetch_dnskey(domain, resolver_ip):      return fetch_dns(domain, resolver_ip, 'DNSKEY')
def fetch_ds(domain, resolver_ip):          return fetch_dns(domain, resolver_ip, 'DS')
def fetch_hip(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'HIP')
def fetch_ipseckey(domain, resolver_ip):    return fetch_dns(domain, resolver_ip, 'IPSECKEY')
def fetch_key(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'KEY')
def fetch_kx(domain, resolver_ip):          return fetch_dns(domain, resolver_ip, 'KX')
def fetch_loc(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'LOC')
def fetch_mx(domain, resolver_ip):          return fetch_dns(domain, resolver_ip, 'MX')
def fetch_naptr(domain, resolver_ip):       return fetch_dns(domain, resolver_ip, 'NAPTR')
def fetch_ns(domain, resolver_ip):          return fetch_dns(domain, resolver_ip, 'NS')
def fetch_nsec(domain, resolver_ip):        return fetch_dns(domain, resolver_ip, 'NSEC')
def fetch_nsec3(domain, resolver_ip):       return fetch_dns(domain, resolver_ip, 'NSEC3')
def fetch_nsec3param(domain, resolver_ip):  return fetch_dns(domain, resolver_ip, 'NSEC3PARAM')
def fetch_ptr(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'PTR')
def fetch_rp(domain, resolver_ip):          return fetch_dns(domain, resolver_ip, 'RP')
def fetch_rrsig(domain, resolver_ip):       return fetch_dns(domain, resolver_ip, 'RRSIG')
def fetch_sig(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'SIG')
def fetch_soa(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'SOA')
def fetch_srv(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'SRV')
def fetch_sshfp(domain, resolver_ip):       return fetch_dns(domain, resolver_ip, 'SSHFP')
def fetch_tlsa(domain, resolver_ip):        return fetch_dns(domain, resolver_ip, 'TLSA')
def fetch_tsig(domain, resolver_ip):        return fetch_dns(domain, resolver_ip, 'TSIG')
def fetch_txt(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'TXT')
def fetch_uri(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'URI')
def fetch_zonemd(domain, resolver_ip):      return fetch_dns(domain, resolver_ip, 'ZONEMD')

# ---------- Dynamic fetcher registry ----------
def get_fetchers():
    return {
        name.split("fetch_")[1].upper(): func
        for name, func in globals().items()
        if callable(func) and name.startswith("fetch_") and name != "fetch_dns"
    }

FETCHERS = get_fetchers()

# ---------- Resolver (Parallelized) ----------
def resolve_records(domains, resolvers, record_types, max_workers=100):
    def task(domain, resolver_ip, rtype):
        fetch_func = FETCHERS.get(rtype)
        if fetch_func:
            return domain, resolver_ip, rtype, fetch_func(domain, resolver_ip)
        return domain, resolver_ip, rtype, []

    jobs = []
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, domain in enumerate(domains):
            resolver_ip = resolvers[i % len(resolvers)]
            for rtype in record_types:
                jobs.append(executor.submit(task, domain, resolver_ip, rtype))

        for future in as_completed(jobs):
            domain, resolver, rtype, result = future.result()
            if domain not in results:
                results[domain] = {"domain": domain, "resolver": resolver}
            results[domain][rtype] = result

    return list(results.values())

# ---------- Printing ----------
def print_results(results, record_types):
    for r in results:
        print(f"\n{r['domain']}")
        print(f"Resolver: {r['resolver']}")
        for rtype in record_types:
            if rtype in r:
                print(f"  {rtype:<4}: {r[rtype]}")

# ---------- Main execution ----------
def main():
    args = parse_args()
    domains = load_list(args.domains)
    resolvers = load_list(args.resolvers)
    record_types = [rtype.strip().upper() for rtype in args.types.split(",")]
    results = resolve_records(domains, resolvers, record_types, max_workers=args.workers)
    if not args.quiet:
        print_results(results, record_types)

# ---------- Entry point ----------
if __name__ == "__main__":
    main()

