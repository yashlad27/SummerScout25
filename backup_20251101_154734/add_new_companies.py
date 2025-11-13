#!/usr/bin/env python3
"""Script to add 50+ new medium-sized tech companies to watchlist"""

import yaml

# New companies to add
new_companies = [
    # Cybersecurity & Cloud Security
    {"company": "Lacework", "url": "https://www.lacework.com/careers/", "source": "generic"},
    {"company": "Abnormal Security", "url": "https://abnormalsecurity.com/careers", "source": "generic"},
    {"company": "Axonius", "url": "https://www.axonius.com/careers", "source": "generic"},
    {"company": "SecurityScorecard", "url": "https://securityscorecard.com/company/careers", "source": "generic"},
    
    # Developer Tools & Infrastructure
    {"company": "Vercel", "url": "https://vercel.com/careers", "source": "generic"},
    {"company": "Supabase", "url": "https://supabase.com/careers", "source": "generic"},
    {"company": "PlanetScale", "url": "https://planetscale.com/careers", "source": "generic"},
    {"company": "Neon", "url": "https://neon.tech/careers", "source": "generic"},
    {"company": "Fly.io", "url": "https://fly.io/jobs/", "source": "generic"},
    {"company": "Railway", "url": "https://railway.app/careers", "source": "generic"},
    {"company": "Render", "url": "https://render.com/careers", "source": "generic"},
    {"company": "Postman", "url": "https://www.postman.com/company/careers/", "source": "generic"},
    {"company": "LaunchDarkly", "url": "https://launchdarkly.com/careers/", "source": "generic"},
    {"company": "Pulumi", "url": "https://www.pulumi.com/careers/", "source": "generic"},
    {"company": "Temporal", "url": "https://temporal.io/careers", "source": "generic"},
    
    # Data & Analytics
    {"company": "Fivetran", "url": "https://www.fivetran.com/careers", "source": "generic"},
    {"company": "dbt Labs", "url": "https://www.getdbt.com/careers/", "source": "generic"},
    {"company": "Airbyte", "url": "https://airbyte.com/careers", "source": "generic"},
    {"company": "Starburst Data", "url": "https://www.starburst.io/careers/", "source": "generic"},
    {"company": "Preset", "url": "https://preset.io/careers/", "source": "generic"},
    {"company": "Census", "url": "https://www.getcensus.com/careers", "source": "generic"},
    {"company": "Hightouch", "url": "https://hightouch.com/careers", "source": "generic"},
    
    # Fintech
    {"company": "Ramp", "url": "https://ramp.com/careers", "source": "generic"},
    {"company": "Mercury", "url": "https://mercury.com/careers", "source": "generic"},
    {"company": "Gusto", "url": "https://gusto.com/careers", "source": "generic"},
    {"company": "Rippling", "url": "https://www.rippling.com/careers", "source": "generic"},
    {"company": "Marqeta", "url": "https://www.marqeta.com/careers", "source": "generic"},
    {"company": "Navan", "url": "https://navan.com/careers", "source": "generic"},
    {"company": "Column", "url": "https://column.com/careers", "source": "generic"},
    
    # E-commerce & Retail Tech
    {"company": "Faire", "url": "https://www.faire.com/careers", "source": "generic"},
    {"company": "Flexport", "url": "https://www.flexport.com/careers/", "source": "generic"},
    {"company": "Shippo", "url": "https://goshippo.com/careers", "source": "generic"},
    {"company": "BigCommerce", "url": "https://careers.bigcommerce.com/", "source": "generic"},
    
    # Communication & Collaboration
    {"company": "Discord", "url": "https://discord.com/careers", "source": "generic"},
    {"company": "Zoom", "url": "https://careers.zoom.us/", "source": "generic"},
    {"company": "Airtable", "url": "https://www.airtable.com/careers", "source": "generic"},
    {"company": "Loom", "url": "https://www.loom.com/careers", "source": "generic"},
    {"company": "Pitch", "url": "https://pitch.com/careers", "source": "generic"},
    
    # AI & ML Startups
    {"company": "Weights & Biases", "url": "https://www.wandb.com/careers", "source": "generic"},
    {"company": "Replicate", "url": "https://replicate.com/careers", "source": "generic"},
    {"company": "Modal", "url": "https://modal.com/careers", "source": "generic"},
    {"company": "Runway", "url": "https://runwayml.com/careers/", "source": "generic"},
    {"company": "Stability AI", "url": "https://stability.ai/careers", "source": "generic"},
    {"company": "Character.AI", "url": "https://character.ai/careers", "source": "generic"},
    {"company": "Perplexity AI", "url": "https://www.perplexity.ai/careers", "source": "generic"},
    {"company": "Together AI", "url": "https://www.together.ai/careers", "source": "generic"},
    
    # Gaming & Entertainment
    {"company": "Unity", "url": "https://careers.unity.com/", "source": "generic"},
    {"company": "Roblox", "url": "https://corp.roblox.com/careers/", "source": "generic"},
    {"company": "Epic Games", "url": "https://www.epicgames.com/site/careers", "source": "generic"},
    {"company": "Riot Games", "url": "https://www.riotgames.com/en/work-with-us/jobs", "source": "generic"},
    
    # Health Tech
    {"company": "Oscar Health", "url": "https://www.hioscar.com/careers", "source": "generic"},
    {"company": "Ro", "url": "https://ro.co/careers/", "source": "generic"},
    {"company": "Hims & Hers", "url": "https://www.forhims.com/careers", "source": "generic"},
    {"company": "Tempus", "url": "https://www.tempus.com/careers/", "source": "generic"},
    
    # Autonomous Vehicles & Robotics
    {"company": "Cruise", "url": "https://getcruise.com/careers/", "source": "generic"},
    {"company": "Aurora", "url": "https://aurora.tech/careers", "source": "generic"},
    {"company": "Zoox", "url": "https://zoox.com/careers/", "source": "generic"},
    {"company": "Nuro", "url": "https://www.nuro.ai/careers", "source": "generic"},
    
    # SaaS & Enterprise
    {"company": "Auth0", "url": "https://auth0.com/careers", "source": "generic"},
    {"company": "Segment", "url": "https://segment.com/careers/", "source": "generic"},
    {"company": "Amplitude", "url": "https://amplitude.com/careers", "source": "generic"},
    {"company": "Mixpanel", "url": "https://mixpanel.com/careers/", "source": "generic"},
    {"company": "Heap", "url": "https://heap.io/careers", "source": "generic"},
    {"company": "Pendo", "url": "https://www.pendo.io/careers/", "source": "generic"},
    {"company": "Gong", "url": "https://www.gong.io/careers/", "source": "generic"},
    {"company": "Outreach", "url": "https://www.outreach.io/company/careers", "source": "generic"},
    
    # PropTech & Real Estate
    {"company": "Opendoor", "url": "https://www.opendoor.com/jobs", "source": "generic"},
    {"company": "Redfin", "url": "https://www.redfin.com/careers", "source": "generic"},
    {"company": "Zillow", "url": "https://www.zillow.com/careers/", "source": "generic"},
    
    # Social & Content
    {"company": "Reddit", "url": "https://www.redditinc.com/careers", "source": "generic"},
    {"company": "Snap", "url": "https://careers.snap.com/", "source": "generic"},
    {"company": "Pinterest", "url": "https://www.pinterestcareers.com/", "source": "generic"},
    {"company": "TikTok", "url": "https://careers.tiktok.com/", "source": "generic"},
    {"company": "Twitch", "url": "https://www.twitch.tv/jobs/", "source": "generic"},
    
    # EdTech
    {"company": "Coursera", "url": "https://about.coursera.org/careers/", "source": "generic"},
    {"company": "Udemy", "url": "https://about.udemy.com/careers/", "source": "generic"},
    {"company": "Duolingo", "url": "https://careers.duolingo.com/", "source": "generic"},
    {"company": "Quizlet", "url": "https://quizlet.com/careers", "source": "generic"},
    {"company": "Grammarly", "url": "https://www.grammarly.com/jobs", "source": "generic"},
]

def main():
    # Read existing watchlist
    with open('config/watchlist.yaml', 'r') as f:
        watchlist = yaml.safe_load(f)
    
    # Get existing companies to avoid duplicates
    existing_companies = {target['company'] for target in watchlist['targets']}
    
    # Add new companies
    added_count = 0
    for company_data in new_companies:
        if company_data['company'] not in existing_companies:
            new_entry = {
                'company': company_data['company'],
                'ats_type': company_data['source'],
                'careers_url': company_data['url'],
                'roles_include': ['intern', 'summer 2026', 'internship'],
                'locations': ['Remote', 'New York', 'Bay Area', 'Seattle', 'Boston', 'Austin', 'Chicago'],
                'categories': [
                    'software_engineering', 'backend', 'frontend', 'fullstack', 'mobile',
                    'devops', 'qa_testing', 'ml_ai', 'data_engineering', 'data_science',
                    'cybersecurity', 'platform_security', 'ml_platform'
                ]
            }
            watchlist['targets'].append(new_entry)
            added_count += 1
            print(f"✓ Added: {company_data['company']}")
        else:
            print(f"⊘ Skipped (already exists): {company_data['company']}")
    
    # Save updated watchlist
    with open('config/watchlist.yaml', 'w') as f:
        yaml.dump(watchlist, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n✅ Added {added_count} new companies!")
    print(f"📊 Total companies: {len(watchlist['targets'])}")

if __name__ == '__main__':
    main()
