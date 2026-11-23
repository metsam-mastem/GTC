# Gadget Time Capsule (GTC)

**Universal Historical & Engineering Atlas of Digital Devices**

GTC is a source-traceable, extensible knowledge base for the history, identity, architecture, components, software, repair, and reverse engineering of digital devices.

## Mission
- Preserve the history of mobile phones and the wider universe of computing and electronic devices.
- Give every product model and hardware variant a stable identity record.
- Connect devices to manufacturers, components, chipsets, standards, firmware, documents, images, and engineering evidence.
- Make uncertainty, provenance, licensing, and verification status explicit.
- Support research, repair, education, interoperability, and lawful hardware analysis.

## Scope
1. Mobile phones, feature phones, smartphones, satellite phones, PDAs.
2. Tablets, e-readers, wearables, cameras, audio and gaming devices.
3. Laptops, desktops, workstations, servers, thin clients, legacy computers.
4. Motherboards, PCBs, CPUs, GPUs, SoCs, MCUs, memory, storage, power and connectivity modules.
5. Networking, embedded, IoT, robotics, automotive, industrial, scientific and energy devices.

## Core principles
- A product family, marketed model, regional SKU, carrier variant, board revision, and component are distinct entities.
- Never merge variants merely because their marketing names look similar.
- Every important factual claim should carry a source, retrieval date, and verification status.
- Separate manufacturer-published facts, third-party specifications, physical observations, software extraction, and engineering inference.
- Respect source licenses, copyright, access controls, privacy, and applicable law.
- Do not claim complete global coverage without measurable evidence.

## Repository map
- `docs/ARCHITECTURE.md` — system architecture and design decisions.
- `docs/TAXONOMY.md` — universal device taxonomy.
- `docs/DEVICE_IDENTITY_SCHEMA.md` — canonical device identity and dossier schema.
- `docs/SOURCES_AND_INGESTION.md` — source registry, ingestion, provenance and validation.
- `data/` — structured device records, organized by entity type.
- `schemas/` — machine-readable JSON Schemas.
- `templates/` — dossier templates.
- `media/` — lightweight original assets and metadata; large binaries should use an appropriate external/LFS store.
- `research/` — historical and engineering research notes.

## Status
Foundation initialized. Device coverage has not yet been populated or audited. This repository must not be described as a complete device catalogue.

## First milestone
Build and validate the canonical data model, then seed a historically representative mobile-phone dataset with cited evidence before expanding to laptops and other hardware families.
