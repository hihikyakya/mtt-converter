from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_BINARY_MAGIC = b"Kaydara FBX Binary"

# "Model: 123456 {\n ... \n}" 형태의 top-level 블록(중첩 없는 경우)을 매칭
_BLOCK_RE = re.compile(r'(Model|Material|Texture|Geometry|Deformer|AnimationStack)\s*:\s*(\d+)?\s*\{(.*?)\n\}', re.DOTALL)
_NAME_RE = re.compile(r'Name\s*:\s*"([^"]*)"')
_FILENAME_RE = re.compile(r'FileName\s*:\s*"([^"]*)"')


@dataclass
class FBXObject:
    kind: str
    obj_id: str
    name: str


@dataclass
class FBXData:
    is_binary: bool
    models: list[FBXObject] = field(default_factory=list)
    materials: list[FBXObject] = field(default_factory=list)
    textures: list[FBXObject] = field(default_factory=list)


def _is_binary_fbx(raw: bytes) -> bool:
    return raw[: len(_BINARY_MAGIC)] == _BINARY_MAGIC


def _parse_ascii_fbx(text: str) -> FBXData:
    data = FBXData(is_binary=False)

    for kind, obj_id, body in _BLOCK_RE.findall(text):
        name_match = _NAME_RE.search(body)
        filename_match = _FILENAME_RE.search(body)
        name = name_match.group(1) if name_match else (filename_match.group(1) if filename_match else "")
        obj = FBXObject(kind=kind, obj_id=obj_id or "", name=name)

        if kind == "Model":
            data.models.append(obj)
        elif kind == "Material":
            data.materials.append(obj)
        elif kind == "Texture":
            data.textures.append(obj)

    return data


def _parse_binary_fbx(input_path: str | Path) -> FBXData:
    '''바이너리 FBX는 regex로 다루기 어려워 pyassimp(Assimp)로 로드한다. 미설치 시 ImportError.'''
    import pyassimp

    data = FBXData(is_binary=True)
    scene = pyassimp.load(str(input_path))
    try:
        for mesh in scene.meshes:
            data.models.append(FBXObject(kind="Model", obj_id="", name=mesh.name or ""))
        for material in scene.materials:
            props = getattr(material, "properties", {}) or {}
            name = props.get("name") if isinstance(props, dict) else None
            data.materials.append(FBXObject(kind="Material", obj_id="", name=name or ""))
    finally:
        pyassimp.release(scene)

    return data
