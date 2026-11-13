from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [
    "index.html", "contattami.html", "prenota-una-lezione.html",
    "materiale-didattico.html", "404.html",
]
REDIRECTS = {
    "contattami.html": "#contatti",
    "prenota-una-lezione.html": "#contatti",
    "materiale-didattico.html": "#materiali",
}
PHONE = "+393770982047"
WHATSAPP = "https://wa.me/393770982047"
OBSOLETE = (
    "3454860367", "393454860367", "maurizio.falconi47@gmail.com",
    "calendly.com", "cusano milanino", "15€/h", "15 €/h",
    "webnode", "cloudfront.net",
)


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.tags: dict[str, int] = {}
        self.has_viewport = False
        self.has_main = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        self.tags[tag] = self.tags.get(tag, 0) + 1
        if attr.get("id"):
            self.ids.add(attr["id"] or "")
        if tag == "a" and attr.get("href"):
            self.hrefs.append(attr["href"] or "")
        if tag == "meta" and (attr.get("name") or "").lower() == "viewport":
            self.has_viewport = True
        if tag == "main":
            self.has_main = True


def main() -> int:
    errors: list[str] = []
    for name in HTML_FILES:
        if not (ROOT / name).is_file():
            errors.append(f"Missing: {name}")
    if errors:
        print("\n".join("ERROR: " + e for e in errors))
        return 1

    pages: dict[str, tuple[str, Page]] = {}
    for name in HTML_FILES:
        content = (ROOT / name).read_text(encoding="utf-8")
        parsed = Page()
        parsed.feed(content)
        pages[name] = (content, parsed)
        if not parsed.has_viewport:
            errors.append(f"{name}: missing viewport")
        if not parsed.has_main:
            errors.append(f"{name}: missing main landmark")

    html, page = pages["index.html"]
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    low = (html + css + "\n" + "\n".join(t for t, _ in pages.values())).lower()
    for term in OBSOLETE:
        if term.lower() in low:
            errors.append(f"Forbidden public marker: {term}")
    if re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", low) or "mailto:" in low:
        errors.append("Public email exposure")

    for fact in (
        "Matematica e fisica", "scuole medie e superiori",
        "Comune di Parma", "377 098 2047",
        "20 € / h", "25 € / h", "Appunti digitali", "Dispense",
    ):
        if fact.lower() not in html.lower():
            errors.append(f"Missing useful information: {fact}")
    if html.count("20 € / h") != 1 or html.count("25 € / h") != 1:
        errors.append("Hourly prices should each appear once")

    for fragment in ("lezioni", "parma", "materiali", "contatti"):
        if fragment not in page.ids:
            errors.append(f"Missing legacy anchor #{fragment}")
    if page.tags.get("h1", 0) != 1:
        errors.append("Exactly one h1 is required")
    if "lesson-preview" in html or "lesson-grid" in html or "subject-card" in html:
        errors.append("Long old lesson/card grid should be removed")
    if "hero-art" not in html or "resonance-figure" not in html:
        errors.append("Signature harmonic-physics figure is missing")
    if "resonance-title" not in html or "role=\"img\"" not in html:
        errors.append("Art needs an accessible description")
    if page.tags.get("details", 0) != 1 or page.tags.get("summary", 0) != 1:
        errors.append("There must be exactly one compact secondary-details disclosure")
    if "google.com/maps/embed" not in html or 'title="Mappa di Parma"' not in html:
        errors.append("Embedded map must remain available on request")
    for external in (
        "https://www.desmos.com/calculator?lang=it",
        "https://photomath.com/it", "https://www.wolframalpha.com/",
    ):
        if external not in html:
            errors.append(f"Optional teaching resource missing: {external}")
    if "assets/maurizio-headshot.webp" not in html or not (ROOT / "assets/maurizio-headshot.webp").is_file():
        errors.append("Tutor portrait missing")
    if 'href="styles.css?v=' not in html:
        errors.append("Versioned stylesheet missing")
    if "height: 100vh" in css or "overflow: hidden" in css.split(".hero")[0]:
        errors.append("Responsive page must never trap scroll")
    if "#388e3c" not in css:
        errors.append("Identity green should remain")
    if "@media (max-width:" not in css or "prefers-reduced-motion" not in css:
        errors.append("Missing responsive/reduced-motion rules")

    tel = [x for x in page.hrefs if x.startswith("tel:")]
    if not tel or any(x != "tel:" + PHONE for x in tel):
        errors.append("Invalid telephone contact")
    if WHATSAPP not in page.hrefs:
        errors.append("WhatsApp CTA missing")
    for href in page.hrefs:
        if href.startswith("#"):
            if href[1:] not in page.ids:
                errors.append(f"Unresolved fragment: {href}")
            continue
        parsed = urlparse(href)
        if parsed.scheme in ("https", "http"):
            continue
        if parsed.scheme == "tel" and href == "tel:" + PHONE:
            continue
        if parsed.scheme:
            errors.append(f"Unexpected link scheme: {href}")
            continue
        if parsed.path in ("", "./"):
            continue
        if not (ROOT / parsed.path).is_file():
            errors.append(f"Broken local link: {href}")

    for name, fragment in REDIRECTS.items():
        text, parsed = pages[name]
        if fragment not in text or "./" + fragment not in parsed.hrefs:
            errors.append(f"Broken old-page redirect: {name}")

    if errors:
        print("\n".join("ERROR: " + e for e in errors))
        return 1
    print("Site quality checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
