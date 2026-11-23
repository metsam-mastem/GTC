# GTC Device Identity and Dossier Schema

## 1. Purpose
Every model receives a stable identity record and an extensible dossier. A dossier is a structured collection of linked facts and evidence, not a single unstructured page.

## 2. Recommended top-level fields
- gtc_id: immutable canonical identifier
- entity_type: device_model | device_variant | hardware_revision | component | module
- lifecycle_status: announced | released | discontinued | unknown
- canonical_name
- manufacturer_id
- brand_id
- product_family_id
- model_codes: array of exact manufacturer/regulatory/operator codes
- codenames: array with source and context
- aliases: names and spelling variants
- category_ids: multi-label taxonomy
- announcement_date, release_date, end_of_sale_date, end_of_support_date
- markets: regions/countries and market-specific variant references
- physical: dimensions, mass, materials, form factor
- hardware: SoC, CPU, GPU, NPU, memory, storage, display, cameras, sensors, audio, connectivity, power
- board: board code, revision, assembly, PCB metadata
- software: operating systems, versions, bootloader, firmware, drivers
- regulatory: FCC ID, certification identifiers, radio approvals
- repair: serviceability, known faults, procedures, parts
- reverse_engineering: observations, diagrams, test results and lawful analysis notes
- media: images, diagrams, video and asset metadata
- documents: manuals, datasheets, service documents, patents and reports
- relationships: successor, predecessor, regional_variant_of, rebrand_of, uses_component, board_revision_of, supported_by
- claims: source-backed field-level assertions
- created_at, updated_at, schema_version

## 3. Field-level evidence
Important values must be traceable to a claim record:
- claim_id
- subject_id
- predicate / field_path
- value
- unit
- source_id
- source_locator
- evidence_type
- publication_date
- retrieved_at
- verification_status
- confidence_note
- reviewer

A record can contain multiple claims for one field when sources disagree. The accepted display value must point to the chosen claim and explain the resolution.

## 4. Dossier sections
1. Identity and naming
2. Historical timeline
3. Manufacturer and market
4. Model and regional variants
5. Physical design and dimensions
6. Hardware architecture and block diagram
7. PCB and board revisions
8. Semiconductor and component inventory
9. Display, camera, audio and sensors
10. RF, antennas and connectivity
11. Power, battery and charging
12. Operating system and software stack
13. Boot chain, partitions and firmware
14. Security architecture
15. Repair, disassembly and parts
16. Fault analysis and diagnostics
17. Reverse-engineering observations and test records
18. Documents, media and references
19. Related models, platforms and components
20. Completeness and evidence assessment

## 5. Variant discipline
Never assume two devices are identical based only on their retail name. Record regional SKU, carrier model, radio bands, SoC, board code/revision, memory configuration, display supplier and firmware branch where known. Use separate variant entities when material hardware/software differences exist.

## 6. Example ID
GTC-MOB-SAM-GT-I9300 is an illustrative identifier for a Samsung Galaxy S III GT-I9300 dossier. It is not a globally unique manufacturer identifier.

## 7. Completeness states
- NOT STARTED
- IDENTIFIED
- BASIC PROFILE
- SPECIFICATIONS SOURCED
- HARDWARE DOCUMENTED
- SOFTWARE DOCUMENTED
- ENGINEERING EVIDENCE
- REVIEWED
- CONFLICTED
- BLOCKED

A completion state must be computed from required fields and evidence rules, not manually inflated.

## 8. Media asset metadata
For each asset record: asset_id, related_entity_id, asset_type, title, creator, source_url, license, attribution, retrieval_date, file_hash, dimensions, file_format, revision, notes. Store only assets that may lawfully be redistributed; otherwise store a link and descriptive metadata.
