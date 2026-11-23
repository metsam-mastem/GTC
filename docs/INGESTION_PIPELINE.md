# GTC Ingestion Pipeline

1. Discover a candidate entity or dataset.
2. Inspect authority, license, terms, scope and freshness.
3. Acquire only data required for the defined import batch.
4. Preserve upstream identifiers, revision, original strings and source locator.
5. Normalize names, units, dates and categories.
6. Resolve identity against current GTC records.
7. Detect duplicate names, model codes, aliases and likely rebrands.
8. Build claim-level provenance; preserve conflicts as separate claims.
9. Run privacy, schema, license and integrity checks.
10. Review and merge through Git.

## Adapter contract
Each adapter documents upstream URL and revision, license, supported categories, field mapping, skipped fields, deduplication policy, request limits, and fixture tests. Adapters are isolated and deterministic.

## TechAPI
The initial adapter reads selected local TechAPI JSON files. It does not clone the upstream data repository, crawl websites, or make network requests. The dataset is CC BY-SA 4.0. Import requires --confirm-license, preserves source_urls and attribution, and marks imported claims UNVERIFIED. It never overwrites existing records without an explicit flag.

## No silent overwrite
A future updater should generate a reviewable diff or patch. It must not automatically replace accepted GTC data.
