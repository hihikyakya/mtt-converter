# mtt-converter

multiform data to text converter — a multimodal Python library that converts documents, images, 3D models, and other data formats into text.

## Installation

### pip

```bash
pip install mtt-converter
```

### uv
```bash
uv add mtt-converter
```

Requires Python 3.12 or higher.

## Quick start

```python
from mtt import MultiModalConverter

mc = MultiModalConverter()

# mode is auto-detected from the file extension
text = mc.convert("report.pdf")

# or specify the mode explicitly
text = mc.convert("photo.png", mode="ocr")
```

If `mode` is not provided, it is inferred from the file extension, and a warning message is printed.

## Supported modes

| mode | Description | Supported extensions |
| --- | --- | --- |
| `doc` | Convert documents to text (uses [docling](https://github.com/docling-project/docling)) | `.pdf` `.doc` `.docx` `.ppt` `.pptx` `.xls` `.xlsx` `.html` `.htm` `.md` `.csv` |
| `ocr` | Extract text from images via OCR (uses docling) | any image file, when called directly |
| `caption` | Describe/caption image content using a multimodal LLM | `.jpg` `.jpeg` `.tif` `.tiff` `.png` `.bmp` |
| `3d_parser` | Parse 3D model files and return a geometry/metadata summary (bounding box, surface area, volume, materials, etc.) as text | `.stl` `.obj` `.ply` `.3mf` `.glb` `.gltf` `.fbx` `.step` `.stp` `.usd` `.usda` `.usdz` |

> `.fbx`, `.step`/`.stp`, and `.usd`/`.usda`/`.usdz` are supported by `scan3dmodel(..., mode="3d_parser")`, but are not yet included in automatic extension detection — pass `mode="3d_parser"` explicitly for these formats.

## Usage examples

### Document → text

```python
mc.convert("report.pdf", mode="doc")
```

### Image OCR

```python
mc.convert("scanned_page.png", mode="ocr")
```

### Image captioning

Describes an image using Gemini, GPT-4o, or Claude. The model and API key are configured when constructing `MultiModalConverter`.

```python
mc = MultiModalConverter(model_name="gemini-2.5-flash", api_key="...")
mc.convert("photo.jpg", mode="caption", sub_prompt="Describe this photo in Korean.")
```

- `model_name`: an actual API model id, one of `"gpt-4o"` / `"gemini-2.5-flash"` / `"gemini-2.5-pro"` / `"gemini-3.5-flash"` / `"gemini-3.5-pro"` / `"claude-opus-4-8"` (default: `"gemini-2.5-flash"`)
- If `api_key` is not provided, each provider's SDK reads it automatically from the corresponding environment variable (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
- If `sub_prompt` is not provided, the default prompt (`"Describe image in detail."`) is used.
    - This may incur **token cost**.

### 3D model parsing

```python
mc.convert("model.stl", mode="3d-parser")
```

Returns a text summary including solid name, triangle count, bounding box, surface area, and (approximate) volume.

For CAD/scene formats, the summary is tailored to the format instead of raw triangle stats:

```python
mc.convert("part.step", mode="3d-parser")   # STEP header (author, organization, schema) + PRODUCT names
mc.convert("scene.usdz", mode="3d-parser")  # USD prim hierarchy, or USDZ package contents
mc.convert("model.fbx", mode="3d-parser")   # FBX models/materials/textures
```

- `.step`/`.stp` are parsed as plain text (no OpenCascade dependency required) to extract header metadata and `PRODUCT` entities.
- `.usd`/`.usda` are parsed via the Pixar USD SDK (`pxr`) when available, falling back to a plain-text `def Type "Name"` scan otherwise; `.usdz` archives are also listed as a zip package.
- ASCII `.fbx` files are parsed as text; binary `.fbx` files require the optional `pyassimp` dependency.

`.glb`/`.gltf` are also supported, and are already covered by automatic extension detection:

```python
mc.convert("scene.gltf")  # mode is inferred as "3d-parser"
mc.convert("scene.glb")   # ASCII glTF (JSON) or binary GLB, detected automatically
```

## Output format

Every `convert` method and mode-specific method accepts a `markdown` parameter.

```python
mc.convert("report.pdf", markdown=False)  # plain text without markdown formatting
```

The default is `markdown=True`.

## Roadmap (current status as of v1)

- ✅ Document conversion (docling)
- ✅ Image OCR (docling)
- ✅ Image captioning (Gemini / GPT-4o / Claude)
- ✅ 3D model parsing: `.stl`, `.obj`, `.ply`, `.3mf`
- ✅ 3D model parsing: `.fbx`, `.step`/`.stp`, `.usd`/`.usda`/`.usdz`
- ✅ 3D model parsing: `.glb`, `.gltf`
- 🚧 Add `.fbx`, `.step`/`.stp`, `.usd`/`.usda`/`.usdz` to automatic extension detection
- 🚧 PointNet-based embeddings: encode models, build a similarity-search DB from the existing parsers, and retrieve/remap similar shapes (planned for v2)
- 🚧 Provide an embedding function (if time permits)

## License

[MIT](./LICENSE)
