"""
A CLI tool to check that the DNS records of the subdomains are correctly configured.
Prints the subdomains that do not point to the correct IP addresses.
Instruct the user to fix the DNS records with a step-by-step guide.
"""
from pathlib import Path
from dataclasses import dataclass
from typing import List
import dns.resolver
import argparse
import yaml
from enum import Enum
from itertools import chain

TARGET_HOSTNAME = "jokeri.ayy.fi"


def load_subdomains():
    """
    Load the subdomains from subdomains/*.yaml.
    """
    subdomains = []
    for subdomain_file in chain(
        Path("subdomains").glob("*.yaml"), Path("subdomains").glob("*.yml")
    ):
        with open(subdomain_file, "r") as f:
            entry = yaml.safe_load(f)
            for _, value in entry.items():
                subdomains.extend(value["redirect_from"])

    return subdomains


class FailReasons(Enum):
    """
    The reasons why the DNS check failed.
    """

    NXDOMAIN = "NXDOMAIN"
    INCORRECT_IPv4 = "INCORRECT_IPv4"
    INCORRECT_IPv6 = "INCORRECT_IPv6"
    NOANSWER = "NO_ANSWER"


@dataclass
class CheckResult:
    """
    The result of a DNS check.
    """

    domain: str
    ipv4: bool
    ipv6: bool
    fails: List[FailReasons]


def check_dns_record(
    domain: str, target_ipv4_address: str, target_ipv6_address: str
) -> CheckResult:
    """
    Check if the DNS record for a given domain matches the specified IPv4 and IPv6 addresses.

    Args:
        domain (str): The domain to check.
        target_ipv4_address (str): The expected IPv4 address for the domain.
        target_ipv6_address (str): The expected IPv6 address for the domain.

    Returns:
        CheckResult: A dataclass containing the results of the DNS check.
            The dataclass contains the following fields:
            - domain (str): The domain that was checked.
            - ipv4_success (bool): True if the IPv4 address matched, False otherwise.
            - ipv6_success (bool): True if the IPv6 address matched, False otherwise.
            - fails (list): A list of FailReasons if the check failed, empty otherwise.
    """
    fails = []
    ipv4_success = False
    ipv6_success = False
    try:
        # Check IPv4 address
        answers = dns.resolver.query(domain, "A")
        if answers[0] != target_ipv4_address[0]:
            fails.append(FailReasons.INCORRECT_IPv4)
        else:
            ipv4_success = True
        # Check IPv6 address
        answers = dns.resolver.query(domain, "AAAA")
        if answers[0] != target_ipv6_address[0]:
            fails.append(FailReasons.INCORRECT_IPv6)
        else:
            ipv6_success = True
    except dns.resolver.NXDOMAIN:
        return CheckResult(domain, False, False, [FailReasons.NXDOMAIN])
    except dns.resolver.NoAnswer:
        return CheckResult(domain, False, False, [FailReasons.NOANSWER])

    return CheckResult(domain, ipv4_success, ipv6_success, fails)


def print_fix_instructions(
    fails: List[CheckResult],
    target_cname: str,
    target_a_record: str,
    target_aaaa_record: str,
):
    """
    Print instructions on how to fix the DNS records of a subdomain.
    """
    print("Fix instructions:")
    for fail in fails:
        print(f"  - {fail.domain}")
        if FailReasons.NXDOMAIN in fail.fails:
            print(
                f"    - Create a CNAME record for {fail.domain} that points to {target_cname}"
            )
        if FailReasons.INCORRECT_IPv4 in fail.fails:
            print(
                f"    - Change {fail.domain} to point to {TARGET_HOSTNAME} (ipv4)"
            )
        if FailReasons.INCORRECT_IPv6 in fail.fails:
            print(
                f"    - Change {fail.domain} to point to {TARGET_HOSTNAME} (ipv6)"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check that the DNS records of the subdomains are correctly configured."
    )

    target_ipv4_address = dns.resolver.query(TARGET_HOSTNAME, "A")
    target_ipv6_address = dns.resolver.query(TARGET_HOSTNAME, "AAAA")

    # Print the target IP addressess
    print(f"Target IPv4 address: {target_ipv4_address[0]}")
    print(f"Target IPv6 address: {target_ipv6_address[0]}")

    subdomains = load_subdomains()
    results = []  # type: List[CheckResult]
    for subdomain in subdomains:
        results.append(
            check_dns_record(subdomain, target_ipv4_address, target_ipv6_address)
        )
    print_fix_instructions(
        results, TARGET_HOSTNAME, target_ipv4_address, target_ipv6_address
    )
