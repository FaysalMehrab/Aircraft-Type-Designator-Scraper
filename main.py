import asyncio
import json
from playwright.async_api import async_playwright

TOTAL_PAGES = 5
OUTPUT_FILE = "Aircraft_Type_Designators.json"
DEBUGGING_PORT = "http://localhost:9222"
FRAME_URL = "https://www.icao.int/sites/default/files/publications/Doc8643/SiteAssets/designators.html"


def build_triples(designator, manufacturer, model, description, engine_type, engine_count, wtc):
    lines = [
        f"({designator}, isManufacturedBy, {manufacturer})",
        f"({designator}, hasModel, {model})",
        f"({designator}, isTypeOf, {description})",
        f"({designator}, hasEngineType, {engine_type})",
        f"({designator}, hasEngineCount, {engine_count})",
        f"({designator}, hasWTC, {wtc})",
    ]
    return "\n".join(lines)


async def get_first_row_text(frame):
    row = await frame.query_selector("#atd-table tbody tr:first-child")
    return await row.inner_text() if row else ""


async def wait_for_table_update(frame, previous_first_row, timeout=10000):
    deadline = asyncio.get_event_loop().time() + timeout / 1000
    while asyncio.get_event_loop().time() < deadline:
        current = await get_first_row_text(frame)
        if current != previous_first_row:
            return
        await asyncio.sleep(0.3)
    raise TimeoutError("Table did not update after pagination click")


async def scrape_current_page(frame):
    await frame.wait_for_selector("#atd-table tbody tr", state="visible")
    rows = await frame.query_selector_all("#atd-table tbody tr")
    records = []
    for row in rows:
        cells = await row.query_selector_all("td")
        if len(cells) < 7:
            continue
        values = [await cell.inner_text() for cell in cells]
        records.append({
            "manufacturer":    values[0].strip(),
            "model":           values[1].strip(),
            "type_designator": values[2].strip(),
            "description":     values[3].strip(),
            "engine_type":     values[4].strip(),
            "engine_count":    values[5].strip(),
            "wtc":             values[6].strip(),
        })
    return records


def merge_into_result(result, records):
    for record in records:
        designator = record["type_designator"]
        triple_string = build_triples(
            designator,
            record["manufacturer"],
            record["model"],
            record["description"],
            record["engine_type"],
            record["engine_count"],
            record["wtc"],
        )
        if designator in result:
            result[designator] += "\n" + triple_string
        else:
            result[designator] = triple_string


def get_table_frame(page):
    for frame in page.frames:
        if FRAME_URL in frame.url:
            return frame
    raise RuntimeError(f"Could not find table frame: {FRAME_URL}")


async def main():
    result = {}

    async with async_playwright() as p:
        print(f"Connecting to Chrome on {DEBUGGING_PORT} ...")
        browser = await p.chromium.connect_over_cdp(DEBUGGING_PORT)
        print("Connected.\n")

        page = browser.contexts[0].pages[0]
        frame = get_table_frame(page)
        print(f"Table frame found: {frame.url}\n")

        print("Waiting for table to be visible...")
        await frame.wait_for_selector("#atd-table tbody tr", state="visible", timeout=0)
        print("Table detected. Starting scrape...\n")

        for page_num in range(1, TOTAL_PAGES + 1):
            print(f"Scraping page {page_num} / {TOTAL_PAGES} ...")

            records = await scrape_current_page(frame)
            merge_into_result(result, records)
            print(f"  Collected {len(records)} rows")

            if page_num < TOTAL_PAGES:
                first_row_before = await get_first_row_text(frame)

                next_btn = await frame.query_selector("#atd-table_next:not(.disabled) a")
                if not next_btn:
                    print("  Next button not available. Stopping early.")
                    break

                await next_btn.click()
                await wait_for_table_update(frame, first_row_before)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"\nDone. {len(result)} unique type designators saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())