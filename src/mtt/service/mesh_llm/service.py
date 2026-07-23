import os
from pathlib import Path

from mtt.types import LangType
from mtt.utils.mesh_llm_utils import (
    parsing_stl,
    parsing_obj,
    parsing_ply,
    parsing_3mf,
    parsing_fbx,
    parsing_step,
    parsing_usd,
    parsing_gltf,
)


class MeshLLMService:
    '''PointNet(허깅페이스, 8bit 양자화) 기반 3D 모델 -> context vector -> projection(나중에 직접 만들거임) ->임베딩 벡터

    TODO: PointNet기반 모델 로딩/추론 구현 또는 임베딩 벡터 기반 검색으로 구현할 예정.
    '''

    def __init__(self, **kwargs):
        pass

    def to_text(self, input_path: str | Path, markdown=True, lang: LangType = "eng") -> str:
        _, ext = os.path.splitext(input_path)
        ext = ext.lower()
        if ext == ".stl":
            return parsing_stl(input_path, markdown=markdown, lang=lang)
        elif ext == ".obj":
            return parsing_obj(input_path, markdown=markdown, lang=lang)
        elif ext == ".ply":
            return parsing_ply(input_path, markdown=markdown, lang=lang)
        elif ext == ".3mf":
            return parsing_3mf(input_path, markdown=markdown, lang=lang)
        elif ext == ".fbx":
            return parsing_fbx(input_path, markdown=markdown, lang=lang)
        elif ext in (".step", ".stp"):
            return parsing_step(input_path, markdown=markdown, lang=lang)
        elif ext in (".usd", ".usda", ".usdz"):
            return parsing_usd(input_path, markdown=markdown, lang=lang)
        elif ext in (".glb", ".gltf"):
            return parsing_gltf(input_path, markdown=markdown, lang=lang)
        raise ValueError(f"Unreadable file or incorrect extension. input_path: {input_path}")
