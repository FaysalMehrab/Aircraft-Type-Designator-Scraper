# ICAO Aircraft Type Designator Scraper

Scrapes aircraft data from [ICAO Doc 8643](https://www.icao.int/operational-safety/doc-8643-aircraft-type-designators/search) and outputs it as an RDF-style knowledge graph in JSON format.

## Output Format

Each **Type Designator** is a key. Duplicate designators across manufacturers are merged into a single key.

```json
"J328": "(J328, isManufacturedBy, 328 SUPPORT SERVICES)\n(J328, hasModel, Dornier 328JET)\n(J328, isTypeOf, LandPlane)\n(J328, hasEngineType, Jet)\n(J328, hasEngineCount, 2)\n(J328, hasWTC, M)\n(J328, isManufacturedBy, AVCRAFT)..."
```

## Requirements

```bash
pip install playwright
playwright install
```

Google Chrome must be installed on your system.

## Usage

**Step 1 — Launch Chrome with remote debugging:**
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug-profile \
  --no-first-run \
  --no-default-browser-check
```

**Step 2 — Navigate to the ICAO page in that Chrome window and complete human verification.**

**Step 3 — Run the scraper:**
```bash
python3 main.py
```

The script detects the table automatically once verification is passed and begins scraping.

## Configuration

In `main.py`:

| Variable | Default | Description |
|---|---|---|
| `TOTAL_PAGES` | `5` | Number of pages to scrape. Set to `725` for full dataset |
| `OUTPUT_FILE` | `Aircraft_Type_Designators.json` | Output file name |

## Why Remote Debugging?

The ICAO website uses bot detection that blocks automated browsers. Attaching to a real Chrome session via CDP bypasses this since the browser is indistinguishable from normal human usage.
