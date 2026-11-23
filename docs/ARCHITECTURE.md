# GTC Architecture

## 1. Architectural model
GTC uses a data-first, repository-native, modular architecture. Git is the reviewable source of truth for schemas, curated records, documentation, and change history. Runtime services and large binary storage remain replaceable.

### Layers
1. Experience: web atlas, search, filters, timeline, device explorer, visual component maps.
2. Knowledge: entity registry, taxonomy, identity resolution, relationships, knowledge graph.
3. Evidence: specifications, sources, documents, images, schematics, firmware metadata, test observations.
4. Ingestion and validation: import adapters, parsers, normalization, deduplication, provenance, schema validation, quality gates.
5. Foundation: identifiers, ontology, versioning, licensing policy, security and governance.

## 2. Entity model
Do not model everything as a single flat "device" table. Use linked entities:
- Manufacturer / Brand
- ProductFamily
- ProductModel (marketed model)
- ProductVariant (region, carrier, storage, radio or board variant)
- HardwareRevision / Board
- Component / Part
- SoC / CPU / GPU / MCU / Modem
- OperatingSystem / Firmware / SoftwareRelease
- Standard / Protocol / Interface
- Document / Image / Dataset / Source
- Test / Observation / RepairProcedure
- Facility / Factory (only when supported by evidence)

## 3. Identity hierarchy
Manufacturer -> Brand -> Product Family -> Product Model -> Product Variant -> Hardware Revision -> Board Assembly -> Component.

A model name is not a unique identifier. Prefer manufacturer model codes, regulatory identifiers, board codes, codenames and source-specific identifiers as aliases attached to a canonical GTC ID.

Suggested ID pattern:
- GTC-MOB-{BRAND}-{MODEL}
- GTC-CMP-{TYPE}-{MFR}-{PART}
- GTC-COM-{CLASS}-{BRAND}-{MODEL}
- GTC-GAD-{CLASS}-{BRAND}-{MODEL}

IDs are immutable. Corrections to names or classification do not change an established ID. If identity is uncertain, create a provisional record rather than guessing.

## 4. Data architecture
- Canonical records: JSON, one entity per file.
- Validation: JSON Schema, deterministic validators and CI.
- Initial local query: SQLite + FTS5.
- Optional hosted scale: PostgreSQL; search service only when justified by measured need.
- Interchange: JSON-LD where semantic linking is useful; CSV for tabular exports.
- API: versioned REST with OpenAPI.
- Media: metadata and hashes in Git; large binaries in Git LFS or separately governed object storage.
- Diagrams: SVG, Mermaid, and source files for editable engineering diagrams.

Avoid making a graph database mandatory at the beginning. Derive graph views from canonical linked records; adopt a dedicated graph engine only when query complexity and scale justify it.

## 5. Evidence and confidence
Each claim should be represented with:
- subject entity and field
- value and unit, where applicable
- source ID and source locator
- source publication/release date, if known
- retrieval date
- evidence type: manufacturer, regulatory, standards body, reputable secondary source, community documentation, physical observation, software extraction, engineering inference
- verification status: VERIFIED, CORROBORATED, UNVERIFIED, CONFLICTED, DEPRECATED
- confidence rationale and reviewer

Do not silently overwrite conflicting values. Preserve competing claims and document resolution.

## 6. Ingestion pipeline
Discover -> acquire metadata -> check license/access conditions -> parse -> normalize -> resolve identity -> deduplicate -> validate -> attach provenance -> human review -> merge -> publish.

Use polite, rate-limited acquisition. Prefer official APIs, downloadable datasets and documented repositories. Do not bypass authentication, paywalls, technical restrictions or access controls.

## 7. Governance
- Schema changes require versioning and migration notes.
- Data changes should be small, reviewable commits.
- Every imported dataset requires a source and license review.
- No unsupported "complete" labels.
- CI should validate JSON, IDs, references, required provenance, duplicate aliases and link integrity.
- Use statuses: PASS, FAIL, NOT RUN, BLOCKED.
- Keep research observations separate from accepted facts.

## 8. Suggested implementation stack
Start with JSON + JSON Schema + Python validation + SQLite FTS5 + static web frontend. Add React/TypeScript, API and PostgreSQL as the use case matures. Keep every service replaceable and support offline export.

## 9. Non-goals for the foundation
- No immediate scraping of every commercial database.
- No assumption that every model has public schematics or firmware.
- No storage of copyrighted manuals/images without a compatible license or permission.
- No reverse engineering that bypasses security protections or targets unauthorized access.
