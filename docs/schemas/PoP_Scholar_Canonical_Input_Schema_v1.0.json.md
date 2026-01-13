{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "PoP_Scholar_Canonical_Input_Schema_v1.0.json",
  "title": "PoP → GPT Canonical Scholar Input Schema",
  "version": "v1.0",
  "maintainer": "L. David Mendoza © 2025",
  "system": "AI Talent Engine – Signal Intelligence",
  "description": "Canonical schema for Google Scholar–derived evidence supplied via Publish or Perish (PoP). Direct Scholar access is prohibited.",
  "type": "object",
  "required": [
    "author",
    "metrics",
    "publications",
    "source",
    "export_timestamp"
  ],
  "properties": {
    "author": {
      "type": "object",
      "required": [
        "author_name",
        "affiliation"
      ],
      "properties": {
        "author_name": {
          "type": "string",
          "minLength": 1
        },
        "affiliation": {
          "type": "string",
          "minLength": 1
        },
        "orcid": {
          "type": ["string", "null"],
          "pattern": "^\\d{4}-\\d{4}-\\d{4}-\\d{3}[\\dX]$"
        },
        "scholar_user_id": {
          "type": ["string", "null"]
        },
        "research_areas": {
          "type": ["array", "null"],
          "items": {
            "type": "string"
          }
        },
        "career_start_year": {
          "type": ["integer", "null"],
          "minimum": 1900,
          "maximum": 2100
        },
        "career_end_year": {
          "type": ["integer", "null"],
          "minimum": 1900,
          "maximum": 2100
        }
      },
      "additionalProperties": false
    },
    "metrics": {
      "type": "object",
      "required": [
        "total_citations",
        "h_index",
        "i10_index",
        "citations_per_year"
      ],
      "properties": {
        "total_citations": {
          "type": "integer",
          "minimum": 0
        },
        "h_index": {
          "type": "integer",
          "minimum": 0
        },
        "i10_index": {
          "type": "integer",
          "minimum": 0
        },
        "citations_per_year": {
          "type": "object",
          "additionalProperties": {
            "type": "integer",
            "minimum": 0
          }
        }
      },
      "additionalProperties": false
    },
    "publications": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": [
          "publication_title",
          "publication_year",
          "venue",
          "citation_count",
          "authors",
          "publication_type"
        ],
        "properties": {
          "publication_title": {
            "type": "string",
            "minLength": 1
          },
          "publication_year": {
            "type": "integer",
            "minimum": 1900,
            "maximum": 2100
          },
          "venue": {
            "type": "string",
            "minLength": 1
          },
          "citation_count": {
            "type": "integer",
            "minimum": 0
          },
          "authors": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string"
            }
          },
          "publication_type": {
            "type": "string",
            "enum": [
              "journal",
              "conference",
              "preprint",
              "book_chapter"
            ]
          }
        },
        "additionalProperties": false
      }
    },
    "source": {
      "type": "string",
      "const": "Google Scholar via Publish or Perish"
    },
    "export_timestamp": {
      "type": "string",
      "format": "date-time"
    }
  },
  "additionalProperties": false
}
