#!/bin/bash
# Script to append all remaining companies to watchlist

cd /Users/yashlad/Development/linkedin_job_scrapper

# Count current companies
current_count=$(grep -c "^  - company:" config/watchlist.yaml)
echo "Current companies in watchlist: $current_count"

# Append remaining companies in batches
# Due to file size, appending the provided YAML directly

cat >> config/watchlist.yaml << 'COMPANIES'

  - company: "PayPal"
    ats_type: "generic"
    careers_url: "https://www.paypal.com/us/webapps/mpp/jobs/interns-and-grads"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "Austin", "New York", "Remote"]
    categories: ["data_engineering","ml_ai","data_science","cybersecurity","platform_security","ml_platform"]

  - company: "Robinhood"
    ats_type: "generic"
    careers_url: "https://careers.robinhood.com/openings/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Menlo Park", "New York", "Seattle", "Remote"]
    categories: ["data_engineering","ml_ai","data_science","cybersecurity","ml_platform","platform_security"]

  - company: "Bloomberg"
    ats_type: "generic"
    careers_url: "https://www.bloomberg.com/careers/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["New York", "Princeton", "San Francisco", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","cybersecurity","ml_platform","platform_security"]

  - company: "Capital One"
    ats_type: "generic"
    careers_url: "https://www.capitalonecareers.com/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["McLean", "New York", "Richmond", "Remote"]
    categories: ["data_engineering","data_science","ml_ai","cybersecurity","platform_security","ml_platform"]

  - company: "JPMorgan Chase"
    ats_type: "generic"
    careers_url: "https://careers.jpmorgan.com/us/en/students/programs"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["New York", "Chicago", "Columbus", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","cybersecurity","platform_security","ml_platform"]

  - company: "Goldman Sachs"
    ats_type: "generic"
    careers_url: "https://www.goldmansachs.com/careers/students/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["New York", "Dallas", "Salt Lake City", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","cybersecurity","platform_security","ml_platform"]

  - company: "Morgan Stanley"
    ats_type: "generic"
    careers_url: "https://www.morganstanley.com/careers/campus"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["New York", "Montreal", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","cybersecurity","platform_security","ml_platform"]

  - company: "Jump Trading"
    ats_type: "generic"
    careers_url: "https://www.jumptrading.com/careers/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Chicago", "New York", "Austin", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","cybersecurity","ml_platform"]

  - company: "DRW"
    ats_type: "generic"
    careers_url: "https://drw.com/work-at-drw/careers/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Chicago", "Austin", "New York", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","cybersecurity","ml_platform"]

  - company: "IMC Trading"
    ats_type: "generic"
    careers_url: "https://careers.imc.com/us/en/students-and-graduates"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Chicago", "New York", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","cybersecurity","ml_platform"]
COMPANIES

echo "Added more companies..."
chmod +x append_all_companies.sh
