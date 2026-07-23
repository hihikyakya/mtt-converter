import os
from pathlib import Path

from mtt.utils.mesh_llm_utils import (
    parsing_stl,
    parsing_obj,
    parsing_ply,
    parsing_3mf,
    parsing_fbx,
    parsing_step,
    parsing_usd,
)


class MeshLLMService:
    '''PointNet(허깅페이스, 8bit 양자화) 기반 3D 모델 -> context vector -> projection(나중에 직접 만들거임) ->임베딩 벡터

    TODO: PointNet기반 모델 로딩/추론 구현 또는 임베딩 벡터 기반 검색으로 구현할 예정.
    '''

    def __init__(self, **kwargs):
        pass

    def to_text(self, input_path: str | Path, markdown=True) -> str:
        _, ext = os.path.splitext(input_path)
        ext = ext.lower()
        if ext == ".stl":
            return parsing_stl(input_path, markdown=markdown)
        elif ext == ".obj":
            return parsing_obj(input_path, markdown=markdown)
        elif ext == ".ply":
            return parsing_ply(input_path, markdown=markdown)
        elif ext == ".3mf":
            return parsing_3mf(input_path, markdown=markdown)
        elif ext == ".fbx":
            return parsing_fbx(input_path, markdown=markdown)
        elif ext in (".step", ".stp"):
            return parsing_step(input_path, markdown=markdown)
        elif ext in (".usd", ".usda", ".usdz"):
            return parsing_usd(input_path, markdown=markdown)
        raise ValueError(f"Unreadable file or incorrect extension. input_path: {input_path}")
