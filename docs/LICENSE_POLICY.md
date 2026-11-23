# GTC License and Third-Party Data Policy

## Separation of rights
- Code in this repository is MIT-licensed.
- Original curated GTC database contributions are CC BY-SA 4.0.
- Third-party datasets, text, images, manuals, schematics, firmware, PCB layouts and documents retain their individual rights and terms.
- GTC's data license never overrides an upstream license or grants rights GTC does not hold.

## Ingestion classes
- ALLOW: explicit license permits intended reuse and required attribution is recorded.
- SHAREALIKE: reuse is allowed only with attribution and compatible share-alike treatment.
- CONDITIONAL: reuse depends on scope, attribution, image or other conditions.
- FACTS_AND_LINKS_ONLY: record independently written factual values and links; do not copy source prose, tables, images or files.
- LEAD_ONLY: use to discover a model or locate a primary source; do not copy its data into the distributable GTC dataset.
- BLOCKED: no ingestion until rights and access conditions are resolved.

## Source-specific rules
- TechAPI data is CC BY-SA 4.0. Attribute it as "Data from TechAPI" and link https://github.com/GetTechAPI/TechAPI. Derived dataset material must retain compatible CC BY-SA terms. TechAPI code is separately MIT-licensed.
- TechEngine code is MIT-licensed. It is an ingestion/validation engine, not the device data source.
- DeviceFarmer/stf-device-db is Apache-2.0 at repository level. Its database is incomplete and regionally biased; image files and other third-party assets need individual checks.
- KHwang9883/MobileModels is CC BY-NC-SA 4.0. It is non-commercial. Treat it as a research lead only; do not copy its records into a commercial or distributable GTC dataset.
- RightToRepairMobile/open-device-db has an MIT code LICENSE, while its README makes a separate data-license statement. Do not ingest its database until the exact data terms and provenance are verified. Its device-instance schema includes IMEI and ownership fields; GTC must not ingest those records.
- Unknown or scraped datasets are not approved merely because a GitHub repository is public.

## Images and documents
A product photograph, teardown image, service manual, boardview, schematic or firmware file may have a separate creator and license. Store URL and asset metadata when redistribution is not permitted. Do not mirror images or documents without applicable permission.

## Personal and security-sensitive data
GTC is a product/model engineering atlas, not a registry of identifiable people's devices. Never store IMEI, IMSI, phone numbers, account identifiers, owner names, serial-number-to-owner mappings, personal diagnostic logs or device-instance tracking data. Exclude secrets, credentials, private firmware keys and personal dumps.

## Review checklist
1. Identify exact dataset/file and owner.
2. Identify the license applying to data, not just code.
3. Check attribution and share-alike obligations.
4. Check image/document rights separately.
5. Check for personal and security-sensitive material.
6. Record retrieval date, upstream revision and original source links.
7. Keep imported claims UNVERIFIED until GTC independently reviews them.
