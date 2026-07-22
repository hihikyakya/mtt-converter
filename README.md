# mtt-converter

multiform data to text converter — 문서, 이미지, 3D 모델 등 다양한 형태의 데이터를 텍스트로 변환해주는 멀티모달 파이썬 라이브러리.

## 설치

```bash
pip install mtt-converter
```

Python 3.12 이상이 필요합니다.

## 빠른 시작

```python
from mtt import MultiModalConverter

mc = MultiModalConverter()

# 확장자를 보고 mode를 자동으로 추정
text = mc.convert("report.pdf")

# mode를 직접 지정
text = mc.convert("photo.png", mode="ocr")
```

`mode`를 넘기지 않으면 파일 확장자로 자동 추정하며, 이때 경고 메시지가 출력됩니다.

## 지원하는 mode

| mode | 설명 | 지원 확장자 |
| --- | --- | --- |
| `doc` | 문서를 텍스트로 변환 ([docling](https://github.com/docling-project/docling) 사용) | `.pdf` `.doc` `.docx` `.ppt` `.pptx` `.xls` `.xlsx` `.html` `.htm` `.md` `.csv` |
| `ocr` | 이미지 속 텍스트를 OCR로 추출 (docling 사용) | 직접 호출 시 임의의 이미지 파일 |
| `caption` | 이미지 내용을 멀티모달 LLM으로 캡셔닝/설명 | `.jpg` `.jpeg` `.tif` `.tiff` `.png` `.bmp` |
| `3dmodel` | 3D 모델 파일을 파싱해 지오메트리 요약(바운딩 박스, 표면적, 부피 등)을 텍스트로 반환 | `.stl` `.obj` `.ply` `.3mf` |

> `.glb`도 `3dmodel`로 추정되지만 아직 파서가 구현되어 있지 않습니다.

## 사용 예시

### 문서 → 텍스트

```python
mc.convert("report.pdf", mode="doc")
```

### 이미지 OCR

```python
mc.convert("scanned_page.png", mode="ocr")
```

### 이미지 캡셔닝

Gemini, GPT-4o, Claude 중 하나로 이미지를 설명합니다. 사용할 모델과 API 키는 `MultiModalConverter` 생성 시 지정합니다.
* **Token cost**가 발생할 수 있습니다.

```python
mc = MultiModalConverter(model_name="gemini-3.5-flash", api_key="...")
mc.convert("photo.jpg", mode="caption", sub_prompt="이 사진을 한국어로 설명해줘.")
```

- `model_name`: `"gemini-*"` / `"gpt-4o"` / `"claude-*"` 중 하나의 실제 API 모델 id (기본값 `"gemini-3.5-flash"`)
- `api_key`를 넘기지 않으면 각 provider SDK가 환경 변수(`GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)에서 자동으로 읽습니다.
- `sub_prompt`를 지정하지 않으면 기본 프롬프트(`"Describe image in detail."`)가 사용됩니다.

### 3D 모델 파싱

```python
mc.convert("model.stl", mode="3dmodel")
```

솔리드 이름, 삼각형 개수, 바운딩 박스, 표면적, 부피(근사) 등을 요약한 텍스트를 반환합니다.

## 출력 형식

모든 `convert`/모드별 메서드는 `markdown` 파라미터를 받습니다.

```python
mc.convert("report.pdf", markdown=False)  # 마크다운 서식 없는 일반 텍스트
```

기본값은 `markdown=True`입니다.

## 로드맵 (v1 기준 현황)

- ✅ 문서 변환 (docling)
- ✅ 이미지 OCR (docling)
- ✅ 이미지 캡셔닝 (Gemini / GPT-4o / Claude)
- ✅ 3D 모델 파싱: `.stl`, `.obj`, `.ply`, `.3mf`
- 🚧 3D 모델 파싱: `.step`/`.stp`, `.usd`/`.usdz`, `.fbx` — PointNet 기반 임베딩 후 기존 파서로 구축한 DB에서 유사 형상을 검색/리매핑하는 방식으로 구현 예정 (v2)
- 🚧 임베딩 함수 제공 (시간이 되면)

## 라이선스

[MIT](./LICENSE)
