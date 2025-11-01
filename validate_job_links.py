#!/usr/bin/env python3
"""
Validate job links from watchlist to ensure they're accessible and return results.
"""

import yaml
from pathlib import Path
from typing import Dict, List
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingest.schemas import WatchlistTarget
from src.ingest.registry import get_scraper
from src.utils.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class LinkValidator:
    """Validate job links from watchlist."""
    
    def __init__(self, watchlist_path: str = "config/watchlist.yaml"):
        self.watchlist_path = Path(watchlist_path)
        self.results = {
            "valid": [],
            "invalid": [],
            "timeout": [],
            "no_jobs": [],
            "errors": []
        }
    
    def load_watchlist(self) -> List[Dict]:
        """Load watchlist configuration."""
        with open(self.watchlist_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('targets', [])
    
    def validate_target(self, target_config: Dict) -> Dict:
        """
        Validate a single target.
        
        Returns:
            Dict with validation results
        """
        company = target_config.get('company', 'Unknown')
        ats_type = target_config.get('ats_type', 'generic')
        
        result = {
            "company": company,
            "ats_type": ats_type,
            "url": target_config.get('careers_url') or target_config.get('greenhouse_id') or target_config.get('lever_id'),
            "status": "unknown",
            "job_count": 0,
            "error": None
        }
        
        try:
            logger.info(f"Validating {company} ({ats_type})...")
            
            # Create target and scraper
            target = WatchlistTarget(**target_config)
            scraper = get_scraper(target)
            
            if not scraper:
                result["status"] = "error"
                result["error"] = f"No scraper available for {ats_type}"
                return result
            
            # Fetch jobs
            jobs = scraper.fetch()
            result["job_count"] = len(jobs)
            
            if len(jobs) > 0:
                result["status"] = "valid"
                logger.info(f"✅ {company}: Found {len(jobs)} jobs")
            else:
                result["status"] = "no_jobs"
                logger.warning(f"⚠️  {company}: 0 jobs found (might be valid but no openings)")
            
        except Exception as e:
            error_msg = str(e)
            
            # Categorize error
            if "Timeout" in error_msg or "timeout" in error_msg.lower():
                result["status"] = "timeout"
                logger.error(f"⏱️  {company}: Timeout")
            elif "404" in error_msg or "Not Found" in error_msg:
                result["status"] = "invalid"
                logger.error(f"❌ {company}: 404 Not Found")
            elif "DNS" in error_msg or "ERR_NAME_NOT_RESOLVED" in error_msg:
                result["status"] = "invalid"
                logger.error(f"❌ {company}: DNS error - domain doesn't exist")
            elif "HTTP2" in error_msg:
                result["status"] = "error"
                logger.error(f"🚫 {company}: HTTP2 protocol error (site blocking)")
            else:
                result["status"] = "error"
                logger.error(f"❌ {company}: {error_msg[:100]}")
            
            result["error"] = error_msg[:200]
        
        return result
    
    def validate_all(self) -> Dict:
        """Validate all targets in watchlist."""
        logger.info("=" * 70)
        logger.info("🔍 Starting Link Validation")
        logger.info("=" * 70)
        
        targets = self.load_watchlist()
        logger.info(f"Found {len(targets)} companies to validate\n")
        
        for idx, target_config in enumerate(targets, 1):
            logger.info(f"[{idx}/{len(targets)}] Validating...")
            result = self.validate_target(target_config)
            
            # Categorize result
            if result["status"] == "valid":
                self.results["valid"].append(result)
            elif result["status"] == "no_jobs":
                self.results["no_jobs"].append(result)
            elif result["status"] == "timeout":
                self.results["timeout"].append(result)
            elif result["status"] == "invalid":
                self.results["invalid"].append(result)
            else:
                self.results["errors"].append(result)
        
        return self.results
    
    def print_summary(self):
        """Print validation summary."""
        logger.info("\n" + "=" * 70)
        logger.info("📊 VALIDATION SUMMARY")
        logger.info("=" * 70)
        
        total = sum(len(v) for v in self.results.values())
        
        logger.info(f"\n✅ Valid links (with jobs): {len(self.results['valid'])}")
        logger.info(f"⚠️  Valid links (no jobs currently): {len(self.results['no_jobs'])}")
        logger.info(f"⏱️  Timeout: {len(self.results['timeout'])}")
        logger.info(f"❌ Invalid/Dead links: {len(self.results['invalid'])}")
        logger.info(f"🚫 Other errors: {len(self.results['errors'])}")
        logger.info(f"\n📈 Total: {total} companies validated")
        
        # Show problematic links
        if self.results["invalid"]:
            logger.info("\n" + "=" * 70)
            logger.info("❌ INVALID LINKS (404 / DNS errors)")
            logger.info("=" * 70)
            for r in self.results["invalid"]:
                logger.info(f"  • {r['company']} ({r['ats_type']})")
                logger.info(f"    URL: {r['url']}")
                logger.info(f"    Error: {r['error']}\n")
        
        if self.results["timeout"]:
            logger.info("\n" + "=" * 70)
            logger.info("⏱️  TIMEOUT LINKS (>60s)")
            logger.info("=" * 70)
            for r in self.results["timeout"]:
                logger.info(f"  • {r['company']} ({r['ats_type']})")
                logger.info(f"    URL: {r['url']}\n")
        
        if self.results["errors"]:
            logger.info("\n" + "=" * 70)
            logger.info("🚫 OTHER ERRORS")
            logger.info("=" * 70)
            for r in self.results["errors"]:
                logger.info(f"  • {r['company']} ({r['ats_type']})")
                logger.info(f"    URL: {r['url']}")
                logger.info(f"    Error: {r['error']}\n")
        
        # Success rate
        valid_count = len(self.results['valid']) + len(self.results['no_jobs'])
        success_rate = (valid_count / total * 100) if total > 0 else 0
        
        logger.info("\n" + "=" * 70)
        logger.info(f"✨ Success Rate: {success_rate:.1f}% ({valid_count}/{total} accessible)")
        logger.info("=" * 70)
    
    def export_results(self, output_file: str = "link_validation_results.yaml"):
        """Export results to YAML file."""
        output_path = Path(output_file)
        
        export_data = {
            "summary": {
                "total": sum(len(v) for v in self.results.values()),
                "valid_with_jobs": len(self.results['valid']),
                "valid_no_jobs": len(self.results['no_jobs']),
                "timeout": len(self.results['timeout']),
                "invalid": len(self.results['invalid']),
                "errors": len(self.results['errors'])
            },
            "results": self.results
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(export_data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"\n💾 Results exported to: {output_path}")


def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate job links from watchlist')
    parser.add_argument('--watchlist', default='config/watchlist.yaml', help='Path to watchlist file')
    parser.add_argument('--output', default='link_validation_results.yaml', help='Output file for results')
    parser.add_argument('--company', help='Validate only specific company')
    
    args = parser.parse_args()
    
    validator = LinkValidator(args.watchlist)
    
    if args.company:
        # Validate single company
        targets = validator.load_watchlist()
        target = next((t for t in targets if args.company.lower() in t['company'].lower()), None)
        
        if not target:
            logger.error(f"Company '{args.company}' not found in watchlist")
            return
        
        result = validator.validate_target(target)
        logger.info(f"\nResult: {result}")
    else:
        # Validate all
        validator.validate_all()
        validator.print_summary()
        validator.export_results(args.output)


if __name__ == "__main__":
    main()
