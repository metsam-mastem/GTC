# Contributing to GTC

## Add a device model
1. Identify exact marketed model and manufacturer model code.
2. Decide whether regional, carrier, storage, radio or board differences require separate variant records.
3. Assign a stable GTC ID; never recycle an established ID.
4. Create one JSON file under the correct data category.
5. Add a claim and source for each factual field being published.
6. Add missing source metadata to data/registry/sources.json.
7. Set verification status conservatively. An upstream verified flag is not GTC verification.
8. Run the validator and unit tests.
9. Submit a pull request with source links and a concise change explanation.

## Add a component
Create a separate component record for a reusable SoC, CPU, GPU, modem, memory device, display controller, PMIC, board assembly or replaceable part. Link products to the component with typed relationships.

## Claim rules
- One claim describes one field or tightly scoped observation.
- Keep units explicit and normalized.
- Record source locator and retrieval date.
- Use CONFLICTED when credible sources disagree; preserve both claims.
- Use UNVERIFIED for imported or community-sourced information awaiting review.
- Use VERIFIED only after GTC review against evidence appropriate to the claim.
- Never invent a value to fill a blank.

## Media rules
Store a link and metadata when redistribution rights are unknown. Do not commit third-party product photography, manuals, schematics or firmware without an applicable permission or license.

## Privacy and security
Do not commit personal device dumps, IMEIs, IMSIs, phone numbers, owner information, credentials, signing keys, private logs or data tied to an identifiable person.

## Required checks
    python tools/gtc_runtime.py validate --strict
    python -m unittest discover -s tests -v

CI is the deterministic gate. A successful local run does not replace source review.
