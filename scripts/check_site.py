from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [
    ROOT / "index.html",
    ROOT / "contattami.html",
    ROOT / "prenota-una-lezione.html",
    ROOT / "materiale-didattico.html",
    ROOT / "404.html",
]
REDIRECTS = {
    "contattami.html": "#contatti",
    "prenota-una-lezione.html": "#contatti",
    "materiale-didattico.html": "#materiali",
}

APPROVED_TEL = "+393770982047"
APPROVED_WHATSAPP = "https://wa.me/393770982047"
FORBIDDEN_PUBLIC_MARKERS = [
    "3454860367",
    "393454860367",
    "maurizio.falconi47@gmail.com",
    "calendly.com",
    "cusano milanino",
    "15€/h",
    "15 €/h",
]


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.has_viewport = False
        self.has_main = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("id"):
            self.ids.add(data["id"] or "")
        if tag == "a" and data.get("href"):
            self.hrefs.append(data["href"] or "")
        if tag == "meta" and data.get("name", "").lower() == "viewport":
            self.has_viewport = True
        if tag == "main":
            self.has_main = True


def add_error(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []

    for path in HTML_FILES:
        if not path.exists():
            add_error(f"Missing required file: {path.relative_to(ROOT)}", errors)

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1

    docs: dict[Path, tuple[str, SiteParser]] = {}
    for path in HTML_FILES:
        text = path.read_text(encoding="utf-8")
        parser = SiteParser()
        parser.feed(text)
        docs[path] = (text, parser)

        if not parser.has_viewport:
            add_error(f"{path.name}: missing viewport meta", errors)
        if not parser.has_main:
            add_error(f"{path.name}: missing main landmark", errors)

    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    public_text = "\n".join(text for text, _ in docs.values()) + "\n" + css
    lowered = public_text.lower()

    legacy_markers = ["web" + "node", "cloudfront" + ".net"]
    for marker in legacy_markers:
        if marker in lowered:
            add_error(f"Legacy marker still present in public site: {marker}", errors)

    if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", public_text):
        add_error("An email address is exposed in the public site", errors)
    if "mailto:" in lowered:
        add_error("A mailto link is exposed in the public site", errors)

    for marker in FORBIDDEN_PUBLIC_MARKERS:
        if marker.lower() in lowered:
            add_error(f"Forbidden obsolete marker still exposed: {marker}", errors)

    index_text, index_parser = docs[ROOT / "index.html"]
    if '<html lang="it">' not in index_text.lower():
        add_error("index.html: lang=it missing", errors)

    required_copy = [
        "Matematica e fisica",
        "scuole medie e superiori",
        "Comune di Parma",
        "377 098 2047",
    ]
    for item in required_copy:
        if item not in index_text:
            add_error(f"index.html: missing confirmed public fact: {item}", errors)

    if "20 € / h" not in index_text:
        add_error("index.html: online price 20 €/h missing", errors)
    if "25 € / h" not in index_text:
        add_error("index.html: in-person price 25 €/h missing", errors)
    if "google.com/maps/embed" not in index_text or 'title="Mappa di Parma"' not in index_text:
        add_error("index.html: Parma Google Maps embed missing", errors)
    required_layout_markers = [
        "lesson-preview",
        "compact-strip",
        "utility-grid",
        "resource-benefits",
        "tools-row",
    ]
    for marker in required_layout_markers:
        if marker not in index_text:
            add_error(f"index.html: compact layout marker missing: {marker}", errors)

    obsolete_layout_markers = [
        'class="hero-board"',
        'class="materials-grid"',
        'class="hero-shell"',
    ]
    for marker in obsolete_layout_markers:
        if marker in index_text:
            add_error(f"index.html: oversized previous layout still present: {marker}", errors)
    if 'id="metodo"' in index_text or 'href="#metodo"' in index_text:
        add_error("index.html: redundant standalone method section/navigation still present", errors)
    if "assets/maurizio-headshot.webp" not in index_text:
        add_error("index.html: tutor headshot is missing from the hero card", errors)
    if not (ROOT / "assets" / "maurizio-headshot.webp").exists():
        add_error("assets/maurizio-headshot.webp: file missing", errors)
    if "gli appunti della lezione restano disponibili in formato digitale" not in index_text:
        add_error("index.html: digital lesson-notes benefit missing", errors)
    if "ti fornisco dispense utili" not in index_text:
        add_error("index.html: handouts benefit missing", errors)
    if "https://photomath.com/it" not in index_text:
        add_error("index.html: Photomath resource link missing", errors)

    if "verificare la disponibilità nella tua area" not in index_text:
        add_error("index.html: updated Parma availability copy missing", errors)
    if "ho tutti i supporti necessari (e ti costa meno!)" not in index_text:
        add_error("index.html: updated online-support copy missing", errors)
    if "#388e3c" not in css.lower():
        add_error("styles.css: original primary green #388e3c missing", errors)

    h1_match = re.search(
        r"h1\s*\{[^}]*font-size:\s*clamp\([^,]+,[^,]+,\s*([0-9.]+)rem\)",
        css,
        re.DOTALL,
    )
    if not h1_match:
        add_error("styles.css: h1 clamp sizing missing", errors)
    elif float(h1_match.group(1)) > 4.0:
        add_error("styles.css: desktop hero title is too large", errors)

    compact_section_rules = [".compact-section", ".utility-section"]
    for selector in compact_section_rules:
        match = re.search(
            re.escape(selector) + r"\s*\{[^}]*padding:\s*([0-9.]+)rem\s+0",
            css,
            re.DOTALL,
        )
        if not match:
            add_error(f"styles.css: compact spacing rule missing for {selector}", errors)
        elif float(match.group(1)) > 4.0:
            add_error(f"styles.css: {selector} is too vertically spacious", errors)

    tel_links = [href for href in index_parser.hrefs if href.startswith("tel:")]
    if not tel_links:
        add_error("index.html: approved telephone link missing", errors)
    elif any(href != f"tel:{APPROVED_TEL}" for href in tel_links):
        add_error(f"index.html: found a telephone link other than tel:{APPROVED_TEL}", errors)
    if APPROVED_WHATSAPP not in index_parser.hrefs:
        add_error("index.html: approved WhatsApp link missing", errors)

    for href in index_parser.hrefs:
        if href.startswith("#"):
            if href[1:] not in index_parser.ids:
                add_error(f"index.html: missing anchor target {href}", errors)
            continue

        parsed = urlparse(href)
        if parsed.scheme in {"http", "https"}:
            continue
        if parsed.scheme == "tel" and href == f"tel:{APPROVED_TEL}":
            continue
        if parsed.scheme:
            add_error(f"index.html: unsupported link scheme in {href}", errors)
            continue

        target_path = parsed.path
        if target_path in {"", "./"}:
            continue
        target = (ROOT / target_path).resolve()
        if not target.exists():
            add_error(f"index.html: missing internal target {target_path}", errors)

    for filename, anchor in REDIRECTS.items():
        text, parser = docs[ROOT / filename]
        if anchor not in text:
            add_error(f"{filename}: expected redirect target {anchor}", errors)
        if "./" + anchor not in parser.hrefs:
            add_error(f"{filename}: missing fallback link to ./{anchor}", errors)

    if "@media (min-width:" not in css:
        add_error("styles.css: responsive breakpoint missing", errors)
    if "prefers-reduced-motion" not in css:
        add_error("styles.css: reduced-motion handling missing", errors)

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1

    print("Site quality checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
