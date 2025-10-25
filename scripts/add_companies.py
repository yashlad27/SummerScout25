#!/usr/bin/env python3
"""Add new companies to US watchlist"""

import yaml

# New companies organized by category
new_companies = [
    # Trading & Quantitative Finance
    {"company": "Citadel Securities", "ats_type": "generic", "url": "https://www.citadelsecurities.com/careers/", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    {"company": "Virtu Financial", "ats_type": "generic", "url": "https://www.virtu.com/careers/", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Tower Research Capital", "ats_type": "generic", "url": "https://www.tower-research.com/careers", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Five Rings Capital", "ats_type": "generic", "url": "https://fiverings.com/apply/", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Belvedere Trading", "ats_type": "lever", "url": "https://jobs.lever.co/belvederetrading", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Flow Traders", "ats_type": "generic", "url": "https://www.flowtraders.com/careers", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Millennium Management", "ats_type": "generic", "url": "https://www.mlp.com/careers/", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    {"company": "Point72", "ats_type": "generic", "url": "https://point72.com/working-here/", "categories": ["software_engineering", "data_science", "ml_ai"]},
    {"company": "Bridgewater Associates", "ats_type": "generic", "url": "https://www.bridgewater.com/careers", "categories": ["software_engineering", "data_science", "ml_ai"]},
    {"company": "Balyasny Asset Management", "ats_type": "generic", "url": "https://www.balyasny.com/join-us", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Voleon Group", "ats_type": "lever", "url": "https://jobs.lever.co/voleon", "categories": ["ml_ai", "data_science", "software_engineering"]},
    {"company": "PDT Partners", "ats_type": "generic", "url": "https://www.pdtpartners.com/careers.html", "categories": ["software_engineering", "data_science"]},
    {"company": "Radix Trading", "ats_type": "lever", "url": "https://jobs.lever.co/radixtrading", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Old Mission Capital", "ats_type": "generic", "url": "https://www.oldmissioncapital.com/careers/", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Geneva Trading", "ats_type": "generic", "url": "https://www.genevatrading.com/careers/", "categories": ["software_engineering"]},
    {"company": "Group One Trading", "ats_type": "generic", "url": "https://group1.com/careers", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Wolverine Trading", "ats_type": "generic", "url": "https://www.wolve.com/careers", "categories": ["software_engineering", "data_engineering"]},
    {"company": "GTS", "ats_type": "generic", "url": "https://www.gts.com/careers/", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Valkyrie Trading", "ats_type": "generic", "url": "https://www.valkyrietrading.com/careers/", "categories": ["software_engineering"]},
    {"company": "Schonfeld Strategic Advisors", "ats_type": "generic", "url": "https://www.schonfeld.com/careers/", "categories": ["software_engineering", "data_science"]},
    
    # Fraud Detection & Security Platforms
    {"company": "Sift", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/sift", "categories": ["software_engineering", "ml_ai", "data_science", "cybersecurity"]},
    {"company": "Feedzai", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/feedzai", "categories": ["software_engineering", "ml_ai", "data_science", "cybersecurity"]},
    {"company": "BioCatch", "ats_type": "generic", "url": "https://www.biocatch.com/company/careers", "categories": ["software_engineering", "ml_ai", "cybersecurity"]},
    {"company": "Signifyd", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/signifyd", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Forter", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/forter", "categories": ["software_engineering", "ml_ai", "data_science", "cybersecurity"]},
    {"company": "Kount", "ats_type": "generic", "url": "https://www.kount.com/company/careers", "categories": ["software_engineering", "ml_ai", "cybersecurity"]},
    {"company": "Riskified", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/riskified", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "DataVisor", "ats_type": "lever", "url": "https://jobs.lever.co/datavisor", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Socure", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/socure", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Arkose Labs", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/arkoselabs", "categories": ["software_engineering", "ml_ai", "cybersecurity"]},
    {"company": "Castle", "ats_type": "lever", "url": "https://jobs.lever.co/castle", "categories": ["software_engineering", "cybersecurity"]},
    
    # Payment Infrastructure & Fintech
    {"company": "Adyen", "ats_type": "generic", "url": "https://careers.adyen.com/", "categories": ["software_engineering", "backend", "data_engineering", "cybersecurity"]},
    {"company": "Checkout.com", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/checkout", "categories": ["software_engineering", "backend", "data_engineering"]},
    {"company": "Modern Treasury", "ats_type": "lever", "url": "https://jobs.lever.co/moderntreasury", "categories": ["software_engineering", "backend", "data_engineering"]},
    {"company": "Lithic", "ats_type": "lever", "url": "https://jobs.lever.co/lithic", "categories": ["software_engineering", "backend", "cybersecurity"]},
    {"company": "Unit", "ats_type": "lever", "url": "https://jobs.lever.co/unit", "categories": ["software_engineering", "backend"]},
    {"company": "Finix", "ats_type": "lever", "url": "https://jobs.lever.co/finix", "categories": ["software_engineering", "backend"]},
    {"company": "Pagaya", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/pagaya", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Chargebee", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/chargebee", "categories": ["software_engineering", "backend"]},
    {"company": "Recurly", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/recurly", "categories": ["software_engineering", "backend"]},
    {"company": "Zuora", "ats_type": "generic", "url": "https://www.zuora.com/about/careers/", "categories": ["software_engineering", "backend"]},
    {"company": "Bolt", "ats_type": "lever", "url": "https://jobs.lever.co/bolt", "categories": ["software_engineering", "backend", "cybersecurity"]},
    {"company": "Rapyd", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/rapyd", "categories": ["software_engineering", "backend"]},
    {"company": "Nuvei", "ats_type": "generic", "url": "https://nuvei.com/careers/", "categories": ["software_engineering", "backend", "cybersecurity"]},
    {"company": "Payoneer", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/payoneer", "categories": ["software_engineering", "backend"]},
    {"company": "Wise", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/wise", "categories": ["software_engineering", "backend", "data_engineering"]},
    {"company": "Remitly", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/remitly", "categories": ["software_engineering", "backend", "ml_ai"]},
    {"company": "Melio", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/melio", "categories": ["software_engineering", "backend"]},
    {"company": "Bill.com", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/billcom", "categories": ["software_engineering", "backend", "data_engineering"]},
    {"company": "Tipalti", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/tipalti", "categories": ["software_engineering", "backend"]},
    {"company": "Jeeves", "ats_type": "lever", "url": "https://jobs.lever.co/jeeves", "categories": ["software_engineering", "backend"]},
    {"company": "Rho", "ats_type": "lever", "url": "https://jobs.lever.co/rho", "categories": ["software_engineering", "backend"]},
    {"company": "Brex", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/brex", "categories": ["software_engineering", "backend", "ml_ai"]},
    {"company": "Ramp", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/ramp", "categories": ["software_engineering", "backend", "ml_ai"]},
    {"company": "Navan", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/tripactions", "categories": ["software_engineering", "backend", "ml_ai"]},
    
    # Cybersecurity
    {"company": "Recorded Future", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/recordedfuture", "categories": ["cybersecurity", "ml_ai", "data_science"]},
    {"company": "ThreatConnect", "ats_type": "lever", "url": "https://jobs.lever.co/threatconnect", "categories": ["cybersecurity", "software_engineering"]},
    {"company": "Anomali", "ats_type": "lever", "url": "https://jobs.lever.co/anomali", "categories": ["cybersecurity", "ml_ai"]},
    {"company": "IronNet Cybersecurity", "ats_type": "lever", "url": "https://jobs.lever.co/ironnetcybersecurity", "categories": ["cybersecurity", "ml_ai"]},
    {"company": "ReliaQuest", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/reliaquest", "categories": ["cybersecurity", "software_engineering"]},
    {"company": "KnowBe4", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/knowbe4", "categories": ["cybersecurity", "software_engineering"]},
    {"company": "Armis", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/armis", "categories": ["cybersecurity", "ml_ai", "software_engineering"]},
    {"company": "Claroty", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/claroty", "categories": ["cybersecurity", "software_engineering"]},
    {"company": "Dragos", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/dragos", "categories": ["cybersecurity", "software_engineering"]},
    {"company": "ExtraHop", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/extrahop", "categories": ["cybersecurity", "ml_ai", "software_engineering"]},
    {"company": "Tanium", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/tanium", "categories": ["cybersecurity", "software_engineering"]},
    {"company": "Illumio", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/illumio", "categories": ["cybersecurity", "software_engineering"]},
    {"company": "Orca Security", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/orcasecurity", "categories": ["cybersecurity", "software_engineering", "ml_ai"]},
    {"company": "Aqua Security", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/aquasecurity", "categories": ["cybersecurity", "software_engineering"]},
    {"company": "Sysdig", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/sysdig", "categories": ["cybersecurity", "software_engineering"]},
    
    # Banks & Financial Institutions
    {"company": "Bank of America", "ats_type": "generic", "url": "https://campus.bankofamerica.com/", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    {"company": "Wells Fargo", "ats_type": "generic", "url": "https://www.wellsfargo.com/about/careers/students/", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    {"company": "Citi", "ats_type": "generic", "url": "https://jobs.citi.com/students", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    {"company": "Barclays", "ats_type": "generic", "url": "https://joinus.barclays/americas/internships/", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Deutsche Bank", "ats_type": "generic", "url": "https://careers.db.com/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "UBS", "ats_type": "generic", "url": "https://www.ubs.com/careers/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "BNP Paribas", "ats_type": "generic", "url": "https://careers.bnpparibas/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "HSBC", "ats_type": "generic", "url": "https://www.hsbc.com/careers/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Standard Chartered", "ats_type": "generic", "url": "https://www.sc.com/careers/students/", "categories": ["software_engineering", "data_engineering"]},
    {"company": "American Express", "ats_type": "generic", "url": "https://careers.americanexpress.com/students", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    {"company": "Discover", "ats_type": "generic", "url": "https://jobs.discover.com/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Mastercard", "ats_type": "generic", "url": "https://careers.mastercard.com/students", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    {"company": "Visa", "ats_type": "generic", "url": "https://usa.visa.com/careers/students.html", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    {"company": "Fidelity", "ats_type": "generic", "url": "https://jobs.fidelity.com/students/", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Charles Schwab", "ats_type": "generic", "url": "https://www.schwab.com/careers/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Vanguard", "ats_type": "generic", "url": "https://www.vanguardjobs.com/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "BlackRock", "ats_type": "generic", "url": "https://careers.blackrock.com/students", "categories": ["software_engineering", "data_engineering", "ml_ai"]},
    
    # Big Tech Additional
    {"company": "Oracle", "ats_type": "generic", "url": "https://www.oracle.com/corporate/careers/students-grads/", "categories": ["software_engineering", "backend", "data_engineering", "cybersecurity"]},
    {"company": "Cisco", "ats_type": "generic", "url": "https://www.cisco.com/c/en/us/about/careers/we-are-cisco/students-and-new-graduates.html", "categories": ["software_engineering", "cybersecurity", "data_engineering"]},
    {"company": "VMware", "ats_type": "generic", "url": "https://careers.vmware.com/students", "categories": ["software_engineering", "cybersecurity"]},
    {"company": "Broadcom", "ats_type": "generic", "url": "https://www.broadcom.com/company/careers/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Intuit", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/intuit", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Workday", "ats_type": "generic", "url": "https://www.workday.com/en-us/company/careers/university-recruiting.html", "categories": ["software_engineering", "ml_ai", "data_engineering"]},
    {"company": "Box", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/box", "categories": ["software_engineering", "backend", "cybersecurity"]},
    {"company": "Dropbox", "ats_type": "generic", "url": "https://www.dropbox.com/jobs/teams/emerging-talent", "categories": ["software_engineering", "backend", "ml_ai"]},
    
    # Data & Analytics
    {"company": "Alteryx", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/alteryx", "categories": ["software_engineering", "data_engineering", "data_science"]},
    {"company": "Domo", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/domo", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Sisense", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/sisense", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Qlik", "ats_type": "generic", "url": "https://www.qlik.com/careers", "categories": ["software_engineering", "data_engineering"]},
    {"company": "ThoughtSpot", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/thoughtspot", "categories": ["software_engineering", "data_engineering", "ml_ai"]},
    {"company": "Collibra", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/collibra", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Alation", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/alation", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Immuta", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/immuta", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    {"company": "BigID", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/bigid", "categories": ["software_engineering", "data_engineering", "cybersecurity"]},
    
    # E-commerce & Marketplace
    {"company": "Etsy", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/etsy", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "eBay", "ats_type": "generic", "url": "https://careers.ebayinc.com/students", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Mercado Libre", "ats_type": "lever", "url": "https://jobs.lever.co/mercadolibre", "categories": ["software_engineering", "ml_ai"]},
    {"company": "StockX", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/stockx", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Poshmark", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/poshmark", "categories": ["software_engineering", "ml_ai"]},
    
    # Crypto & Blockchain Security
    {"company": "Chainalysis", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/chainalysis", "categories": ["software_engineering", "data_science", "cybersecurity"]},
    {"company": "Elliptic", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/elliptic", "categories": ["software_engineering", "ml_ai", "cybersecurity"]},
    {"company": "TRM Labs", "ats_type": "lever", "url": "https://jobs.lever.co/trmlabs", "categories": ["software_engineering", "data_science", "cybersecurity"]},
    
    # Insurance Tech
    {"company": "Lemonade", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/lemonade", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Root Insurance", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/rootinc", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Hippo Insurance", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/hippoinsurance", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Next Insurance", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/nextinsurance", "categories": ["software_engineering", "data_engineering"]},
    
    # RegTech & Compliance
    {"company": "ComplyAdvantage", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/complyadvantage", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Trulioo", "ats_type": "lever", "url": "https://jobs.lever.co/trulioo", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Jumio", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/jumio", "categories": ["software_engineering", "ml_ai", "cybersecurity"]},
    {"company": "Onfido", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/onfido", "categories": ["software_engineering", "ml_ai", "cybersecurity"]},
    {"company": "Veriff", "ats_type": "lever", "url": "https://jobs.lever.co/veriff", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Persona", "ats_type": "lever", "url": "https://jobs.lever.co/persona", "categories": ["software_engineering", "ml_ai", "cybersecurity"]},
    {"company": "Alloy", "ats_type": "lever", "url": "https://jobs.lever.co/alloy", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Sardine", "ats_type": "lever", "url": "https://jobs.lever.co/sardine", "categories": ["software_engineering", "ml_ai", "cybersecurity"]},
    
    # Additional Fintech
    {"company": "Klarna", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/klarna", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Sezzle", "ats_type": "lever", "url": "https://jobs.lever.co/sezzle", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Zip", "ats_type": "lever", "url": "https://jobs.lever.co/zip", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Bread Financial", "ats_type": "generic", "url": "https://careers.breadfinancial.com/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Synchrony", "ats_type": "generic", "url": "https://careers.synchrony.com/students", "categories": ["software_engineering", "data_engineering"]},
    {"company": "Upgrade", "ats_type": "lever", "url": "https://jobs.lever.co/upgrade", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Avant", "ats_type": "lever", "url": "https://jobs.lever.co/avant", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Dave", "ats_type": "lever", "url": "https://jobs.lever.co/dave", "categories": ["software_engineering", "ml_ai"]},
    {"company": "MoneyLion", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/moneylion", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Current", "ats_type": "lever", "url": "https://jobs.lever.co/current", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Albert", "ats_type": "lever", "url": "https://jobs.lever.co/albert", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Varo", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/varomoney", "categories": ["software_engineering", "ml_ai"]},
    {"company": "LendingClub", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/lendingclub", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "Prosper", "ats_type": "lever", "url": "https://jobs.lever.co/prosper", "categories": ["software_engineering", "ml_ai"]},
    {"company": "Upstart", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/upstart", "categories": ["software_engineering", "ml_ai", "data_science"]},
    {"company": "SoFi", "ats_type": "greenhouse", "url": "https://boards.greenhouse.io/sofi", "categories": ["software_engineering", "ml_ai", "data_science"]},
]

# Load existing watchlist (MAIN file used by ./scrape.sh)
watchlist_path = '/Users/yashlad/Development/linkedin_job_scrapper/config/watchlist.yaml'
with open(watchlist_path, 'r') as f:
    watchlist = yaml.safe_load(f)

# Count existing companies
existing_count = len(watchlist["targets"])
existing_names = {target["company"] for target in watchlist["targets"]}

# Add new companies (skip if already exists)
added_count = 0
for company_data in new_companies:
    if company_data["company"] not in existing_names:
        entry = {
            "company": company_data["company"],
            "ats_type": company_data["ats_type"],
            "careers_url": company_data["url"],
            "roles_include": ["intern", "summer 2026", "internship"],
            "locations": ["Remote", "New York", "Bay Area", "Seattle", "Boston", "Austin", "Chicago"],
            "categories": company_data["categories"]
        }
        watchlist["targets"].append(entry)
        added_count += 1

# Write back to MAIN watchlist
with open(watchlist_path, 'w') as f:
    yaml.dump(watchlist, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"✅ Added {added_count} new companies to main watchlist")
print(f"📊 Total companies: {len(watchlist['targets'])} (was {existing_count})")
print(f"🎯 Skipped {len(new_companies) - added_count} duplicates")
