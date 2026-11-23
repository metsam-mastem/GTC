# GTC Explorer

A dependency-free responsive static web application in site/.

## Features
- Search model name, manufacturer, GTC ID, model codes, codenames, aliases and selected technical fields.
- Filter by entity type, taxonomy and manufacturer.
- Sort chronologically or alphabetically.
- Open a dossier with identity, lifecycle, physical, hardware, software, relations, missing sections and claim-level source links.
- Show verification status without treating UNVERIFIED data as accepted fact.
- PWA manifest and service worker for offline shell caching.

## Build and run
From repository root:

    python tools/gtc_runtime.py validate --strict
    python tools/gtc_runtime.py build-index
    python -m http.server 8000 --directory site

Open http://localhost:8000. A local HTTP server is required because browsers restrict fetch from file://.

The catalogue is generated from canonical JSON records into site/catalog.json. Do not edit that generated file. No third-party JavaScript runtime is required. Font hosting is optional and has a system-font fallback.
