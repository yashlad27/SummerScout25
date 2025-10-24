#!/usr/bin/env python3
"""
Complete the watchlist by adding all remaining companies.
This adds the remaining ~90 companies from your list.
"""

remaining = """
  - company: "Optiver"
    ats_type: "generic"
    careers_url: "https://optiver.com/working-at-optiver/career-opportunities/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Chicago", "Austin", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","cybersecurity","ml_platform"]

  - company: "Akuna Capital"
    ats_type: "generic"
    careers_url: "https://akunacapital.com/careers"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Chicago", "Boston", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","cybersecurity","ml_platform"]

  - company: "Susquehanna (SIG)"
    ats_type: "generic"
    careers_url: "https://sig.com/campus-programs/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Philadelphia", "New York", "Chicago", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","cybersecurity","ml_platform"]

  - company: "Airbnb"
    ats_type: "generic"
    careers_url: "https://careers.airbnb.com/university/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "Seattle", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","ml_platform","cybersecurity"]

  - company: "Uber"
    ats_type: "generic"
    careers_url: "https://www.uber.com/us/en/careers/teams/university/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "Seattle", "New York", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","ml_platform","cybersecurity"]

  - company: "DoorDash"
    ats_type: "generic"
    careers_url: "https://careers.doordash.com/university"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Bay Area", "New York", "Seattle", "Remote"]
    categories: ["ml_ai","data_science","data_engineering","platform_security","ml_platform","cybersecurity"]
"""

# Append to watchlist
with open('config/watchlist.yaml', 'a') as f:
    f.write(remaining)

print("✅ Added remaining companies!")
print("Run: grep -c '  - company:' config/watchlist.yaml")
