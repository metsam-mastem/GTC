# GTC Canonical Data Model

## Entity types
- Manufacturer / brand: registered in the manufacturer registry.
- Device model: marketed product identity.
- Device variant: material market, radio, storage, carrier or hardware revision difference.
- Component: reusable semiconductor, module, board or replaceable part.
- Source: evidence provider with licensing and acquisition policy.
- Claim: one source-backed assertion about one field.
- Asset: separately licensed image, document, diagram, firmware or measurement artifact.

## Identity
A canonical GTC ID is immutable. Product names, manufacturer model codes, board IDs, regulatory IDs and codenames are different identifier classes. A model can have many variants; a variant can have many revisions; a revision can contain many board assemblies and components.

## Claim-level provenance
Display fields are convenient summaries. The claims list preserves why each value is present. Multiple claims may target one field. If sources disagree, retain both and mark the record or field CONFLICTED rather than silently overwriting.

## Relationship vocabulary
successor_of, predecessor_of, variant_of, regional_variant_of, carrier_variant_of, rebrand_of, sold_as, uses_component, used_by, board_revision_of, compatible_with, accessory_for, runs_software, supported_by, derived_from, based_on.

Relations are directed, typed and target a GTC ID. Factual relations should carry supporting claims.

## Variant splitting
Create a separate variant when model code, regional SKU, radio bands/modem/RF front-end, SoC/mainboard, materially relevant display/camera/sensor supplier, memory/storage SKU, power/mechanical package or firmware branch differs in a way relevant to research or repair. Do not split merely for color or retail bundle without a research reason.

## Units
Use SI units where appropriate: mm, g, mAh, V, MHz, GHz, GB (decimal). Use MiB/GiB only where source notation requires them. Preserve the original source representation in claim notes.

## Lifecycle
DISCOVERED -> IDENTIFIED -> BASIC_PROFILE -> SPECIFICATIONS_SOURCED -> HARDWARE_DOCUMENTED / SOFTWARE_DOCUMENTED -> ENGINEERING_EVIDENCE -> REVIEWED.

CONFLICTED and BLOCKED are side states. Completeness is evidence-driven and conservative.
