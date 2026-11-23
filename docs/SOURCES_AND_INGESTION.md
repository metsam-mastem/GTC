# Sources, Provenance and Ingestion

## 1. Source classes
1. Manufacturer: official product pages, press releases, manuals, support pages, service bulletins.
2. Regulatory: FCC equipment authorization, regional radio approvals and certification records.
3. Standards bodies: 3GPP, IEEE, USB-IF, Bluetooth SIG and relevant standards organizations.
4. Open-source projects: Linux kernel, device trees, LineageOS, coreboot and board/vendor repositories.
5. Repair and teardown: iFixit and reputable repair documentation.
6. Structured datasets: Wikidata and open device/specification repositories.
7. Community research: forums, repair communities, enthusiast databases and archived material.
8. Physical/software observation: teardown photos, markings, measurements, logs and reproducible tests.

## 2. Initial discovery references
These are candidate sources, not automatically approved data feeds:
- https://github.com/GetTechAPI/TechAPI — structured consumer-electronics dataset; repository describes CC-BY-SA 4.0.
- https://github.com/openstf/stf-device-db — JSON database of smartphones, tablets and wearables; its README warns coverage is incomplete and development moved to DeviceFarmer.
- https://github.com/KHwang9883/MobileModels — model names, model codes and codenames across device families.
- https://github.com/bytecharts/device_specs_gsmarena — scraped specifications dataset; review upstream terms and dataset provenance before reuse.
- https://opendevicedb.org/ — directory of device research, open firmware and protocols.
- https://github.com/RightToRepairMobile/open-device-db — community repair and device information database; inspect repository status and licensing.
- https://www.wikidata.org/
- https://www.ifixit.com/
- https://www.fcc.gov/oet/ea
- https://www.3gpp.org/
- https://www.kernel.org/
- https://lineageos.org/
- https://www.coreboot.org/
- https://www.usb.org/
- https://www.bluetooth.com/specifications/

## 3. Source registry fields
source_id, name, source_type, canonical_url, owner, license, terms_url, attribution_text, access_method, data_scope, known_limitations, last_checked_at, approved_for_ingestion, notes.

## 4. Ingestion workflow
Discover -> inspect source and license -> capture metadata -> acquire permitted data -> parse -> normalize -> map aliases -> resolve entities -> detect duplicates -> attach claim-level provenance -> validate -> human review -> commit.

## 5. Validation
- JSON Schema validation
- unique GTC IDs
- no dangling entity references
- valid source IDs for sourced claims
- units normalized to declared units
- dates represented in ISO 8601
- preserve original source strings alongside normalized values
- detect duplicate model codes and aliases
- check license and attribution metadata for every imported asset/dataset
- identify missing and conflicting values
- record retrieval timestamps and source version/commit where possible

## 6. Acquisition policy
Prefer official APIs, downloadable datasets and repository releases. Respect robots policies, rate limits, license terms and access controls. Do not evade paywalls, authentication, anti-bot systems or technical protection measures. Do not ingest private data or personal data. Firmware and service documents may have redistribution restrictions; metadata/link-only records may be appropriate.

## 7. Coverage reporting
Report coverage by category, manufacturer, era, market and evidence depth. Separate:
- known entities
- identified models
- models with basic metadata
- models with sourced specifications
- models with engineering documentation
- models reviewed for quality

Never equate a large number of scraped records with completeness or correctness.
