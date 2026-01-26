# ===============================================
#  AI TALENT ENGINE — SIGNAL INTELLIGENCE
#
#  Proprietary and Confidential
#
#  © 2025–2026 L. David Mendoza. All Rights Reserved.
#
#  This file is part of the AI Talent Engine — Signal Intelligence system.
#  It contains proprietary methodologies, schemas, scoring logic, and
#  execution workflows developed by L. David Mendoza.
#
#  Unauthorized copying, modification, distribution, disclosure, or use
#  of this file or its contents, in whole or in part, is strictly prohibited
#  without prior written consent from the author.
#
#  This code is intended solely for authorized evaluation, demonstration,
#  and execution under controlled conditions as defined in the
#  Canonical Requirements Manifest and Claude Master Execution Guidebook.
#
#  GOVERNANCE NOTICE:
#  — Public-source data only
#  — No inferred or fabricated data
#  — No private or gated scraping
#  — Deterministic, audit-ready execution required
#
# ===============================================

"""
AI Talent Engine - Main Pipeline Orchestrator
Version: 1.0.0
"""

import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
import json

# Import pipeline modules
from seed_hub_parser import SeedHubParser
from seed_enumerator import SeedEnumerator
from evidence_enricher import EvidenceEnricher
from contact_scraper import ContactScraper
from role_classifier import RoleClassifier
from citation_calculator import CitationCalculator
from schema_validator import SchemaValidator
from output_generator import OutputGenerator
from talent_preview import TalentPreview


class AITalentPipeline:
    """Main orchestrator for AI Talent Engine automation"""
    
    VALID_MODES = ['demo', 'gpt_slim', 'scenario']
    DEMO_MAX_ROWS = 50
    
    def __init__(self, mode: str, seed_hub_path: str, output_dir: str = './outputs'):
        """
        Initialize the pipeline
        
        Args:
            mode: Execution mode (demo, gpt_slim, scenario)
            seed_hub_path: Path to Seed Hub Excel file
            output_dir: Output directory for results
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {self.VALID_MODES}")
        
        self.mode = mode
        self.seed_hub_path = seed_hub_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        self.quarantine_rows = []
        self.audit_log = []
        
        # Initialize modules
        self.parser = SeedHubParser(seed_hub_path)
        self.enumerator = SeedEnumerator()
        self.enricher = EvidenceEnricher()
        self.contact_scraper = ContactScraper()
        self.role_classifier = RoleClassifier()
        self.citation_calc = CitationCalculator()
        self.validator = SchemaValidator()
        self.output_gen = OutputGenerator()
        self.preview = TalentPreview()
        
    def log(self, message: str, level: str = 'INFO'):
        """Add entry to audit log"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.audit_log.append(log_entry)
        print(log_entry)
    
    def run(self) -> dict:
        """Execute the full pipeline"""
        self.log(f"Starting AI Talent Engine pipeline in {self.mode.upper()} mode")
        
        try:
            # Stage 1: Parse Seed Hub
            self.log("Stage 1: Parsing Seed Hub Excel")
            seed_data = self.parser.parse()
            self.log(f"Loaded {len(seed_data)} seed sources")
            
            # Stage 2: Enumerate individuals from seed sources
            self.log("Stage 2: Enumerating individuals from seed sources")
            individuals = []
            for idx, seed in enumerate(seed_data):
                try:
                    enumerated = self.enumerator.enumerate_from_seed(seed)
                    individuals.extend(enumerated)
                    if enumerated:
                        self.log(f"  Seed {idx+1}: Enumerated {len(enumerated)} individuals from {seed.get('Organization', 'Unknown')}")
                except Exception as e:
                    self.log(f"  Seed {idx+1}: Enumeration failed - {str(e)}", level='ERROR')
            
            self.log(f"Total individuals enumerated: {len(individuals)}")
            
            # CRITICAL: Zero enumerated individuals = FAILED RUN
            # ABORT EARLY - Do not proceed to enrichment
            if len(individuals) == 0 and len(seed_data) > 0:
                self.log("="*80, level='CRITICAL')
                self.log("PIPELINE FAILURE: Enumeration returned 0 individuals", level='CRITICAL')
                self.log("="*80, level='CRITICAL')
                self.log(f"Seed sources parsed: {len(seed_data)}", level='CRITICAL')
                self.log(f"Enumeration attempts: {len(self.enumerator.get_enumeration_stats())}", level='CRITICAL')
                self.log(f"Individuals enumerated: 0", level='CRITICAL')
                self.log("", level='CRITICAL')
                self.log("LIKELY CAUSE: Network blocking or API access failure", level='CRITICAL')
                self.log("ACTION REQUIRED: Deploy in environment with access to:", level='CRITICAL')
                self.log("  - api.github.com", level='CRITICAL')
                self.log("  - api.semanticscholar.org", level='CRITICAL')
                self.log("  - api.openalex.org", level='CRITICAL')
                self.log("="*80, level='CRITICAL')
                
                # Write minimal audit log
                self._write_audit_log()
                
                # Return failure result immediately
                return {
                    'status': 'FAILED',
                    'enumeration_failed': True,
                    'failure_reason': 'Enumeration returned 0 individuals from non-zero seed sources',
                    'records_processed': 0,
                    'records_quarantined': 0,
                    'output_files': {},
                    'preview_file': None,
                    'seeds_parsed': len(seed_data),
                    'enumeration_attempts': len(self.enumerator.get_enumeration_stats())
                }
            
            # Get enumeration stats
            stats = self.enumerator.get_enumeration_stats()
            self.log(f"Enumeration stats: {len(stats)} sources processed")
            
            # Stage 3: Determine row limit based on mode
            row_limit = self._get_row_limit()
            self.log(f"Row limit for {self.mode} mode: {row_limit}")
            
            # Apply limit
            if row_limit:
                individuals = individuals[:row_limit]
                self.log(f"Limited to {len(individuals)} individuals")
            
            # Stage 4: Evidence enrichment
            # Stage 4: Evidence enrichment
            self.log("Stage 4: Enriching evidence (URLs, OSS, Kaggle, Publications, Patents)")
            enriched_data = []
            for idx, record in enumerate(individuals):
                try:
                    enriched = self.enricher.enrich(record)
                    enriched_data.append(enriched)
                except Exception as e:
                    self.log(f"Failed to enrich row {idx}: {str(e)}", level='ERROR')
                    self.quarantine_rows.append({'row': idx, 'data': record, 'error': str(e)})
            
            self.log(f"Successfully enriched {len(enriched_data)} records")
            
            # Stage 5: Contact scraping
            self.log("Stage 5: Scraping contact information (email, phone, location)")
            for idx, record in enumerate(enriched_data):
                try:
                    self.contact_scraper.scrape(record)
                except Exception as e:
                    self.log(f"Contact scraping failed for row {idx}: {str(e)}", level='WARN')
            
            # Stage 6: Role classification
            self.log("Stage 6: Classifying AI roles")
            for record in enriched_data:
                try:
                    self.role_classifier.classify(record)
                except Exception as e:
                    self.log(f"Role classification failed: {str(e)}", level='WARN')
            
            # Stage 7: Citation velocity calculation
            self.log("Stage 7: Calculating citation velocities")
            for record in enriched_data:
                try:
                    self.citation_calc.calculate(record)
                except Exception as e:
                    self.log(f"Citation calculation failed: {str(e)}", level='WARN')
            
            # Stage 8: Schema validation
            self.log("Stage 8: Validating schema compliance")
            validated_data = []
            for idx, record in enumerate(enriched_data):
                if self.validator.validate(record):
                    validated_data.append(record)
                else:
                    self.log(f"Schema validation failed for row {idx}", level='ERROR')
                    self.quarantine_rows.append({'row': idx, 'data': record, 'error': 'Schema validation failed'})
            
            self.log(f"Schema validation passed for {len(validated_data)} records")
            
            # Stage 9: Generate outputs
            self.log("Stage 9: Generating outputs")
            output_files = self.output_gen.generate(
                validated_data, 
                self.mode, 
                self.output_dir, 
                self.timestamp
            )
            
            # Stage 10: Generate Talent Intelligence Preview
            self.log("Stage 10: Generating Talent Intelligence Preview")
            preview_html = self.preview.generate(validated_data, self.mode, enumeration_failed)
            preview_path = self.output_dir / f"talent_preview_{self.mode}_{self.timestamp}.html"
            preview_path.write_text(preview_html)
            
            # Stage 11: Write quarantine and audit files
            self._write_quarantine()
            self._write_audit_log()
            self._write_validation_report(validated_data)
            
            self.log(f"Pipeline completed successfully. Processed {len(validated_data)} records.")
            
            # Determine overall success
            run_status = 'FAILED' if (enumeration_failed or len(validated_data) == 0) else 'SUCCESS'
            
            return {
                'status': run_status,
                'enumeration_failed': enumeration_failed,
                'records_processed': len(validated_data),
                'records_quarantined': len(self.quarantine_rows),
                'output_files': output_files,
                'preview_file': str(preview_path)
            }
            
        except Exception as e:
            self.log(f"Pipeline failed: {str(e)}", level='CRITICAL')
            raise
    
    def _get_row_limit(self) -> int:
        """Get row limit based on execution mode"""
        if self.mode == 'demo':
            return self.DEMO_MAX_ROWS
        elif self.mode == 'gpt_slim':
            return self.DEMO_MAX_ROWS  # Same limit as demo
        else:  # scenario
            return None  # No limit
    
    def _write_quarantine(self):
        """Write quarantined rows to separate CSV"""
        if not self.quarantine_rows:
            return
        
        quarantine_path = self.output_dir / f"quarantine_{self.mode}_{self.timestamp}.json"
        with open(quarantine_path, 'w') as f:
            json.dump(self.quarantine_rows, f, indent=2)
        
        self.log(f"Wrote {len(self.quarantine_rows)} quarantined rows to {quarantine_path}")
    
    def _write_audit_log(self):
        """Write audit log to text file"""
        audit_path = self.output_dir / f"audit_log_{self.mode}_{self.timestamp}.txt"
        with open(audit_path, 'w') as f:
            f.write('\n'.join(self.audit_log))
        
        self.log(f"Wrote audit log to {audit_path}")
    
    def _write_validation_report(self, data: list):
        """Write validation report JSON"""
        report = {
            'pipeline_version': '1.0.0',
            'schema_version': '3.3',
            'execution_mode': self.mode,
            'timestamp': self.timestamp,
            'records_processed': len(data),
            'records_quarantined': len(self.quarantine_rows),
            'validation_passed': True,
            'governance_agents': ['#21', '#22', '#23', '#24', '#36']
        }
        
        report_path = self.output_dir / f"validation_report_{self.mode}_{self.timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Wrote validation report to {report_path}")


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(
        description='AI Talent Engine - Signal Intelligence Pipeline'
    )
    parser.add_argument(
        '--mode',
        required=True,
        choices=['demo', 'gpt_slim', 'scenario'],
        help='Execution mode'
    )
    parser.add_argument(
        '--seed-hub',
        required=True,
        help='Path to Seed Hub Excel file'
    )
    parser.add_argument(
        '--output-dir',
        default='./outputs',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    # Validate seed hub exists
    if not os.path.exists(args.seed_hub):
        print(f"ERROR: Seed Hub file not found: {args.seed_hub}")
        sys.exit(1)
    
    # Run pipeline
    pipeline = AITalentPipeline(args.mode, args.seed_hub, args.output_dir)
    result = pipeline.run()
    
    print("\n" + "="*80)
    if result['status'] == 'FAILED':
        print("❌ PIPELINE EXECUTION FAILED")
        if result.get('enumeration_failed'):
            print("   REASON: Enumeration returned 0 individuals")
            print("   LIKELY CAUSE: Network blocking or API access failure")
            print("   ACTION REQUIRED: Verify network access to api.github.com")
    else:
        print("✅ PIPELINE EXECUTION COMPLETE")
    print("="*80)
    print(f"Status: {result['status']}")
    print(f"Records processed: {result['records_processed']}")
    print(f"Records quarantined: {result['records_quarantined']}")
    print(f"Output files: {result['output_files']}")
    print(f"Preview: {result['preview_file']}")
    print("="*80)
    
    # Exit with appropriate code
    if result['status'] == 'FAILED':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
