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
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress output to stdout"
    )
    parser.add_argument(
        "-t", "--types",
        default="A",
        help="Comma-separated list of DNS record types to fetch (e.g., A,MX,TXT)",
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
            answers = resolver.resolve(domain, record_type, raise_on_no_answer=False, lifetime=5.0)
            return [r.to_text() for r in answers] if answers.rrset else []
        except Exception:
            if attempt == retries:
                return []

def fetch_a(domain, resolver_ip):           return fetch_dns(domain, resolver_ip, 'A')
def fetch_aaaa(domain, resolver_ip):        return fetch_dns(domain, resolver_ip, 'AAAA')
def fetch_afsdb(domain, resolver_ip):       return fetch_dns(domain, resolver_ip, 'AFSDB')
def fetch_apl(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'APL')
def fetch_caa(domain, resolver_ip):         return fetch_dns(domain, resolver_ip, 'CAA')
def fetch_cdnskey(domain, resolver_ip):     return fetch_dns(domain, resolver_ip, 'CDNSKEY')
def fetch_cdnskey(domain, resolver_ip):     return fetch_dns(domain, resolver_ip, 'CDNSKEY')
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

def resolve_records(domains, resolvers, record_types):
    for i, domain in enumerate(domains):
        resolver_ip = resolvers[i % len(resolvers)]
        record = {
            "domain": domain,
            "resolver": resolver_ip,
        }
        if "A" in record_types:
            record["A"] = fetch_a(domain, resolver_ip)
        if "AAAA" in record_types:
            record["AAAA"] = fetch_aaaa(domain, resolver_ip)
        if "AFSDB" in record_types:
            record["AFSDB"] = fetch_afsdb(domain, resolver_ip)
        if "APL" in record_types:
            record["APL"] = fetch_apl(domain, resolver_ip)
        if "CAA" in record_types:
            record["CAA"] = fetch_caa(domain, resolver_ip)
        if "CDNSKEY" in record_types:
            record["CDNSKEY"] = fetch_cdnskey(domain, resolver_ip)
        if "CDS" in record_types:
            record["CDS"] = fetch_cds(domain, resolver_ip)
        if "CERT" in record_types:
            record["CERT"] = fetch_cert(domain, resolver_ip)
        if "CNAME" in record_types:
            record["CNAME"] = fetch_cname(domain, resolver_ip)
        if "DHCID" in record_types:
            record["DHCID"] = fetch_dhcid(domain, resolver_ip)
        if "DLV" in record_types:
            record["DLV"] = fetch_dlv(domain, resolver_ip)
        if "DNAME" in record_types:
            record["DNAME"] = fetch_dname(domain, resolver_ip)
        if "DNSKEY" in record_types:
            record["DNSKEY"] = fetch_dnskey(domain, resolver_ip)
        if "DS" in record_types:
            record["DS"] = fetch_ds(domain, resolver_ip)
        if "HIP" in record_types:
            record["HIP"] = fetch_hip(domain, resolver_ip)
        if "IPSECKEY" in record_types:
            record["IPSECKEY"] = fetch_ipseckey(domain, resolver_ip)
        if "KEY" in record_types:
            record["KEY"] = fetch_key(domain, resolver_ip)
        if "KX" in record_types:
            record["KX"] = fetch_kx(domain, resolver_ip)
        if "LOC" in record_types:
            record["LOC"] = fetch_loc(domain, resolver_ip)
        if "MX" in record_types:
            record["MX"] = fetch_mx(domain, resolver_ip)
        if "NAPTR" in record_types:
            record["NAPTR"] = fetch_naptr(domain, resolver_ip)
        if "NS" in record_types:
            record["NS"] = fetch_ns(domain, resolver_ip)
        if "NSEC" in record_types:
            record["NSEC"] = fetch_nsec(domain, resolver_ip)
        if "NSEC3" in record_types:
            record["NSEC3"] = fetch_nsec3(domain, resolver_ip)
        if "NSEC3PARAM" in record_types:
            record["NSEC3PARAM"] = fetch_nsec3param(domain, resolver_ip)
        if "PTR" in record_types:
            record["PTR"] = fetch_ptr(domain, resolver_ip)
        if "RP" in record_types:
            record["RP"] = fetch_rp(domain, resolver_ip)
        if "RRSIG" in record_types:
            record["RRSIG"] = fetch_rrsig(domain, resolver_ip)
        if "SIG" in record_types:
            record["SIG"] = fetch_sig(domain, resolver_ip)
        if "SOA" in record_types:
            record["SOA"] = fetch_soa(domain, resolver_ip)
        if "SRV" in record_types:
            record["SRV"] = fetch_srv(domain, resolver_ip)
        if "SSHFP" in record_types:
            record["SSHFP"] = fetch_sshfp(domain, resolver_ip)
        if "TLSA" in record_types:
            record["TLSA"] = fetch_tlsa(domain, resolver_ip)
        if "TSIG" in record_types:
            record["TSIG"] = fetch_tsig(domain, resolver_ip)
        if "TXT" in record_types:
            record["TXT"] = fetch_txt(domain, resolver_ip)
        if "URI" in record_types:
            record["URI"] = fetch_uri(domain, resolver_ip)
        if "ZONEMD" in record_types:
            record["ZONEMD"] = fetch_zonemd(domain, resolver_ip)
        yield record

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
    results = resolve_records(domains, resolvers, record_types)
    if not args.quiet:
        print_results(results, record_types)

# ---------- Entry point ----------
if __name__ == "__main__":
    main()

