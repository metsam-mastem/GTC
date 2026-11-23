# Gadget Time Capsule (GTC)

**Universal Historical, Device Knowledge and Engineering Atlas**

GTC is a modular, source-traceable atlas for the history, identity, hardware, software, repair and lawful engineering analysis of digital devices.

## Current foundation
- Stable device and component identity model.
- Claim-level provenance and evidence statuses.
- Universal hardware taxonomy and source registry.
- Cited starter dossiers for mobile phones, laptops and single-board computers.
- Standard-library Python runtime for validation, catalogue indexing and source-health checks.
- Controlled TechAPI importer with provenance and license handling.
- GitHub Actions validation and scheduled source-health monitoring.

## Repository map
- docs/ — architecture, taxonomy, data model, source and license policy.
- schemas/ — machine-readable JSON contracts.
- data/registry/ — taxonomy, manufacturers and source registry.
- data/mobile/, data/computing/, data/components/ — canonical records.
- tools/ — local runtime and controlled import adapters.
- templates/ — reusable dossier templates.
- tests/ — runtime tests.
- site/ — Persian responsive web atlas and offline-capable PWA shell.
- .github/workflows/ — automated validation, source monitoring and Pages deployment.
- generated/ — derived local/CI outputs, not canonical source data.

## Run locally
Requires Python 3.10+ and no third-party packages.

    python tools/gtc_runtime.py validate --strict
    python tools/gtc_runtime.py build-index
    python -m unittest discover -s tests -v
    python -m http.server 8000 --directory site

Import selected local TechAPI JSON records after reviewing its CC BY-SA 4.0 data terms:

    python tools/importers/import_techapi.py path/to/record.json --source-root path/to/TechAPI/data --confirm-license --dry-run

Imported claims remain UNVERIFIED in GTC until independently reviewed.

## Evidence discipline
A model name is not a unique product identity. Regional SKUs, operator versions, hardware revisions and board variants must remain distinguishable. Factual claims carry their own source, locator, retrieval date, evidence type and verification status. An upstream verified flag is never automatically promoted to GTC verification.

## Coverage statement
This is an extensible foundation and a small, cited starter catalogue, not a complete global inventory. Coverage must be measured by family, manufacturer, era, market, variants and evidence depth.

## Licensing
- Repository code: MIT; see LICENSE.
- Original curated GTC database contributions: CC BY-SA 4.0; see DATA_LICENSE.md.
- Third-party datasets and media retain their own source licenses and conditions. See docs/LICENSE_POLICY.md.

## Principles
Source first. No fabricated specifications. No hidden merges. No copied restricted media. No personal-device identifiers. No unsupported completeness claims.
