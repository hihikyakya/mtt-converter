import base64
import mimetypes
from pathlib import Path


def _image_to_base64(input_path: str | Path) -> tuple[str, str]:
    '''이미지를 base64로 인코딩하고 media type을 함께 반환하는 최하위 함수.'''
    media_type = mimetypes.guess_type(str(input_path))[0] or "image/png"
    image_b64 = base64.standard_b64encode(Path(input_path).read_bytes()).decode("utf-8")
    return media_type, image_b64
