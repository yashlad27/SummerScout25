#!/usr/bin/env python3
"""Script to add new companies to watchlist.yaml"""

import yaml

# Read existing watchlist
with open('config/watchlist.yaml', 'r') as f:
    data = yaml.safe_load(f)

# New companies to add
new_companies = """
  - company: "Amazon"
    ats_type: "generic"
    careers_url: "https://www.amazon.jobs/en/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Seattle", "Bay Area", "Boston", "New York", "Austin", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","cybersecurity","ml_platform","platform_security"]

  - company: "Meta"
    ats_type: "generic"
    careers_url: "https://www.metacareers.com/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "Seattle", "New York", "Boston", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","cybersecurity","ml_platform","platform_security"]

  - company: "Apple"
    ats_type: "generic"
    careers_url: "https://jobs.apple.com/en-us/search?team=internships"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Cupertino", "Seattle", "Austin", "Boston", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","cybersecurity","ml_platform","platform_security"]

  - company: "NVIDIA"
    ats_type: "generic"
    careers_url: "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "Seattle", "Austin", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","cybersecurity","ml_platform","platform_security"]

  - company: "Databricks"
    ats_type: "generic"
    careers_url: "https://www.databricks.com/company/careers/open-positions"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "Seattle", "New York", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","ml_platform","platform_security","cybersecurity"]
"""

# Parse the YAML string with new companies
new_targets = yaml.safe_load(new_companies)

# Add to existing targets
if 'targets' not in data:
    data['targets'] = []
    
data['targets'].extend(new_targets)

# Write back
with open('config/watchlist.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

print(f"✅ Added {len(new_targets)} new companies!")
print(f"Total companies in watchlist: {len(data['targets'])}")
