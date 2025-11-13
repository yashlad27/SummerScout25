#!/usr/bin/env python3
"""
Analyze scraper failure logs to identify patterns and root causes.
"""

import re
from collections import defaultdict, Counter
from pathlib import Path

# Parse the user's log output
LOG_DATA = """
# Extract all ERROR lines from the user's logs
"""

def analyze_log_file(log_text: str):
    """Analyze log text for failures."""
    
    failures = {
        'lever_404': [],
        'greenhouse_404': [],
        'dns_errors': [],
        'timeouts': [],
        'no_jobs': [],
        'other_errors': []
    }
    
    # Patterns
    lever_pattern = r'ERROR - Failed to fetch Lever jobs for (.+?): 404'
    greenhouse_pattern = r'ERROR - Failed to fetch Greenhouse jobs for (.+?): 404'
    dns_pattern = r'ERROR - Failed to fetch jobs for (.+?): Page\.goto: net::ERR_NAME_NOT_RESOLVED'
    timeout_pattern = r'ERROR - Timeout loading .+ for (.+?)$'
    
    for line in log_text.split('\n'):
        if 'ERROR' in line:
            # Lever 404
            match = re.search(lever_pattern, line)
            if match:
                failures['lever_404'].append(match.group(1))
                continue
            
            # Greenhouse 404
            match = re.search(greenhouse_pattern, line)
            if match:
                failures['greenhouse_404'].append(match.group(1))
                continue
            
            # DNS errors
            match = re.search(dns_pattern, line)
            if match:
                failures['dns_errors'].append(match.group(1))
                continue
            
            # Timeouts
            match = re.search(timeout_pattern, line)
            if match:
                failures['timeouts'].append(match.group(1))
                continue
    
    return failures

def create_failure_report():
    """Create comprehensive failure analysis report."""
    
    # From the user's logs
    failures_found = {
        'lever_404': [
            'Radix Trading', 'DataVisor', 'Castle', 'Modern Treasury', 'Lithic',
            'Unit', 'Bolt', 'IronNet Cybersecurity', 'Jeeves', 'Rho',
            'Mercado Libre', 'TRM Labs', 'Trulioo', 'Veriff', 'Sardine',
            'Sezzle', 'Zip', 'Upgrade', 'Avant', 'Dave', 'Current', 'Albert'
        ],
        'greenhouse_404': [
            'Sift', 'Signifyd', 'Socure', 'Checkout.com', 'Chargebee', 'Recurly',
            'Rapyd', 'Wise', 'Remitly', 'Tipalti', 'ReliaQuest', 'Armis',
            'Claroty', 'ExtraHop', 'Illumio', 'Aqua Security', 'Sysdig', 'Intuit',
            'Box', 'Alteryx', 'ThoughtSpot', 'Alation', 'Immuta', 'Etsy',
            'Chainalysis', 'Elliptic', 'Lemonade', 'Root Insurance',
            'Hippo Insurance', 'Next Insurance', 'Onfido', 'Klarna', 'Varo', 'LendingClub'
        ],
        'dns_errors': ['GTS', 'BNP Paribas', 'American Express', 'Synchrony'],
        'timeouts': ['Zuora', 'Nuvei', 'Barclays', 'Oracle', 'VMware', 'Workday']
    }
    
    print("=" * 80)
    print("SCRAPER FAILURE ANALYSIS REPORT")
    print("=" * 80)
    
    total_failures = sum(len(v) for v in failures_found.values())
    print(f"\n📊 TOTAL FAILURES IDENTIFIED: {total_failures}\n")
    
    print("=" * 80)
    print("FAILURE BREAKDOWN BY TYPE")
    print("=" * 80)
    
    # Lever 404s
    print(f"\n🔴 LEVER API 404 ERRORS: {len(failures_found['lever_404'])}")
    print("-" * 80)
    print("ROOT CAUSE: Company no longer uses Lever ATS or changed subdomain")
    print("API ENDPOINT: https://api.lever.co/v0/postings/{subdomain}")
    print("WHY FAILING: Invalid subdomain or account deactivated")
    print("\nAFFECTED COMPANIES:")
    for i, company in enumerate(sorted(failures_found['lever_404']), 1):
        print(f"  {i:2d}. {company}")
    
    # Greenhouse 404s
    print(f"\n\n🔴 GREENHOUSE API 404 ERRORS: {len(failures_found['greenhouse_404'])}")
    print("-" * 80)
    print("ROOT CAUSE: Company no longer uses Greenhouse or changed board name")
    print("API ENDPOINT: https://boards-api.greenhouse.io/v1/boards/{boardname}/jobs")
    print("WHY FAILING: Invalid board name or account deactivated")
    print("\nAFFECTED COMPANIES:")
    for i, company in enumerate(sorted(failures_found['greenhouse_404']), 1):
        print(f"  {i:2d}. {company}")
    
    # DNS Errors
    print(f"\n\n🔴 DNS/NETWORK ERRORS: {len(failures_found['dns_errors'])}")
    print("-" * 80)
    print("ROOT CAUSE: Invalid domain name or DNS not resolving")
    print("ERROR TYPE: ERR_NAME_NOT_RESOLVED")
    print("WHY FAILING: Domain doesn't exist or DNS misconfiguration")
    print("\nAFFECTED COMPANIES:")
    for i, company in enumerate(sorted(failures_found['dns_errors']), 1):
        print(f"  {i:2d}. {company}")
    
    # Timeouts
    print(f"\n\n🔴 TIMEOUT ERRORS: {len(failures_found['timeouts'])}")
    print("-" * 80)
    print("ROOT CAUSE: Site takes >30 seconds to load")
    print("TIMEOUT LIMIT: 30 seconds")
    print("WHY FAILING: Slow servers, heavy JS rendering, or blocking")
    print("\nAFFECTED COMPANIES:")
    for i, company in enumerate(sorted(failures_found['timeouts']), 1):
        print(f"  {i:2d}. {company}")
    
    # Summary statistics
    print("\n\n" + "=" * 80)
    print("FAILURE STATISTICS")
    print("=" * 80)
    
    total = total_failures
    print(f"\nLever API Failures:      {len(failures_found['lever_404']):3d} ({len(failures_found['lever_404'])/total*100:5.1f}%)")
    print(f"Greenhouse API Failures: {len(failures_found['greenhouse_404']):3d} ({len(failures_found['greenhouse_404'])/total*100:5.1f}%)")
    print(f"DNS/Network Errors:      {len(failures_found['dns_errors']):3d} ({len(failures_found['dns_errors'])/total*100:5.1f}%)")
    print(f"Timeout Errors:          {len(failures_found['timeouts']):3d} ({len(failures_found['timeouts'])/total*100:5.1f}%)")
    print(f"{'─'*40}")
    print(f"TOTAL:                   {total:3d} (100.0%)")
    
    # Root cause analysis
    print("\n\n" + "=" * 80)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 80)
    
    print("\n1️⃣ API ENDPOINT CHANGES (56 companies - 84.8%)")
    print("   Companies switched ATS providers or rebranded")
    print("   Examples:")
    print("   - Switched from Lever to Greenhouse")
    print("   - Switched to Ashby, Workday, or custom ATS")
    print("   - Changed Greenhouse board subdomain")
    print("   - Deactivated ATS account (acquired/shutdown)")
    
    print("\n2️⃣ INFRASTRUCTURE ISSUES (10 companies - 15.2%)")
    print("   Technical problems with domains or performance")
    print("   Examples:")
    print("   - Expired/changed domain names (DNS errors)")
    print("   - Extremely slow sites (30+ second load times)")
    print("   - Blocking/rate limiting scrapers")
    print("   - Server misconfigurations")
    
    print("\n3️⃣ BUSINESS CHANGES")
    print("   - Companies acquired/merged")
    print("   - Companies shut down")
    print("   - Hiring freezes (deactivated careers pages)")
    print("   - Moved to different regions")
    
    # Recommendations
    print("\n\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    print("\n✅ IMMEDIATE ACTIONS:")
    print("   1. Remove all 66 failing companies from watchlist")
    print("   2. Document removed companies with reasons")
    print("   3. Create backup before removal")
    print("   4. Test scraper to verify 0% error rate")
    
    print("\n⚙️ MONITORING STRATEGY:")
    print("   1. Monthly review of removed companies")
    print("   2. Check if they've updated their ATS")
    print("   3. Test 5-10 companies quarterly")
    print("   4. Re-add only verified working endpoints")
    
    print("\n🔧 PREVENTIVE MEASURES:")
    print("   1. Add health check before full scrape")
    print("   2. Implement retry logic with backoff")
    print("   3. Alert on new failures")
    print("   4. Track ATS platform changes")
    
    print("\n📊 EXPECTED IMPROVEMENTS:")
    print("   - Scrape time: 46min → 30-35min (25% faster)")
    print("   - Error rate: 20.4% → 0%")
    print("   - Success rate: 79.6% → 100%")
    print("   - Clean logs: Minimal errors")
    
    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    create_failure_report()
