from __future__ import annotations

import re
from dataclasses import dataclass, field

# STEP(ISO-10303-21)은 내부적으로 텍스트 기반 entity 구조라 OpenCascade 없이도
# HEADER 섹션과 PRODUCT entity를 정규식으로 추출할 수 있다.
_FILE_DESCRIPTION_RE = re.compile(r"FILE_DESCRIPTION\s*\(\s*\((.*?)\)\s*,\s*'([^']*)'\s*\)", re.DOTALL)
_FILE_NAME_RE = re.compile(
    r"FILE_NAME\s*\(\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*\((.*?)\)\s*,\s*\((.*?)\)", re.DOTALL
)
_FILE_SCHEMA_RE = re.compile(r"FILE_SCHEMA\s*\(\s*\((.*?)\)\s*\)", re.DOTALL)
_PRODUCT_RE = re.compile(r"#\d+\s*=\s*PRODUCT\s*\(\s*'([^']*)'\s*,\s*'([^']*)'")
_QUOTED_RE = re.compile(r"'([^']*)'")


@dataclass
class STEPHeader:
    description: str | None = None
    schema_version: str | None = None
    file_name: str | None = None
    timestamp: str | None = None
    author: list[str] = field(default_factory=list)
    organization: list[str] = field(default_factory=list)
    schema: list[str] = field(default_factory=list)


@dataclass
class STEPData:
    header: STEPHeader
    product_names: list[str] = field(default_factory=list)


def _parse_step(text: str) -> STEPData:
    header = STEPHeader()

    desc_match = _FILE_DESCRIPTION_RE.search(text)
    if desc_match:
        quoted = _QUOTED_RE.findall(desc_match.group(1))
        header.description = "; ".join(q for q in quoted if q) or None
        header.schema_version = desc_match.group(2) or None

    name_match = _FILE_NAME_RE.search(text)
    if name_match:
        header.file_name = name_match.group(1) or None
        header.timestamp = name_match.group(2) or None
        header.author = [a for a in _QUOTED_RE.findall(name_match.group(3)) if a]
        header.organization = [o for o in _QUOTED_RE.findall(name_match.group(4)) if o]

    schema_match = _FILE_SCHEMA_RE.search(text)
    if schema_match:
        header.schema = [s for s in _QUOTED_RE.findall(schema_match.group(1)) if s]

    product_names: list[str] = []
    seen: set[str] = set()
    for name, _label in _PRODUCT_RE.findall(text):
        if name and name not in seen:
            seen.add(name)
            product_names.append(name)

    return STEPData(header=header, product_names=product_names)
