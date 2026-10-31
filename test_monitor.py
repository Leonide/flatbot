import unittest

from monitor import parse_page


def listing_html(listing_id: str, listing_type: str) -> str:
    return f"""
    <div class="listing-card">
      <a href="/grodno-region/sale-flats/object/{listing_id}/">Open listing</a>
      <div class="text-caption text-basic flex justify-between">
        <div><span>ID {listing_id}</span></div>
        <div>{listing_type}</div>
      </div>
    </div>
    """


class ParsePageTests(unittest.TestCase):
    def test_selects_contact_person_and_tracks_all_page_ids(self):
        html = listing_html("123", "Контактное лицо") + listing_html("456", "Агентство")

        contacts, page_ids = parse_page(html)

        self.assertEqual(contacts, {"123": "https://realt.by/grodno-region/sale-flats/object/123/"})
        self.assertEqual(page_ids, {"123", "456"})

    def test_fails_when_page_contains_no_listing_links(self):
        with self.assertRaises(ValueError):
            parse_page("<html><body>Page changed</body></html>")


if __name__ == "__main__":
    unittest.main()