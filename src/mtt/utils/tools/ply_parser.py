from __future__ import annotations

import struct
from dataclasses import dataclass, field

_TYPE_MAP = {
    "char": ("b", 1), "int8": ("b", 1),
    "uchar": ("B", 1), "uint8": ("B", 1),
    "short": ("h", 2), "int16": ("h", 2),
    "ushort": ("H", 2), "uint16": ("H", 2),
    "int": ("i", 4), "int32": ("i", 4),
    "uint": ("I", 4), "uint32": ("I", 4),
    "float": ("f", 4), "float32": ("f", 4),
    "double": ("d", 8), "float64": ("d", 8),
}


@dataclass
class _PLYElement:
    name: str
    count: int
    # 일반 property: (type, name, None, None) / list property: ("list", name, count_type, item_type)
    properties: list[tuple[str, str, str | None, str | None]] = field(default_factory=list)


@dataclass
class PLYData:
    is_binary: bool
    vertex_count: int
    face_count: int
    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    faces: list[list[int]] = field(default_factory=list)


def _parse_ply_header(raw: bytes) -> tuple[list[_PLYElement], str, bytes]:
    header_end = raw.index(b"end_header\n") + len(b"end_header\n")
    header_text = raw[:header_end].decode("ascii", errors="replace")
    body = raw[header_end:]

    fmt = "ascii"
    elements: list[_PLYElement] = []
    current: _PLYElement | None = None

    for line in header_text.splitlines():
        tokens = line.strip().split()
        if not tokens:
            continue
        if tokens[0] == "format":
            fmt = tokens[1]
        elif tokens[0] == "element":
            if current is not None:
                elements.append(current)
            current = _PLYElement(name=tokens[1], count=int(tokens[2]))
        elif tokens[0] == "property" and current is not None:
            if tokens[1] == "list":
                current.properties.append(("list", tokens[4], tokens[2], tokens[3]))
            else:
                current.properties.append((tokens[1], tokens[2], None, None))

    if current is not None:
        elements.append(current)

    return elements, fmt, body


def _parse_ply(raw: bytes) -> PLYData:
    elements, fmt, body = _parse_ply_header(raw)
    is_binary = fmt != "ascii"
    endian = ">" if fmt == "binary_big_endian" else "<"

    vertices: list[tuple[float, float, float]] = []
    faces: list[list[int]] = []
    vertex_count = 0
    face_count = 0

    if is_binary:
        offset = 0
        for element in elements:
            if element.name == "vertex":
                vertex_count = element.count
                names = [p[1] for p in element.properties]
                x_i, y_i, z_i = names.index("x"), names.index("y"), names.index("z")
                for _ in range(element.count):
                    values = []
                    for prop_type, _name, _lc, _li in element.properties:
                        fmt_char, size = _TYPE_MAP[prop_type]
                        (val,) = struct.unpack_from(endian + fmt_char, body, offset)
                        values.append(val)
                        offset += size
                    vertices.append((values[x_i], values[y_i], values[z_i]))
            elif element.name == "face":
                face_count = element.count
                _kind, _name, count_type, item_type = element.properties[0]
                count_char, count_size = _TYPE_MAP[count_type]
                item_char, item_size = _TYPE_MAP[item_type]
                for _ in range(element.count):
                    (n,) = struct.unpack_from(endian + count_char, body, offset)
                    offset += count_size
                    indices = list(struct.unpack_from(endian + item_char * n, body, offset))
                    offset += item_size * n
                    faces.append(indices)
            else:
                break  # 지원하지 않는 추가 element는 건너뜀
    else:
        lines = iter(body.decode("ascii", errors="replace").splitlines())
        for element in elements:
            if element.name == "vertex":
                vertex_count = element.count
                names = [p[1] for p in element.properties]
                x_i, y_i, z_i = names.index("x"), names.index("y"), names.index("z")
                for _ in range(element.count):
                    tokens = next(lines).split()
                    vertices.append((float(tokens[x_i]), float(tokens[y_i]), float(tokens[z_i])))
            elif element.name == "face":
                face_count = element.count
                for _ in range(element.count):
                    tokens = next(lines).split()
                    n = int(tokens[0])
                    faces.append([int(t) for t in tokens[1:1 + n]])

    return PLYData(
        is_binary=is_binary,
        vertex_count=vertex_count,
        face_count=face_count,
        vertices=vertices,
        faces=faces,
    )
