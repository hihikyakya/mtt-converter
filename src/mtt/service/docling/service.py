import re
from pathlib import Path
from docling.document_converter import DocumentConverter

from mtt.types import LangType
from mtt.utils.docling_utils import convert_document, document_to_markdown, document_to_text

_EMPTY_OCR_PLACEHOLDER: dict[LangType, str] = {
    "eng": "<!-- empty OCR result -->",
    "kor": "<!-- OCR 결과가 비어있음 -->",
}


class DoclingService:
    '''docling utils 함수를 엮어서 문서/이미지를 텍스트로 변환하는 서비스.

    문서(pdf, docx, ...)는 doc2text에, 이미지는 ocr에 재사용된다.
    docling이 이미지 입력에 대해서도 OCR 파이프라인을 자동으로 태우기 때문.
    '''

    def __init__(self, converter: DocumentConverter | None = None):
        self._converter = converter or DocumentConverter()

    def to_text(self, input_path: str | Path, markdown=True, lang: LangType = "eng") -> str:
        result = convert_document(self._converter, input_path)

        text=document_to_markdown(result) if markdown else document_to_text(result)

        # Rapid OCR exception
        placeholder = _EMPTY_OCR_PLACEHOLDER.get(lang, _EMPTY_OCR_PLACEHOLDER["eng"])
        text=re.sub(r"RapidOCR returned empty result!", placeholder, text)
        return text
