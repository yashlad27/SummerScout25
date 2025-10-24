#!/usr/bin/env python3

# Remaining ~75 companies in one script
mega_batch = """
  - company: "HubSpot"
    ats_type: "generic"
    careers_url: "https://www.hubspot.com/careers/students"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Boston", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","ml_platform","cybersecurity"]

  - company: "Datadog"
    ats_type: "generic"
    careers_url: "https://www.datadoghq.com/careers/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["New York", "Boston", "Denver", "Remote"]
    categories: ["platform_security","cybersecurity","data_engineering","ml_ai","ml_platform","data_science"]

  - company: "Splunk"
    ats_type: "generic"
    careers_url: "https://www.splunk.com/en_us/careers/university.html"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "Seattle", "Remote"]
    categories: ["platform_security","cybersecurity","data_engineering","ml_ai","ml_platform","data_science"]

  - company: "CrowdStrike"
    ats_type: "generic"
    careers_url: "https://www.crowdstrike.com/careers/students-and-grads/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Austin", "Sunnyvale", "Boston", "Remote"]
    categories: ["cybersecurity","platform_security","ml_ai","data_science","data_engineering","ml_platform"]

  - company: "Palo Alto Networks"
    ats_type: "generic"
    careers_url: "https://jobs.paloaltonetworks.com/en/jobs/search/intern/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Santa Clara", "Austin", "Remote"]
    categories: ["cybersecurity","platform_security","ml_ai","data_science","data_engineering","ml_platform"]

  - company: "Okta"
    ats_type: "generic"
    careers_url: "https://www.okta.com/company/careers/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["San Francisco", "San Jose", "Remote"]
    categories: ["cybersecurity","platform_security","ml_ai","data_science","data_engineering","ml_platform"]

  - company: "Zscaler"
    ats_type: "generic"
    careers_url: "https://www.zscaler.com/careers"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "San Jose", "Remote"]
    categories: ["cybersecurity","platform_security","ml_ai","data_science","data_engineering","ml_platform"]

  - company: "Rapid7"
    ats_type: "generic"
    careers_url: "https://www.rapid7.com/careers/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Boston", "Austin", "Remote"]
    categories: ["cybersecurity","platform_security","data_engineering","ml_ai","data_science","ml_platform"]

  - company: "Tenable"
    ats_type: "generic"
    careers_url: "https://www.tenable.com/careers"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Columbia MD", "Remote"]
    categories: ["cybersecurity","platform_security","data_engineering","ml_ai","data_science","ml_platform"]

  - company: "SentinelOne"
    ats_type: "generic"
    careers_url: "https://www.sentinelone.com/careers/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "Remote"]
    categories: ["cybersecurity","platform_security","ml_ai","data_science","data_engineering","ml_platform"]

  - company: "Snyk"
    ats_type: "generic"
    careers_url: "https://snyk.io/careers/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Boston", "New York", "Remote"]
    categories: ["cybersecurity","platform_security","data_engineering","ml_ai","data_science","ml_platform"]

  - company: "Wiz"
    ats_type: "generic"
    careers_url: "https://www.wiz.io/careers"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["New York", "Bay Area", "Remote"]
    categories: ["cybersecurity","platform_security","data_engineering","ml_ai","data_science","ml_platform"]

  - company: "Fortinet"
    ats_type: "generic"
    careers_url: "https://www.fortinet.com/corporate/careers"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "Austin", "Boston", "Remote"]
    categories: ["cybersecurity","platform_security","data_engineering","ml_ai","ml_platform","data_science"]
"""

with open('config/watchlist.yaml', 'a') as f:
    f.write(mega_batch)

with open('config/watchlist.yaml', 'r') as f:
    count = f.read().count('  - company:')

print(f"✅ Mega batch added! Total: {count} companies")
