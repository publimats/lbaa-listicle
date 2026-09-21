#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.images = []
        self.shop_links = []
        self.reason_sections = 0
        self.in_reason = False
        self.in_reason_h2 = False
        self.headline_parts = []
        self.reason_headlines = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.append(values["id"])
        if tag == "section" and "reason" in values.get("class", "").split():
            self.reason_sections += 1
            self.in_reason = True
        if tag == "h2" and self.in_reason:
            self.in_reason_h2 = True
            self.headline_parts = []
        if tag == "img":
            self.images.append(values)
        if tag == "a" and "shop-link" in values.get("class", "").split():
            self.shop_links.append(values)

    def handle_endtag(self, tag):
        if tag == "h2" and self.in_reason_h2:
            self.reason_headlines.append(" ".join(self.headline_parts).strip())
            self.in_reason_h2 = False
        if tag == "section" and self.in_reason:
            self.in_reason = False

    def handle_data(self, data):
        if self.in_reason_h2:
            self.headline_parts.append(data.strip())


parser = AuditParser()
parser.feed(HTML)

assert parser.reason_sections == 5, f"Expected 5 reasons, found {parser.reason_sections}"
assert len(parser.reason_headlines) == 5, "Every reason needs one H2"
assert len(parser.ids) == len(set(parser.ids)), "Duplicate HTML id"
assert len(parser.shop_links) == 4, "Expected CTA links after reasons 3, 4, 5 and in the final offer"
assert {link.get("data-cta-position") for link in parser.shop_links} == {
    "after_reason_3",
    "after_reason_4",
    "after_reason_5",
    "final_offer",
}, "CTA cadence no longer matches the reference article"

for link in parser.shop_links:
    assert link.get("data-cta-position"), "Every shop link needs a CTA position"
    assert urlparse(link.get("href", "")).netloc == "la-bande-a-anna.com", "Unexpected shop destination"

for image in parser.images:
    src = image.get("src", "")
    alt = image.get("alt")
    assert src, "Image without src"
    assert alt is not None and alt.strip(), f"Image without useful alt: {src}"
    if not urlparse(src).scheme:
        assert (ROOT / src).is_file(), f"Missing local asset: {src}"

for required in ["styles.css", "script.js", "assets/logo.png", "assets/pack-trio.jpg"]:
    assert (ROOT / required).is_file(), f"Missing required file: {required}"

lower = HTML.lower()
assert "quick-read" not in lower and "les 5 points à retenir" not in lower, "The article must not front-load a summary"
assert "class=\"hero\"" not in lower and "site-header" not in lower, "The listicle must open as an article, not a landing-page hero"
for forbidden in ["zéro fuite", "antibactérien", "hypoallergénique", "stock limité", "compte à rebours"]:
    assert forbidden not in lower, f"Risky or unsupported claim present: {forbidden}"
assert "—" not in HTML, "Use a normal hyphen instead of an em dash"

print("PASS: static listicle audit")
print("HEADLINES ONLY:")
for headline in parser.reason_headlines:
    print(headline)
