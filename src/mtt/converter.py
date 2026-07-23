import os
from pathlib import Path
from typing import get_args

from mtt.service.docling import DoclingService
from mtt.service.mesh_llm import MeshLLMService
from mtt.service.caption_explaner import CaptionExplanerService
from mtt.types import ModeType, CaptionModelType as ModelType


def print_model_list():
    print(">>> model_list")
    for model_name in get_args(ModelType):
        print(model_name)



class MultiModalConverter:
    '''
    [params]
    api_key: above model's api key
    model_name: llm model name 
    ```python
    from mtt import print_model_list

    print_model_list()
    ```
    '''
    
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
        ".stl": "3dmodel",
        ".obj": "3dmodel",
        ".ply": "3dmodel",
        ".3mf": "3dmodel",
        ".glb": "3dmodel",
    }

    def __init__(self, **kwargs):
        # TODO: 나중에 임베딩 모델 api 관련해서 파라미터를 받을 수 있게하거나 할듯. 그리고 일부 시스템 프롬프트를 조절할 수 있게 할듯.
        self._docling_service = DoclingService()
        self._mesh_llm_service = MeshLLMService()
        self._caption_explaner_service = CaptionExplanerService(
            model_name=kwargs.get("model_name", "gemini-2.5-flash"), # default: gemini
            api_key=kwargs.get("api_key")
        )

    def convert(self, input_path: str | Path, sub_prompt=None, markdown=True, mode: ModeType | None = None):
        if sub_prompt is None:
            sub_prompt = "Describe image in detail."

        if mode is None:
            print("[Warning] The 'mode' argument is missing, so the 'mode' value is estimated and used.")
            _, ext = os.path.splitext(input_path)

            mode = self.MODE_ESTIMATE_MAP.get(ext.lower())
            print(f"[Warning] the mode was set to {mode}")

        if mode == "caption":
            # input 가공 가능
            return self.caption(input_path, sub_prompt=sub_prompt, markdown=markdown)
        elif mode == "ocr":
            # input 가공 가능
            return self.ocr(input_path, markdown=markdown)
        elif mode == "3dmodel":
            # input 가공 가능함.
            return self.scan3dmodel(input_path, markdown=markdown)
        elif mode in ["doc", "docs", "document"]:
            # input 가공 가능함.
            return self.doc2text(input_path, markdown=markdown)
        else:
            raise ValueError(f"There is no valid function for the mode. | mode: {mode}")



    def caption(self, input_path: str | Path, sub_prompt=None, markdown=True) -> str:
        '''
        image의 정보를 텍스트로 설명 ; 캡셔닝
        '''
        return self._caption_explaner_service.to_text(input_path, sub_prompt=sub_prompt, markdown=markdown) #이미지 용 멀티모달 임베딩 api를 찾아서 구현할듯.

    def ocr(self, input_path: str | Path, markdown=True) -> str:
        '''
        image내 텍스트를 ocr하여 얻어옴.
        '''
        return self._docling_service.to_text(input_path, markdown=markdown)

    def scan3dmodel(self, input_path: str | Path, markdown=True) -> str:
        '''
        3D 모델을 텍스트로 설명
        '''
        return self._mesh_llm_service.to_text(input_path, markdown=markdown) # TODO: point net과 parser들로 구현할 예정 ; 가능한 parser는 claude가 이미 구현한듯?

    def doc2text(self, input_path: str | Path, markdown=True) -> str:
        '''
        문서를 텍스트로 변환 [docling 모듈을 이용]
        '''
        return self._docling_service.to_text(input_path, markdown=markdown)
    

#TODO: v1이고, v2에서는 pointNet기반으로 context vector를 embedding vector로 projection해서 줄듯. (이건 아직 한참 나중에 만들 계획)
# PointNet으로 임베딩해서 기존 stl 등으로 구축해둔 DB에서 검색 후 리매핑하는 방식으로 구현 예정 (직접 파싱 대신 유사 형상 검색).