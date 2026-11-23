# Dataset discovery automation

The weekly `GTC TechAPI Inventory` workflow runs a metadata-only Git tree discovery over the upstream TechAPI dataset. It creates a candidate path manifest; it does not download all device data, import facts, or write to the GTC repository.

Run it manually from GitHub Actions or locally:

```bash
python tools/discoveries/discover_techapi.py --categories smartphone,tablet,laptop,soc --output research/inventories/techapi-manifest.json
```

Then import a reviewed batch using the bounded importer:

```bash
python tools/importers/import_techapi.py --manifest research/inventories/techapi-manifest.json --limit 25 --confirm-license --register-manufacturer --dry-run
```

Review every dry-run target and source/license context before removing `--dry-run`. Imported claims remain UNVERIFIED. The importer permits only HTTPS raw files under `GetTechAPI/TechAPI/develop/data/` and caps each record at 2 MiB.

GitHub Actions stores the path inventory as an artifact; scheduled discovery does not commit changes to canonical GTC data.
