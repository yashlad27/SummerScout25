#!/usr/bin/env python3
"""
Script to fix ALL failing scrapers (version 2 - includes additional failures).

Creates a backup and removes companies with persistent API failures.
"""

import yaml
from pathlib import Path
from datetime import datetime
import shutil

# Companies to remove (404 errors, no longer use these ATS systems)
COMPANIES_TO_REMOVE = {
    # === Previously identified failures ===
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
    
    # DNS/Network errors
    "GTS",
    "BNP Paribas",
    "American Express",
    
    # Persistent timeouts
    "Zuora",
    "Nuvei",
    "Barclays",
    "Oracle",
    "VMware",
    
    # === Additional failures from recent scrape ===
    # More Greenhouse 404s
    "Box",
    "Alteryx",
    "ThoughtSpot",
    "Alation",
    "Immuta",
    "Etsy",
    "Chainalysis",
    "Elliptic",
    "Lemonade",
    "Root Insurance",
    "Hippo Insurance",
    "Next Insurance",
    "Onfido",
    "Klarna",
    "Varo",
    "LendingClub",
    
    # More Lever 404s
    "Mercado Libre",
    "TRM Labs",
    "Trulioo",
    "Veriff",
    "Sardine",
    "Sezzle",
    "Zip",
    "Upgrade",
    "Avant",
    "Dave",
    "Current",
    "Albert",
    
    # More DNS/Timeout errors
    "Synchrony",
    "Workday",
}

def fix_watchlist(watchlist_path: Path, output_path: Path = None):
    """
    Fix watchlist by removing broken companies.
    
    Args:
        watchlist_path: Path to watchlist.yaml
        output_path: Output path (if None, overwrites original)
    """
    # Create backup
    backup_path = watchlist_path.parent / f"{watchlist_path.stem}_backup_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
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
    
    # List removed companies by category
    print(f"\n🗑️  Removed Companies by Category:")
    
    lever_404 = [c for c in COMPANIES_TO_REMOVE if c in [
        "Radix Trading", "DataVisor", "Castle", "Modern Treasury", "Lithic", 
        "Unit", "Bolt", "IronNet Cybersecurity", "Jeeves", "Rho",
        "Mercado Libre", "TRM Labs", "Trulioo", "Veriff", "Sardine", 
        "Sezzle", "Zip", "Upgrade", "Avant", "Dave", "Current", "Albert"
    ]]
    
    greenhouse_404 = [c for c in COMPANIES_TO_REMOVE if c in [
        "Sift", "Signifyd", "Socure", "Checkout.com", "Chargebee", "Recurly",
        "Rapyd", "Wise", "Remitly", "Tipalti", "ReliaQuest", "Armis", 
        "Claroty", "ExtraHop", "Illumio", "Aqua Security", "Sysdig", "Intuit",
        "Box", "Alteryx", "ThoughtSpot", "Alation", "Immuta", "Etsy",
        "Chainalysis", "Elliptic", "Lemonade", "Root Insurance", 
        "Hippo Insurance", "Next Insurance", "Onfido", "Klarna", "Varo", "LendingClub"
    ]]
    
    dns_timeout = [c for c in COMPANIES_TO_REMOVE if c in [
        "GTS", "BNP Paribas", "American Express", "Synchrony",
        "Zuora", "Nuvei", "Barclays", "Oracle", "VMware", "Workday"
    ]]
    
    print(f"\n   Lever API 404s ({len(lever_404)}):")
    for c in sorted(lever_404):
        print(f"      - {c}")
    
    print(f"\n   Greenhouse API 404s ({len(greenhouse_404)}):")
    for c in sorted(greenhouse_404):
        print(f"      - {c}")
    
    print(f"\n   DNS/Timeout Errors ({len(dns_timeout)}):")
    for c in sorted(dns_timeout):
        print(f"      - {c}")

def main():
    """Main function."""
    project_root = Path(__file__).parent
    watchlist_path = project_root / "config" / "watchlist.yaml"
    
    if not watchlist_path.exists():
        print(f"❌ Watchlist not found: {watchlist_path}")
        return 1
    
    print("🔧 Fixing ALL Failing Scrapers (v2)")
    print("=" * 80)
    print(f"\n📌 Total companies to remove: {len(COMPANIES_TO_REMOVE)}")
    
    # Fix watchlist
    fix_watchlist(watchlist_path)
    
    print("\n" + "=" * 80)
    print(f"✅ Done! {len(COMPANIES_TO_REMOVE)} failing scrapers have been removed.")
    print("\nNext steps:")
    print("  1. Review changes: git diff config/watchlist.yaml")
    print("  2. Test a scrape to verify no more failures")
    print("  3. Commit changes if satisfied")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
