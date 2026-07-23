from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field

_GLB_MAGIC = b"glTF"
_CHUNK_TYPE_JSON = 0x4E4F534A
_CHUNK_TYPE_BIN = 0x004E4942


@dataclass
class GLTFData:
    is_binary: bool
    version: str | None = None
    generator: str | None = None
    scene_count: int = 0
    node_count: int = 0
    animation_count: int = 0
    mesh_names: list[str] = field(default_factory=list)
    material_names: list[str] = field(default_factory=list)
    texture_uris: list[str] = field(default_factory=list)
    bin_chunk_length: int | None = None


def _is_glb(raw: bytes) -> bool:
    return raw[: len(_GLB_MAGIC)] == _GLB_MAGIC


def _extract_gltf_document(doc: dict, is_binary: bool, bin_chunk_length: int | None = None) -> GLTFData:
    asset = doc.get("asset", {}) or {}
    meshes = doc.get("meshes", []) or []
    materials = doc.get("materials", []) or []
    images = doc.get("images", []) or []

    return GLTFData(
        is_binary=is_binary,
        version=asset.get("version"),
        generator=asset.get("generator"),
        scene_count=len(doc.get("scenes", []) or []),
        node_count=len(doc.get("nodes", []) or []),
        animation_count=len(doc.get("animations", []) or []),
        mesh_names=[mesh.get("name", f"mesh_{i}") for i, mesh in enumerate(meshes)],
        material_names=[mat.get("name", f"material_{i}") for i, mat in enumerate(materials)],
        texture_uris=[image.get("uri", f"(embedded image {i})") for i, image in enumerate(images)],
        bin_chunk_length=bin_chunk_length,
    )


def _parse_gltf(text: str) -> GLTFData:
    '''ASCII glTF(.gltf)는 그 자체가 JSON이라 표준 json 모듈로 바로 읽을 수 있다.'''
    doc = json.loads(text)
    return _extract_gltf_document(doc, is_binary=False)


def _parse_glb(raw: bytes) -> GLTFData:
    '''GLB(.glb)는 12바이트 헤더 뒤에 JSON 청크(+ 선택적 BIN 청크)가 오는 바이너리 컨테이너.'''
    offset = 12  # magic(4) + version(4) + length(4)

    json_doc: dict = {}
    bin_chunk_length: int | None = None

    while offset < len(raw):
        chunk_length, chunk_type = struct.unpack_from("<II", raw, offset)
        offset += 8
        chunk_data = raw[offset: offset + chunk_length]
        offset += chunk_length

        if chunk_type == _CHUNK_TYPE_JSON:
            json_doc = json.loads(chunk_data.decode("utf-8"))
        elif chunk_type == _CHUNK_TYPE_BIN:
            bin_chunk_length = len(chunk_data)

    return _extract_gltf_document(json_doc, is_binary=True, bin_chunk_length=bin_chunk_length)
