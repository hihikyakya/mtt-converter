from pathlib import Path

from docling.document_converter import DocumentConverter

from mtt.utils.docling_utils import convert_document, document_to_markdown


class DoclingService:
    '''docling utils 함수를 엮어서 문서/이미지를 텍스트로 변환하는 서비스.

    문서(pdf, docx, ...)는 doc2text에, 이미지는 ocr에 재사용된다.
    docling이 이미지 입력에 대해서도 OCR 파이프라인을 자동으로 태우기 때문.
    '''

    def __init__(self, converter: DocumentConverter | None = None):
        self._converter = converter or DocumentConverter()

    def to_text(self, input_path: str | Path) -> str:
        result = convert_document(self._converter, input_path)
        return document_to_markdown(result)
