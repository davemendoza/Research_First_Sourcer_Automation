# Publish or Perish → GPT Canonical Scholar Input Schema
Version: v1.0  
Maintainer: L. David Mendoza © 2025  
System: AI Talent Engine – Signal Intelligence  
Scope: Google Scholar–derived evidence via Publish or Perish (PoP)

---

## 1. Purpose

This document defines the **canonical, enforceable input schema** for all Google Scholar–derived data supplied to the AI Talent Engine.

The AI Talent Engine **does not access Google Scholar directly**.  
All Scholar-based evidence must be provided through **Publish or Perish (PoP)** exports or equivalent Scholar-derived structured datasets.

This schema ensures:
- Evidence integrity
- Deterministic evaluation
- Audit readiness
- Policy compliance
- Demo safety

Any Scholar-derived input **not conforming** to this schema is considered **invalid**.

---

## 2. Accepted Input Formats

Scholar-derived data must be supplied in **one or more** of the following structured formats:

- CSV
- JSON
- Markdown table

Raw URLs, screenshots, PDFs, or free-text descriptions **are not valid inputs**.

---

## 3. Required Author-Level Fields (MANDATORY)

Every Scholar-derived dataset **must include** the following author-level fields:

| Field Name | Type | Description |
|----------|------|-------------|
| author_name | string | Full legal or professional name |
| affiliation | string | Primary institutional or organizational affiliation |
| source | string | Must be exactly: `Google Scholar via Publish or Perish` |
| export_timestamp | ISO-8601 string | Timestamp of PoP export |
| total_citations | integer | Total citation count |
| h_index | integer | h-index |
| i10_index | integer | i10-index |
| citations_per_year | integer[] or map | Yearly citation counts |

If **any required author-level field is missing**, the dataset is invalid.

---

## 4. Optional Author-Level Fields

| Field Name | Type | Description |
|----------|------|-------------|
| orcid | string | ORCID identifier |
| scholar_user_id | string | Google Scholar profile ID |
| research_areas | string[] | Declared research interests |
| career_start_year | integer | First publication year |
| career_end_year | integer or null | If inactive |

---

## 5. Required Publication-Level Fields (MANDATORY)

Each publication record **must include**:

| Field Name | Type | Description |
|----------|------|-------------|
| publication_title | string | Full title |
| publication_year | integer | Year of publication |
| venue | string | Journal, conference, or archive |
| citation_count | integer | Citations for this work |
| authors | string[] | Author list |
| publication_type | enum | journal, conference, preprint, book_chapter |

Publications missing required fields **must be discarded**, not inferred.

---

## 6. Normalization Rules

- Citation counts must be integers
- Venue names must not be inferred or expanded
- Duplicate publications merged by title + year
- No synthetic or estimated metrics allowed

---

## 7. Prohibited Inputs (HARD FAIL)

The following inputs are forbidden:
- Live Google Scholar URLs
- HTML scrapes
- CAPTCHA-bypassed data
- Estimated or hallucinated metrics

Any presence invalidates the dataset.

---

## 8. GPT Interpretation Rules

When schema is satisfied, GPT may:
- Compute citation velocity
- Classify research impact
- Evaluate field relevance
- Feed results into evaluation templates

GPT must **not** guess or backfill missing data.

---

## 9. Governance & Validation

Enforced by Governance Agents:
#21 Schema Validator  
#22 Audit & Provenance  
#24 Compliance  
#36 Integrity  

---

## 10. Versioning

- v1.0 Initial release
- Future revisions must be versioned

---

## 11. Canonical Statement

Scholar-derived evidence enters the AI Talent Engine **only** as structured data conforming to this schema.

© 2025 L. David Mendoza. All rights reserved.
