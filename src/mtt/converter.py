import os
from pathlib import Path
from typing import Literal

from mtt.service.docling import DoclingService
from mtt.service.point_llm import PointLLMService

ModeType = Literal["caption", "ocr", "3dmodel", "doc"]


class MultiModalConverter:
    MODE_ESTIMATE_MAP: dict[str, ModeType] = {
        ".jpg": "caption",
        ".jpeg": "caption",
        ".tif": "caption",
        ".tiff": "caption",
        ".png": "caption",
        ".bmp": "caption",
        ".pdf": "doc",
        ".doc": "doc",
        ".docx": "doc",
        ".ppt": "doc",
        ".pptx": "doc",
        ".xls": "doc",
        ".xlsx": "doc",
        ".html": "doc",
        ".htm": "doc",
        ".md": "doc",
        ".csv": "doc",
        ".obj": "3dmodel",
        ".ply": "3dmodel",
        ".glb": "3dmodel",
    }

    def __init__(self, **kwargs):
        # TODO: 나중에 임베딩 모델 api 관련해서 파라미터를 받을 수 있게하거나 할듯. 그리고 일부 시스템 프롬프트를 조절할 수 있게 할듯.
        self._docling_service = DoclingService()
        self._point_llm_service = PointLLMService()

    def convert(self, input_path: str | Path, mode: ModeType | None = None):
        if mode is None:
            print("[Warning] The 'mode' argument is missing, so the 'mode' value is estimated and used.")
            _, ext = os.path.splitext(input_path)

            mode = self.MODE_ESTIMATE_MAP.get(ext.lower())

        if mode == "caption":
            # input 가공 가능
            return self.caption(input_path)
        elif mode == "ocr":
            # input 가공 가능
            return self.ocr(input_path)
        elif mode == "3dmodel":
            # input 가공 가능함.
            return self.scan3dmodel(input_path)
        elif mode in ["doc", "docs", "document"]:
            # input 가공 가능함.
            return self.doc2text(input_path)
        else:
            raise ValueError(f"There is no valid function for the mode. | mode: {mode}")



    def caption(self, input_path: str | Path):
        '''
        image의 정보를 텍스트로 설명 ; 캡셔닝
        '''
        raise NotImplementedError("caption mode is not implemented yet.") #이미지 용 멀티모달 임베딩 api를 찾아서 구현할듯.

    def ocr(self, input_path: str | Path) -> str:
        '''
        image내 텍스트를 ocr하여 얻어옴.
        '''
        return self._docling_service.to_text(input_path)

    def scan3dmodel(self, input_path: str | Path) -> str:
        '''
        3D 모델을 텍스트로 설명
        '''
        return self._point_llm_service.to_text(input_path) # TODO: point llm으로 구현할 예정

    def doc2text(self, input_path: str | Path) -> str:
        '''
        문서를 텍스트로 변환 [docling 모듈을 이용]
        '''
        return self._docling_service.to_text(input_path)
    # 만약 docling관련해서 분리가 필요하면 분리하기.
