#!/usr/bin/env python3
"""
Script to fix failing scrapers by commenting out broken companies.

Creates a backup and removes companies with persistent API failures.
"""

import yaml
from pathlib import Path
from datetime import datetime
import shutil

# Companies to remove (404 errors, no longer use these ATS systems)
COMPANIES_TO_REMOVE = {
    # Lever API 404s
    "Radix Trading",
    "DataVisor",
    "Castle",
    "Modern Treasury",
    "Lithic",
    "Unit",
    "Bolt",
    "IronNet Cybersecurity",
    "Jeeves",
    "Rho",
    
    # Greenhouse API 404s
    "Sift",
    "Signifyd",
    "Socure",
    "Checkout.com",
    "Chargebee",
    "Recurly",
    "Rapyd",
    "Wise",
    "Remitly",
    "Tipalti",
    "ReliaQuest",
    "Armis",
    "Claroty",
    "ExtraHop",
    "Illumio",
    "Aqua Security",
    "Sysdig",
    "Intuit",
    
    # DNS/Network errors (invalid URLs)
    "GTS",
    "BNP Paribas",
    "American Express",
    
    # Persistent timeout issues
    "Zuora",
    "Nuvei",
    "Barclays",
    "Oracle",
    "VMware",
}

def fix_watchlist(watchlist_path: Path, output_path: Path = None):
    """
    Fix watchlist by removing broken companies.
    
    Args:
        watchlist_path: Path to watchlist.yaml
        output_path: Output path (if None, overwrites original)
    """
    # Create backup
    backup_path = watchlist_path.parent / f"{watchlist_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    shutil.copy(watchlist_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Load watchlist
    with open(watchlist_path, 'r') as f:
        watchlist = yaml.safe_load(f)
    
    if 'targets' not in watchlist:
        print("❌ No 'targets' key in watchlist")
        return
    
    # Filter out broken companies
    original_count = len(watchlist['targets'])
    watchlist['targets'] = [
        target for target in watchlist['targets']
        if target.get('company') not in COMPANIES_TO_REMOVE
    ]
    new_count = len(watchlist['targets'])
    removed_count = original_count - new_count
    
    # Write updated watchlist
    output_path = output_path or watchlist_path
    with open(output_path, 'w') as f:
        yaml.dump(watchlist, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n📊 Results:")
    print(f"   Original companies: {original_count}")
    print(f"   Removed: {removed_count}")
    print(f"   Remaining: {new_count}")
    print(f"\n✅ Updated watchlist saved to: {output_path}")
    
    # List removed companies
    print(f"\n🗑️  Removed Companies:")
    for company in sorted(COMPANIES_TO_REMOVE):
        print(f"   - {company}")

def create_removed_companies_doc():
    """Create documentation of removed companies."""
    doc_path = Path(__file__).parent / "REMOVED_COMPANIES.md"
    
    content = f"""# Removed Companies - {datetime.now().strftime('%Y-%m-%d')}

## Overview
The following companies were removed from the watchlist due to persistent scraping failures.

## Reason Categories

### 404 Errors - Lever API
Companies no longer use Lever or changed their careers page:
"""
    
    lever_404 = [
        "Radix Trading",
        "DataVisor",
        "Castle",
        "Modern Treasury",
        "Lithic",
        "Unit",
        "Bolt",
        "IronNet Cybersecurity",
        "Jeeves",
        "Rho",
    ]
    
    for company in lever_404:
        content += f"- **{company}** - `https://jobs.lever.co/{company.lower().replace(' ', '')}`\n"
    
    content += """
### 404 Errors - Greenhouse API
Companies no longer use Greenhouse or changed their board name:
"""
    
    greenhouse_404 = [
        "Sift",
        "Signifyd",
        "Socure",
        "Checkout.com",
        "Chargebee",
        "Recurly",
        "Rapyd",
        "Wise",
        "Remitly",
        "Tipalti",
        "ReliaQuest",
        "Armis",
        "Claroty",
        "ExtraHop",
        "Illumio",
        "Aqua Security",
        "Sysdig",
        "Intuit",
    ]
    
    for company in greenhouse_404:
        content += f"- **{company}** - `https://boards.greenhouse.io/{company.lower().replace(' ', '').replace('.', '')}`\n"
    
    content += """
### DNS/Network Errors
Invalid or changed domain names:
- **GTS** - `https://www.gts.com/careers/`
- **BNP Paribas** - `https://careers.bnpparibas/students`
- **American Express** - `https://careers.americanexpress.com/students`

### Persistent Timeouts
Sites consistently timeout (30+ seconds):
- **Zuora** - `https://www.zuora.com/about/careers/`
- **Nuvei** - `https://nuvei.com/careers/`
- **Barclays** - `https://joinus.barclays/americas/internships/`
- **Oracle** - `https://www.oracle.com/corporate/careers/students-grads/`
- **VMware** - `https://careers.vmware.com/students`

## Total Removed: 37 companies

## How to Re-add

If a company fixes their careers page or changes ATS systems:

1. Research their current ATS system
2. Update `config/watchlist.yaml`
3. Test with: `python -m src.ingest.runner --company "CompanyName"`
4. Remove from this list if successful

## Alternative Data Sources

For some companies, consider:
- Checking LinkedIn Jobs directly
- Using their corporate careers site API
- Manual monitoring of their careers pages
"""
    
    with open(doc_path, 'w') as f:
        f.write(content)
    
    print(f"\n📄 Documentation created: {doc_path}")

def main():
    """Main function."""
    project_root = Path(__file__).parent
    watchlist_path = project_root / "config" / "watchlist.yaml"
    
    if not watchlist_path.exists():
        print(f"❌ Watchlist not found: {watchlist_path}")
        return 1
    
    print("🔧 Fixing Failing Scrapers")
    print("=" * 80)
    
    # Fix watchlist
    fix_watchlist(watchlist_path)
    
    # Create documentation
    create_removed_companies_doc()
    
    print("\n" + "=" * 80)
    print("✅ Done! Failing scrapers have been removed.")
    print("\nNext steps:")
    print("  1. Review changes: git diff config/watchlist.yaml")
    print("  2. Test a scrape: docker-compose run --rm worker python -m src.ingest.runner --company Google")
    print("  3. Commit changes if satisfied")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
