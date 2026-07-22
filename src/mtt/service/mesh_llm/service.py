import os
from pathlib import Path

from mtt.utils.mesh_llm_utils import parsing_stl, parsing_obj, parsing_ply, parsing_3mf


class MeshLLMService:
    '''PointNet(허깅페이스, 8bit 양자화) 기반 3D 모델 -> context vector -> projection(나중에 직접 만들거임) ->임베딩 벡터

    TODO: PointNet기반 모델 로딩/추론 구현 또는 임베딩 벡터 기반 검색으로 구현할 예정.
    '''

    def __init__(self, **kwargs):
        pass

    def to_text(self, input_path: str | Path, markdown=True) -> str: #TODO: v1이고, v2에서는 pointNet기반으로 context vector를 embedding vector로 projection해서 줄듯.
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
        # TODO: .step/.stp, .usd/.usdz, .fbx는 PointNet으로 임베딩해서 기존 stl 등으로 구축해둔 DB에서
        # 검색 후 리매핑하는 방식으로 구현 예정 (직접 파싱 대신 유사 형상 검색).
        raise ValueError(f"Unreadable file or incorrect extension. input_path: {input_path}")
