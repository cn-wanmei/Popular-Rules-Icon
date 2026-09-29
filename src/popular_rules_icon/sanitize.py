from __future__ import annotations

import re
from xml.etree import ElementTree as ET

# Lightweight SVG safety without external deps (L1 friendly).
_FORBIDDEN_TAGS = {
    "script",
    "foreignobject",
    "iframe",
    "object",
    "embed",
    "handler",
}
_EVENT_ATTR = re.compile(r"^on", re.I)


class SanitizeError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def sanitize_svg(data: bytes) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SanitizeError("SVG_UNSAFE", f"not utf-8 svg: {exc}") from exc
    lower = text.lower()
    if "<script" in lower or "javascript:" in lower:
        raise SanitizeError("SVG_UNSAFE", "script or javascript URI")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise SanitizeError("SVG_UNSAFE", f"parse error: {exc}") from exc

    def strip(elem: ET.Element) -> None:
        tag = elem.tag.split("}")[-1].lower() if isinstance(elem.tag, str) else ""
        if tag in _FORBIDDEN_TAGS:
            raise SanitizeError("SVG_UNSAFE", f"forbidden tag: {tag}")
        for attr in list(elem.attrib):
            if _EVENT_ATTR.match(attr) or attr.lower() in {"href", "xlink:href"}:
                val = elem.attrib.get(attr, "")
                if tag != "use" and ("http://" in val or "https://" in val or val.startswith("//")):
                    raise SanitizeError("SVG_UNSAFE", f"external ref in {attr}")
                if _EVENT_ATTR.match(attr):
                    raise SanitizeError("SVG_UNSAFE", f"event attr {attr}")
        for child in list(elem):
            strip(child)

    strip(root)
    return ET.tostring(root, encoding="utf-8")
