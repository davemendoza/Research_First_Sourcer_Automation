# AI Talent Engine - Signal Intelligence Pipeline

© 2025-2026 L. David Mendoza. All Rights Reserved.  
Proprietary and Confidential

## System Overview

The AI Talent Engine is a research-grade automation system for authentic AI-engineering talent discovery, verification, and governance.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### DEMO Mode (≤50 rows)
```bash
python main_pipeline.py --mode demo --seed-hub path/to/AI_Talent_Engine_Seed_Hub.xlsx
```

### GPT-SLIM Mode (23 fields, ≤50 rows)
```bash
python main_pipeline.py --mode gpt_slim --seed-hub path/to/AI_Talent_Engine_Seed_Hub.xlsx
```

### SCENARIO Mode (unlimited rows)
```bash
python main_pipeline.py --mode scenario --seed-hub path/to/AI_Talent_Engine_Seed_Hub.xlsx
```

### Custom Output Directory
```bash
python main_pipeline.py --mode demo --seed-hub path/to/seed_hub.xlsx --output-dir ./my_outputs
```

## Output Files

Each run generates:
- **Excel file**: `AI_Talent_{MODE}_{TIMESTAMP}.xlsx` (gold standard format)
- **CSV file**: `AI_Talent_{MODE}_{TIMESTAMP}.csv`
- **Validation report**: `validation_report_{MODE}_{TIMESTAMP}.json`
- **Audit log**: `audit_log_{MODE}_{TIMESTAMP}.txt`
- **Talent preview**: `talent_preview_{MODE}_{TIMESTAMP}.html`
- **Quarantine file**: `quarantine_{MODE}_{TIMESTAMP}.json` (if any rows failed)

## Modules

1. **seed_hub_parser.py** - Parse Seed Hub Excel with deduplication
2. **evidence_enricher.py** - Enrich with GitHub, Kaggle, publications, patents
3. **contact_scraper.py** - Active scraping of emails, phones, locations
4. **role_classifier.py** - Classify into 27 canonical AI roles
5. **citation_calculator.py** - Fetch citations from Scholar APIs
6. **schema_validator.py** - Validate schema (Agents #21-24, #36)
7. **output_generator.py** - Generate Excel/CSV outputs
8. **talent_preview.py** - Generate HTML preview
9. **main_pipeline.py** - Main orchestrator

## Schema Compliance

- Schema Version: v3.3 Extended
- Governance Agents: #21, #22, #23, #24, #36
- Evidence Hierarchy: Code > Papers > Patents > Models > Portfolios
- Canonical Roles: 27 AI role types (see ai_role_registry.py)

## Contact Scraping Sources

- GitHub profiles
- GitHub.io personal sites
- Kaggle profiles
- CV/resume pages
- Blog URLs
- Conference speaker pages

## Citation Data Sources

1. Semantic Scholar API (primary)
2. OpenAlex API (secondary)
3. Google Scholar (manual only - no official API)

## Deduplication Checks

- Exact URL match
- Normalized URL match
- GitHub username match
- Organization + enumeration target match

## Governance Rules

- Public-source data only
- No inferred or fabricated data
- No private or gated scraping
- Deterministic, audit-ready execution
- Evidence provenance required

## Error Handling

- Invalid rows are skipped (not halted)
- Quarantined rows saved separately
- Full audit trail maintained
- Validation reports generated

## License

All rights reserved. Unauthorized use prohibited.
