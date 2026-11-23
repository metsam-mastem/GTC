# Source Audit and Dataset Strategy

Last checked: 2026-11-23. Public project metadata and documentation were inspected. This is a source-selection assessment, not a legal opinion or a claim that every upstream record is correct.

| Source | Coverage / role | Declared license | GTC use | Limitation |
|---|---|---|---|---|
| GetTechAPI/TechAPI | Curated smartphones, tablets, watches, PDAs, laptops, monitors, CPUs, GPUs, SoCs and brands | Dataset CC BY-SA 4.0; code MIT | Primary structured seed candidate with attribution and share-alike | Curated subset, not exhaustive; record quality varies; repository is very large, so use selected-file or local sparse ingestion |
| GetTechAPI/TechEngine | Validation, API, collectors, coverage and verification engine | MIT code | Study and selectively adapt patterns | Coupled to TechAPI schemas; not itself the device dataset |
| DeviceFarmer/stf-device-db | JSON phone/tablet/wearable model records, regional codes and basic specs | Apache-2.0 repository license | Secondary model-code discovery; review media rights | README describes coverage as incomplete and mainly Japanese-market focused |
| KHwang9883/MobileModels | Brand/model names, market codes and codenames | CC BY-NC-SA 4.0 | Lead-only | Non-commercial restriction makes it unsuitable for a commercial redistributable GTC dataset |
| RightToRepairMobile/open-device-db | Phone specifications, repair, firmware and repairability schema | MIT code; data license needs separate confirmation | Schema and feature reference only | README has a separate CC BY-SA data claim; verify exact data grant and provenance. Its schema includes personal device-instance fields that GTC excludes |
| bytecharts/device_specs_gsmarena | Scraped phone specification records | Not approved; verify rights | Lead-only | Dataset provenance and redistribution terms not established |
| Wikidata | Linked entities and identifiers across device history | CC0 for structured data | Entity reconciliation and historical discovery | Community-maintained and uneven; statement-level references still required |
| Apple Support | Apple model identifiers and year introduced | Copyrighted support content | Factual citation only | Do not copy prose or images |
| Motorola Solutions heritage | Corporate history of DynaTAC | Copyrighted web content | Manufacturer-history reference | Does not provide a full engineering dossier |
| Trinity College Dublin SCSSTreasures | Physical artifact/manual catalogue and historic phone records | Terms to review | Historical evidence and artifact references | Nokia 1011 page quotes Wikipedia for several specifications; not independent corroboration |
| OldThinkPad | Transcribed IBM historical service references | Terms to review | Technical lead and service-document discovery | Community transcription; consult linked original IBM manuals before servicing |
| Raspberry Pi Documentation | Official board and revision references | Copyrighted docs | Factual citation only | Distinguish board revision and memory variants |
| FCC OET | Equipment authorization records | Record-specific terms | Regulatory identifiers and RF evidence | Filing may apply to a specific radio variant and may omit retail specifications |
| 3GPP | Cellular standards and releases | Standards publication rights apply | Standard/version linkage | Link official specification and version; do not mirror protected documents without permission |
| Linux Kernel | Driver, device-tree and subsystem support | GPL-2.0-only for kernel code; docs vary | Software-support evidence | Driver support does not establish complete product BOM |
| LineageOS | Device support, codenames and build configuration | Mixed repository/file licenses | Firmware and software-support evidence | Community support is not manufacturer support; variants may differ |

## Practical source strategy
1. Use TechAPI as the high-leverage structured source for modern and historical consumer hardware, importing selected records and preserving CC BY-SA provenance.
2. Use DeviceFarmer as a complementary discovery source for model-code and regional-device reconciliation.
3. Use MobileModels only to discover candidates and aliases; do not ingest its non-commercial records.
4. Use manufacturer and regulator sources to verify important specifications and exact model codes.
5. Use repair communities and device-specific repositories for engineering depth, not as substitutes for primary identity sources.
6. Use Wikidata for graph discovery, not as the sole technical authority.

## Size and acquisition
TechAPI's GitHub metadata reported a very large repository size on the audit date. Avoid full clones in routine development and CI. Prefer selected raw JSON files, sparse checkout or reviewed snapshots. DeviceFarmer's database is also sizeable and regionally incomplete; do not pull its full asset set into GTC by default.


## Additional primary sources added to the catalogue
- Apple Mac model identification: https://support.apple.com/en-us/102869 — model identifier and externally visible model identification.
- Apple MacBook Air M1 technical specifications: https://support.apple.com/en-us/111883 — manufacturer-published configuration and hardware data.
- Qualcomm Snapdragon 8 Elite launch: https://www.qualcomm.com/news/releases/2024/10/qualcomm-unveils-snapdragon-8-elite-with-the-world-s-fastest-mob — official 21 October 2024 press note.
- Qualcomm Snapdragon 8 Elite Product Brief: https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/images/company/news-media/media-center/press-kits/snapdragon-summit-2024/day-1/documents/Snapdragon8EliteProductBrief.pdf — official platform technical brief, including CPU, GPU, NPU, connectivity, memory and SM8750-AB part number.
