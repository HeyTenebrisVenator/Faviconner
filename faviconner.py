#!/usr/bin/env python3
"""
faviconner.py

A multithreaded favicon fingerprinting tool.

Faviconner collects favicons from multiple targets, calculates MurmurHash3
hashes compatible with Shodan-style favicon fingerprinting, and optionally
tags known technologies based on favicon hashes.

Use only against systems you own or are authorized to test.
"""

import argparse
import base64
import csv
import json
import sys
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import mmh3
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


DEFAULT_TIMEOUT = 8
DEFAULT_WORKERS = 30

KNOWN_FAVICON_HASHES = {
    -247388890: "Jenkins",
    -305179312: "GitLab",
    1278323681: "Kibana",
    -1200737715: "Grafana",
    81586312: "Atlassian Jira",
    743365239: "Atlassian Confluence",
    -127886975: "phpMyAdmin",
    552727997: "SonarQube",
    116323821: "Swagger UI",
    -235701012: "WordPress",
}


@dataclass
class FaviconResult:
    target: str
    final_url: str
    favicon_url: str
    status: str
    hash: int | None
    tag: str
    content_type: str
    size_bytes: int
    error: str


def normalize_target(target: str) -> str:
    target = target.strip()

    if not target:
        return ""

    if target.startswith(("http://", "https://")):
        return target.rstrip("/")

    return f"https://{target.rstrip('/')}"


def load_targets(path: str) -> list[str]:
    targets = []

    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            target = line.strip()

            if not target or target.startswith("#"):
                continue

            targets.append(normalize_target(target))

    return list(dict.fromkeys(targets))


def get_base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def calculate_favicon_hash(content: bytes) -> int:
    encoded = base64.encodebytes(content)
    return mmh3.hash(encoded)


def discover_favicon_url(target: str, timeout: int, verify_tls: bool) -> str:
    default_favicon = urljoin(target + "/", "/favicon.ico")

    try:
        response = requests.get(
            target,
            timeout=timeout,
            verify=verify_tls,
            allow_redirects=True,
            headers={"User-Agent": "Faviconner/1.0"},
        )

        soup = BeautifulSoup(response.text, "html.parser")

        candidates = []

        for link in soup.find_all("link"):
            rel = " ".join(link.get("rel", [])).lower()
            href = link.get("href")

            if not href:
                continue

            if "icon" in rel:
                candidates.append(urljoin(response.url, href))

        if candidates:
            return candidates[0]

        return urljoin(get_base_url(response.url), "/favicon.ico")

    except RequestException:
        return default_favicon


def fetch_favicon(
    target: str,
    timeout: int,
    verify_tls: bool,
    discover: bool,
) -> FaviconResult:
    normalized_target = normalize_target(target)

    if not normalized_target:
        return FaviconResult(
            target=target,
            final_url="",
            favicon_url="",
            status="error",
            hash=None,
            tag="-",
            content_type="",
            size_bytes=0,
            error="empty target",
        )

    favicon_url = (
        discover_favicon_url(normalized_target, timeout, verify_tls)
        if discover
        else urljoin(normalized_target + "/", "/favicon.ico")
    )

    try:
        response = requests.get(
            favicon_url,
            timeout=timeout,
            verify=verify_tls,
            allow_redirects=True,
            headers={"User-Agent": "Faviconner/1.0"},
        )

        content_type = response.headers.get("Content-Type", "")
        content = response.content or b""

        if response.status_code != 200:
            return FaviconResult(
                target=normalized_target,
                final_url=response.url,
                favicon_url=favicon_url,
                status=f"http_{response.status_code}",
                hash=None,
                tag="-",
                content_type=content_type,
                size_bytes=len(content),
                error="favicon not found",
            )

        favicon_hash = calculate_favicon_hash(content)
        tag = KNOWN_FAVICON_HASHES.get(favicon_hash, "-")

        return FaviconResult(
            target=normalized_target,
            final_url=response.url,
            favicon_url=favicon_url,
            status="ok",
            hash=favicon_hash,
            tag=tag,
            content_type=content_type,
            size_bytes=len(content),
            error="",
        )

    except RequestException as error:
        return FaviconResult(
            target=normalized_target,
            final_url="",
            favicon_url=favicon_url,
            status="error",
            hash=None,
            tag="-",
            content_type="",
            size_bytes=0,
            error=str(error),
        )


def write_csv(results: list[FaviconResult], output: str) -> None:
    with open(output, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()

        for result in results:
            writer.writerow(asdict(result))


def write_json(results: list[FaviconResult], output: str) -> None:
    with open(output, "w", encoding="utf-8") as file:
        json.dump(
            [asdict(result) for result in results],
            file,
            indent=2,
            ensure_ascii=False,
        )


def write_txt(results: list[FaviconResult], output: str) -> None:
    with open(output, "w", encoding="utf-8") as file:
        for result in results:
            if result.hash is None:
                file.write(
                    f"{result.target} | ERROR | {result.status} | {result.error}\n"
                )
                continue

            file.write(
                f"{result.target} | hash={result.hash} | "
                f"tag={result.tag} | favicon={result.favicon_url}\n"
            )


def detect_output_format(output: str, forced_format: str | None) -> str:
    if forced_format:
        return forced_format

    if output.lower().endswith(".json"):
        return "json"

    if output.lower().endswith(".txt"):
        return "txt"

    return "csv"


def save_results(results: list[FaviconResult], output: str, output_format: str) -> None:
    if not results:
        return

    if output_format == "json":
        write_json(results, output)
    elif output_format == "txt":
        write_txt(results, output)
    else:
        write_csv(results, output)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Multithreaded favicon fingerprinting tool"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-u",
        "--url",
        help="Single target URL or domain",
    )

    group.add_argument(
        "-i",
        "--input",
        help="Input file containing targets, one per line",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="faviconner_results.csv",
        help="Output file path",
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json", "txt"],
        default=None,
        help="Force output format",
    )

    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="Number of worker threads",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="Request timeout in seconds",
    )

    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Disable TLS certificate verification",
    )

    parser.add_argument(
        "--no-discover",
        action="store_true",
        help="Do not parse HTML to discover custom favicon paths",
    )

    parser.add_argument(
        "--only-matches",
        action="store_true",
        help="Only save results that match a known favicon tag",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    targets = [normalize_target(args.url)] if args.url else load_targets(args.input)

    if not targets:
        print("[!] No valid targets provided.")
        sys.exit(1)

    output_format = detect_output_format(args.output, args.format)
    verify_tls = not args.no_verify
    discover = not args.no_discover

    print("[*] Faviconner started")
    print(f"[*] Targets: {len(targets)}")
    print(f"[*] Workers: {args.workers}")
    print(f"[*] Discover favicons: {discover}")
    print(f"[*] Output: {args.output}")
    print()

    results = []

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(
                fetch_favicon,
                target,
                args.timeout,
                verify_tls,
                discover,
            )
            for target in targets
        ]

        for future in as_completed(futures):
            result = future.result()

            if args.only_matches and result.tag == "-":
                continue

            results.append(result)

            if result.hash is not None:
                print(
                    f"[+] {result.target} -> hash={result.hash} tag={result.tag}"
                )
            else:
                print(
                    f"[!] {result.target} -> {result.status} {result.error}"
                )

    results.sort(key=lambda item: item.target)

    save_results(results, args.output, output_format)

    matched = sum(1 for result in results if result.tag != "-")

    print()
    print("[+] Scan completed")
    print(f"[+] Results: {len(results)}")
    print(f"[+] Known matches: {matched}")
    print(f"[+] Output saved to: {args.output}")


if __name__ == "__main__":
    main()
