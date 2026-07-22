from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

_3MF_CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"


@dataclass
class ThreeMFData:
    object_count: int
    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    triangles: list[tuple[int, int, int]] = field(default_factory=list)


def _parse_3mf(input_path: str | Path) -> ThreeMFData:
    with zipfile.ZipFile(input_path) as archive:
        model_path = next(
            (name for name in archive.namelist() if name.endswith("3dmodel.model")),
            None,
        )
        if model_path is None:
            raise ValueError("3MF 파일 안에서 3dmodel.model을 찾을 수 없습니다.")
        root = ET.fromstring(archive.read(model_path))

    vertices: list[tuple[float, float, float]] = []
    triangles: list[tuple[int, int, int]] = []
    object_count = 0

    for obj in root.iter(f"{{{_3MF_CORE_NS}}}object"):
        object_count += 1
        mesh = obj.find(f"{{{_3MF_CORE_NS}}}mesh")
        if mesh is None:
            continue

        base_index = len(vertices)
        vertices_el = mesh.find(f"{{{_3MF_CORE_NS}}}vertices")
        if vertices_el is not None:
            for vertex in vertices_el:
                vertices.append((float(vertex.get("x")), float(vertex.get("y")), float(vertex.get("z"))))

        triangles_el = mesh.find(f"{{{_3MF_CORE_NS}}}triangles")
        if triangles_el is not None:
            for triangle in triangles_el:
                v1 = base_index + int(triangle.get("v1"))
                v2 = base_index + int(triangle.get("v2"))
                v3 = base_index + int(triangle.get("v3"))
                triangles.append((v1, v2, v3))

    return ThreeMFData(object_count=object_count, vertices=vertices, triangles=triangles)
