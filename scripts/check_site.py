"""Validate the public tutoring site and the destinations of its legacy pages."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = {
    "contattami.html": "#contatti",
    "prenota-una-lezione.html": "#contatti",
    "materiale-didattico.html": "#materiali",
}
HTML_FILES = ["index.html", *REDIRECTS, "404.html"]
APPROVED_TEL = "+393770982047"
APPROVED_WHATSAPP = "https://wa.me/393770982047"
PORTFOLIO = "https://falker47.github.io/"
FORBIDDEN_PUBLIC_MARKERS = (
    "3454860367",
    "393454860367",
    "maurizio.falconi47@gmail.com",
    "calendly.com",
    "cusano milanino",
    "web" + "node",
    "cloudfront" + ".net",
    "mailto:",
)


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.hrefs: list[str] = []
        self.assets: list[str] = []
        self.refresh: str | None = None
        self.has_viewport = False
        self.has_main = False
        self.lang = ""
        self.robots = ""
        self.controls: list[str] = []
        self.slide_titles: list[str] = []
        self.body_text: list[str] = []
        self.in_body = False
        self.in_code = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        identifier = data.get("id")
        if identifier:
            if identifier in self.ids:
                self.duplicate_ids.add(identifier)
            self.ids.add(identifier)
        if tag == "html":
            self.lang = data.get("lang", "")
        elif tag == "main":
            self.has_main = True
        elif tag == "body":
            self.in_body = True
        elif tag == "meta":
            name = data.get("name", "").lower()
            if name == "viewport":
                self.has_viewport = "width=device-width" in data.get("content", "").replace(" ", "")
            elif name == "robots":
                self.robots = data.get("content", "").lower()
            if data.get("http-equiv", "").lower() == "refresh":
                self.refresh = data.get("content")
        elif tag == "a" and "href" in data:
            self.hrefs.append(data["href"])
        elif tag == "link" and data.get("rel", "") in ("stylesheet", "icon", "preload"):
            self.assets.append(data.get("href", ""))
        elif tag == "button" and data.get("aria-label"):
            self.controls.extend(key for key in data if key in {"data-play", "data-next", "data-previous"})

        if tag in {"script", "style"}:
            self.in_code = True
        if tag in {"script", "img", "source"} and "src" in data:
            self.assets.append(data["src"])
        if "example-slide" in data.get("class", "").split():
            self.slide_titles.append(data.get("data-title", ""))

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.in_code = False
        if tag == "body":
            self.in_body = False

    def handle_data(self, data: str) -> None:
        if self.in_body and not self.in_code:
            self.body_text.append(data)


def main() -> int:
    errors: list[str] = []
    docs: dict[Path, SiteParser] = {}
    public_sources: dict[Path, str] = {}
    for filename in HTML_FILES:
        path = ROOT / filename
        if not path.is_file():
            errors.append(f"Missing required page: {filename}")
            continue
        public_sources[path] = path.read_text(encoding="utf-8")
        parser = SiteParser()
        parser.feed(public_sources[path])
        parser.close()
        docs[path] = parser
        if not parser.has_viewport or not parser.has_main:
            errors.append(f"{filename}: viewport or main landmark missing")
        if parser.duplicate_ids:
            errors.append(f"{filename}: duplicate IDs: {sorted(parser.duplicate_ids)}")

    def local_target(origin: Path, url: str) -> Path | None:
        parsed = urlparse(url)
        if parsed.scheme or parsed.netloc:
            return None
        target = (origin.parent / unquote(parsed.path)).resolve() if parsed.path else origin
        if target.is_dir():
            target = target / "index.html"
        if not target.is_relative_to(ROOT) or not target.is_file():
            errors.append(f"{origin.relative_to(ROOT)}: missing or invalid local target {url!r}")
            return None
        return target

    home_sources: dict[str, list[str]] = {".css": [], ".js": []}
    for path, doc in docs.items():
        for href in doc.hrefs:
            parsed = urlparse(href)
            if parsed.scheme in {"http", "https"}:
                if parsed.hostname == "wa.me" and href != APPROVED_WHATSAPP:
                    errors.append(f"{path.name}: unapproved WhatsApp number")
                continue
            if href == f"tel:{APPROVED_TEL}":
                continue
            if parsed.scheme or parsed.netloc or not href:
                errors.append(f"{path.name}: unexpected link {href!r}")
                continue
            target = local_target(path, href)
            if target in docs and parsed.fragment and unquote(parsed.fragment) not in docs[target].ids:
                errors.append(f"{path.name}: unresolved fragment {href}")
        for url in doc.assets:
            if not url:
                errors.append(f"{path.name}: empty asset URL")
                continue
            target = local_target(path, url)
            if target and target.suffix in home_sources:
                if target not in public_sources:
                    public_sources[target] = target.read_text(encoding="utf-8")
                if path.name == "index.html":
                    home_sources[target.suffix].append(public_sources[target])

    for path, text in public_sources.items():
        if path.suffix == ".css":
            for _, url in re.findall(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""", text, re.I):
                if not url.startswith("#"):
                    local_target(path, url.strip())
        lowered = text.casefold()
        for marker in FORBIDDEN_PUBLIC_MARKERS:
            if marker in lowered:
                errors.append(f"{path.name}: obsolete private or vendor marker {marker!r}")
        if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text):
            errors.append(f"{path.name}: a public email address was found")
        if re.search(r"(?<!\d)15\s*€\s*/\s*h(?!\w)", lowered):
            errors.append(f"{path.name}: obsolete tuition rate")

    home = docs.get(ROOT / "index.html")
    if home:
        copy = " ".join(" ".join(home.body_text).split()).casefold()
        if home.lang != "it" or "noindex" in home.robots or "none" in home.robots.split(","):
            errors.append("index.html: public Italian homepage expected")
        for fact in ("maurizio falconi", "matematica e fisica", "lezioni individuali", "medie",
                     "superiori", "appunti digitali", "dispens", "falker47"):
            if fact not in copy:
                errors.append(f"index.html: missing confirmed public fact {fact!r}")
        for label, price in [("in presenza a parma", 25), ("online", 20)]:
            if not re.search(rf"{label}\s+{price}\s*€\s*/\s*h\b", copy):
                errors.append(f"index.html: missing or incorrect {label} rate")
        if home.hrefs.count(APPROVED_WHATSAPP) != 1 or PORTFOLIO not in home.hrefs:
            errors.append("index.html: expected one WhatsApp CTA and the personal-site link")
        for anchor in ("contenuto", "lezioni", "parma", "materiali", "contatti"):
            if anchor not in home.ids:
                errors.append(f"index.html: missing legacy destination #{anchor}")
        if len(home.slide_titles) != 3 or not all(
            topic in title.casefold()
            for topic, title in zip(("pitagora", "secondo grado", "velocità"), home.slide_titles)
        ):
            errors.append("index.html: the three approved Quaderno examples are missing or out of order")
        if sorted(home.controls) != ["data-next", "data-play", "data-previous"]:
            errors.append("index.html: missing or duplicate labelled carousel controls")
        styles = "\n".join(home_sources[".css"])
        scripts = "\n".join(home_sources[".js"])
        if not re.search(r"@media[^{}]*(?:min|max)-width\s*:", styles, re.I):
            errors.append("index.html: responsive breakpoints missing")
        if "prefers-reduced-motion" not in styles + scripts or not scripts:
            errors.append("index.html: carousel script or reduced-motion handling missing")

    for filename, anchor in REDIRECTS.items():
        doc = docs.get(ROOT / filename)
        if doc:
            dest = "./" + anchor
            if not re.fullmatch(r"\s*0\s*;\s*url\s*=\s*" + re.escape(dest) + r"\s*", doc.refresh or "", re.I):
                errors.append(f"{filename}: automatic redirect to {dest} missing")
            if dest not in doc.hrefs:
                errors.append(f"{filename}: fallback link to {dest} missing")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("Site quality checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
