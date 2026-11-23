# GTC Automation Runtime

## Purpose
Provide a repeatable, low-cost runtime that continues repository quality checks when a chat session is closed. This is repository automation, not a persistent AI agent; it does not autonomously invent or publish device facts.

## Runtime components
- Local CLI: tools/gtc_runtime.py
- Dataset adapter: tools/importers/import_techapi.py
- Unit tests: tests/
- Push and pull-request gate: .github/workflows/validate.yml
- Scheduled source monitoring: .github/workflows/source-audit.yml

## Local commands
- validate --strict: check source registry, records, IDs, evidence, dates, references and prohibited personal fields.
- build-index: build derived catalogue index and coverage counts under generated/.
- source-audit: perform rate-limited HTTP checks for selected sources and write generated/source-health.json.
- unittest: run deterministic regression tests using Python's standard library.

## Scheduled operation
GitHub Actions validates every push and pull request. A weekly source-health workflow checks selected source endpoints and uploads a report artifact. Workflows use read-only repository permissions and do not commit or publish generated data.

## Controlled ingestion
Ingestion is explicit and human-triggered. The TechAPI adapter reads selected local JSON files from a TechAPI data checkout. It does not crawl the web, bypass rate limits, clone the full upstream repository, or commit imported data. It writes reviewable GTC draft records. Imported claims start as UNVERIFIED and retain the TechAPI record URL and original source_urls.

## Cost and reliability
- No paid external API is required.
- Runtime depends only on Python standard library.
- Source checks have a short timeout and fixed allowlist.
- Network source checks are isolated from data validation.
- Workflows are read-only and upload generated artifacts; they do not push commits.
- Large datasets and binaries are not downloaded as part of ordinary CI.

## Extension points
A later runtime may add SQLite/FTS5 export, API builds, visual atlas generation, more import adapters, coverage-gap detection and manual source refresh. Add these behind explicit CLI commands and reproducible tests.
