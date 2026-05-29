# Faviconner

A multithreaded favicon fingerprinting and web technology discovery tool.

Faviconner collects favicons from websites, calculates MurmurHash3 fingerprints compatible with Shodan-style favicon identification, and helps security researchers discover technologies, applications, and attack surface indicators across large target sets.

Unlike traditional favicon hash collectors, Faviconner can automatically discover custom favicon locations, identify known technologies, and export results in multiple formats.

> **Disclaimer:** Use this tool only against systems you own or are explicitly authorized to test.

---

# Overview

Many web applications expose unique favicon files that can be used to identify technologies, frameworks, management panels, and third-party products.

Faviconner automates the process of:

1. Locating favicon files.
2. Downloading favicon content.
3. Generating MurmurHash3 fingerprints.
4. Comparing hashes against known technologies.
5. Exporting results for reconnaissance and asset intelligence workflows.

---

# Why Favicon Fingerprinting?

Many platforms expose unique favicons.

Examples include:

* Jenkins
* Grafana
* Kibana
* GitLab
* Jira
* Confluence
* SonarQube
* Swagger UI
* WordPress
* phpMyAdmin

Even when:

* Page titles are hidden
* Login pages are protected
* Technology headers are removed
* Server banners are disabled

The favicon often remains unchanged.

---

# Features

### Multithreaded Scanning

* Concurrent processing
* Configurable worker pool
* Suitable for large target lists

### Automatic Favicon Discovery

Instead of relying only on:

```text id="xj1e5u"
/favicon.ico
```

Faviconner can parse HTML and discover:

```html id="b2r0ud"
<link rel="icon" href="/assets/favicon.png">
```

```html id="ofjg0m"
<link rel="shortcut icon" href="/img/favicon.ico">
```

```html id="u4x9x0"
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

---

### MurmurHash3 Generation

Generates hashes compatible with:

* Shodan
* FOFA
* ZoomEye
* Asset discovery tools

---

### Technology Detection

Built-in support for identifying known products using favicon fingerprints.

Examples:

* Jenkins
* GitLab
* Grafana
* Kibana
* Jira
* Confluence
* Swagger UI
* SonarQube
* WordPress

---

### Multiple Export Formats

Supported outputs:

* CSV
* JSON
* TXT

---

### Technology Filtering

Only display recognized technologies:

```bash id="6p20uh"
--only-matches
```

Useful for reducing noise during reconnaissance.

---

# Installation

Clone the repository:

```bash id="jlwm2n"
git clone https://github.com/yourusername/faviconner.git
cd faviconner
```

Install dependencies:

```bash id="2tl09w"
pip install -r requirements.txt
```

Or manually:

```bash id="zx9x8v"
pip install requests mmh3 beautifulsoup4
```

---

# Usage

## Scan a Single Target

```bash id="e92f3s"
python3 faviconner.py \
    -u https://example.com
```

---

## Scan Multiple Targets

```bash id="44evu4"
python3 faviconner.py \
    -i domains.txt
```

---

## Export Results

CSV:

```bash id="7mjxpw"
python3 faviconner.py \
    -i domains.txt \
    -o results.csv
```

JSON:

```bash id="d7d0d7"
python3 faviconner.py \
    -i domains.txt \
    -o results.json
```

TXT:

```bash id="5a9k7q"
python3 faviconner.py \
    -i domains.txt \
    -o results.txt
```

---

## Increase Scan Speed

```bash id="4crp9z"
python3 faviconner.py \
    -i domains.txt \
    -w 100
```

---

## Show Only Recognized Technologies

```bash id="8dkvfz"
python3 faviconner.py \
    -i domains.txt \
    --only-matches
```

---

## Disable Favicon Discovery

Only check:

```text id="z5l3cm"
/favicon.ico
```

```bash id="l7wtqa"
python3 faviconner.py \
    -i domains.txt \
    --no-discover
```

---

# Command Line Options

| Option            | Description                       |
| ----------------- | --------------------------------- |
| `-u`, `--url`     | Single target                     |
| `-i`, `--input`   | Input file                        |
| `-o`, `--output`  | Output file                       |
| `-w`, `--workers` | Worker threads                    |
| `-t`, `--timeout` | Request timeout                   |
| `--format`        | Force output format               |
| `--only-matches`  | Only show recognized technologies |
| `--no-discover`   | Disable HTML favicon discovery    |
| `--no-verify`     | Disable TLS verification          |

---

# Input File Format

One target per line:

```text id="hjzrmv"
https://example.com
https://app.example.com
https://portal.example.com
```

Comments are supported:

```text id="xwx79m"
# Production
https://app.example.com

# Staging
https://staging.example.com
```

---

# Example Output

CSV:

```csv id="cv79xz"
target,hash,tag
https://gitlab.example.com,-305179312,GitLab
https://grafana.example.com,-1200737715,Grafana
https://jenkins.example.com,-247388890,Jenkins
```

TXT:

```text id="b04l2j"
https://gitlab.example.com
Hash: -305179312
Technology: GitLab

https://grafana.example.com
Hash: -1200737715
Technology: Grafana
```

---

# Reconnaissance Workflow

Faviconner works particularly well after:

```text id="73w2u2"
Subdomain Enumeration
        │
        ▼
HTTP Verification
        │
        ▼
Faviconner
        │
        ▼
Technology Identification
        │
        ▼
Vulnerability Research
```

---

# Integration with Synex

Potential integrations:

* Fingerprint Engine
* Technology Detection
* Service Classification
* Asset Discovery
* Recon Automation
* Exposure Analysis

Example:

```text id="wwxt0n"
favicon hash
        │
        ▼
technology detected
        │
        ▼
associated CVEs
        │
        ▼
priority score
```

---

# Future Roadmap

Planned features:

* Screenshot collection
* Automatic favicon downloading
* HTML report generation
* PDF reporting
* FOFA query generation
* Shodan query generation
* ZoomEye query generation
* Custom fingerprint databases
* Technology confidence scoring
* Machine learning based clustering
* Integration with CVE databases

---

# Example Use Cases

### Bug Bounty

Quickly identify technologies across hundreds of subdomains.

### Attack Surface Management

Discover unexpected services and exposed applications.

### Penetration Testing

Improve reconnaissance and technology fingerprinting.

### Asset Intelligence

Map infrastructure and software exposure.

### Red Team Operations

Prioritize targets based on detected technologies.

---

# Author

Arthur Witt

Built for web reconnaissance, attack surface management, bug bounty hunting, penetration testing, and security research.

---

# License

This project is intended for educational purposes, research, and authorized security assessments only.
