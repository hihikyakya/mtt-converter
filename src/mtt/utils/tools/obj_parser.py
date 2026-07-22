from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OBJData:
    name: str
    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    faces: list[list[int]] = field(default_factory=list)  # 0-indexed vertex indices per face


def _parse_obj(text: str) -> OBJData:
    name = "(obj)"
    vertices: list[tuple[float, float, float]] = []
    faces: list[list[int]] = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        tokens = line.split()
        keyword = tokens[0]

        if keyword in ("o", "g") and len(tokens) >= 2 and name == "(obj)":
            name = " ".join(tokens[1:])
        elif keyword == "v" and len(tokens) >= 4:
            vertices.append((float(tokens[1]), float(tokens[2]), float(tokens[3])))
        elif keyword == "f" and len(tokens) >= 4:
            # "v", "v/vt", "v/vt/vn", "v//vn" 모두 지원. 음수 인덱스는 끝에서부터의 상대 참조.
            indices = []
            for token in tokens[1:]:
                v_index = int(token.split("/")[0])
                indices.append(v_index - 1 if v_index > 0 else len(vertices) + v_index)
            faces.append(indices)

    return OBJData(name=name, vertices=vertices, faces=faces)
