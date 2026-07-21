from pathlib import Path

from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter


def convert_document(converter: DocumentConverter, input_path: str | Path) -> ConversionResult:
    '''docling converter로 파일(문서/이미지)을 파싱하는 최하위 함수.'''
    return converter.convert(input_path)


def document_to_markdown(result: ConversionResult) -> str:
    '''ConversionResult에서 마크다운 텍스트를 추출하는 최하위 함수.'''
    return result.document.export_to_markdown()
