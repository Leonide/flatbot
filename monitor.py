import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


PAGE_URL = "https://realt.by/grodno-region/sale/flats/?sortType=createdAt&page=1"
STATE_PATH = Path(__file__).with_name("seen_ids.json")
OBJECT_PATH = re.compile(r"/sale-flats/object/(\d+)/")
METADATA_CLASSES = {"text-caption", "text-basic", "flex", "justify-between"}


def parse_page(html: str) -> tuple[dict[str, str], set[str]]:
    soup = BeautifulSoup(html, "html.parser")
    contact_listings: dict[str, str] = {}
    page_ids: set[str] = set()

    for link in soup.find_all("a", href=OBJECT_PATH):
        match = OBJECT_PATH.search(link["href"])
        if match is None:
            continue

        listing_id = match.group(1)
        page_ids.add(listing_id)
        listing_type = find_listing_type(link, listing_id)
        if listing_type == "Контактное лицо":
            contact_listings[listing_id] = urljoin(PAGE_URL, link["href"])

    if not page_ids:
        raise ValueError("No listings found; the page structure may have changed")

    return contact_listings, page_ids


def find_listing_type(link, listing_id: str) -> str | None:
    for container in link.parents:
        if container.name != "div":
            continue

        if listing_id not in container.get_text(" ", strip=True):
            continue

        for row in container.find_all(
            "div",
            class_=lambda value: value
            and METADATA_CLASSES.issubset(value.split() if isinstance(value, str) else value),
        ):
            if listing_id not in row.get_text(" ", strip=True):
                continue

            columns = row.find_all("div", recursive=False)
            if len(columns) >= 2:
                return columns[1].get_text(" ", strip=True)

    return None


def load_state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def send_telegram_message(listing_id: str, url: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")

    response = httpx.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": f"Новое объявление от контактного лица\n{url}"},
        timeout=20,
    )
    response.raise_for_status()
    if not response.json().get("ok"):
        raise RuntimeError(f"Telegram rejected listing {listing_id}")


def main() -> None:
    response = httpx.get(
        PAGE_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; Flatbot/1.0)"},
        timeout=30,
    )
    response.raise_for_status()
    contact_listings, page_ids = parse_page(response.text)
    state = load_state()

    if not state["initialized"]:
        state = {"initialized": True, "ids": sorted(page_ids)}
        STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Initial scan complete; recorded {len(page_ids)} listings without notifications")
        return

    previous_ids = set(state["ids"])
    new_contact_ids = sorted(set(contact_listings) - previous_ids)
    for listing_id in new_contact_ids:
        send_telegram_message(listing_id, contact_listings[listing_id])
        print(f"Sent listing {listing_id}")

    next_state = {"initialized": True, "ids": sorted(page_ids)}
    STATE_PATH.write_text(json.dumps(next_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scan complete; sent {len(new_contact_ids)} notification(s)")


if __name__ == "__main__":
    main()