from pathlib import Path

from mtt.types import LangType
from mtt.utils.tools.stl_parser import _is_binary_stl, _parse_binary_stl, _parse_ascii_stl, _compute_stats
from mtt.utils.tools.obj_parser import _parse_obj
from mtt.utils.tools.ply_parser import _parse_ply
from mtt.utils.tools.threemf_parser import _parse_3mf
from mtt.utils.tools.fbx_parser import _is_binary_fbx, _parse_ascii_fbx, _parse_binary_fbx
from mtt.utils.tools.step_parser import _parse_step
from mtt.utils.tools.usd_parser import _is_usdz, _list_usdz_members, _parse_usd_with_pxr, _parse_usd_text
from mtt.utils.tools.mesh_geometry import fan_triangulate, compute_triangle_stats, format_mesh_report

_FBX_LABELS: dict[LangType, dict[str, str]] = {
    "eng": {
        "title": "FBX Parsing Result",
        "format": "Format",
        "model_count": "Model/mesh count",
        "model_names": "Model/mesh names",
        "material_count": "Material count",
        "material_names": "Material names",
        "textures": "Textures",
        "none": "(none)",
    },
    "kor": {
        "title": "FBX 파싱 결과",
        "format": "포맷",
        "model_count": "모델/메시 개수",
        "model_names": "모델/메시 이름",
        "material_count": "머티리얼 개수",
        "material_names": "머티리얼 이름",
        "textures": "텍스처",
        "none": "(없음)",
    },
}

_STEP_LABELS: dict[LangType, dict[str, str]] = {
    "eng": {
        "title": "STEP Parsing Result",
        "description": "Description (DESCRIPTION)",
        "schema_version": "Schema version",
        "file_name": "Original file name",
        "timestamp": "Timestamp",
        "author": "Author (AUTHOR)",
        "organization": "Organization (ORGANIZATION)",
        "schema": "FILE_SCHEMA",
        "product_count": "PRODUCT count",
        "product_names": "PRODUCT names",
        "none": "(none)",
    },
    "kor": {
        "title": "STEP 파싱 결과",
        "description": "설명(DESCRIPTION)",
        "schema_version": "스키마 버전",
        "file_name": "원본 파일명",
        "timestamp": "작성 시각",
        "author": "작성자(AUTHOR)",
        "organization": "조직(ORGANIZATION)",
        "schema": "FILE_SCHEMA",
        "product_count": "PRODUCT 개수",
        "product_names": "PRODUCT 이름",
        "none": "(없음)",
    },
}

_USD_LABELS: dict[LangType, dict[str, str]] = {
    "eng": {
        "title": "USD Parsing Result",
        "format": "Format",
        "usdz_detail": "USDZ (zip package)",
        "usd_detail": "USD/USDA",
        "prim_count": "Prim count",
        "prim_list": "Prim list",
        "member_count": "Internal file count",
        "member_list": "Internal file list",
    },
    "kor": {
        "title": "USD 파싱 결과",
        "format": "포맷",
        "usdz_detail": "USDZ (zip 패키지)",
        "usd_detail": "USD/USDA",
        "prim_count": "Prim 개수",
        "prim_list": "Prim 목록",
        "member_count": "내부 파일 개수",
        "member_list": "내부 파일 목록",
    },
}


def parsing_stl(input_path: str | Path, markdown: bool = True, lang: LangType = "eng") -> str:
    """
    STL 파일을 파싱해 요약 정보를 문자열로 반환한다.

    Args:
        input_path: STL 파일 경로 (.stl)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환
        lang: 출력 언어("eng"/"kor")

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    raw = path.read_bytes()

    if _is_binary_stl(raw):
        mesh = _parse_binary_stl(raw)
    else:
        mesh = _parse_ascii_stl(raw.decode("ascii", errors="replace"))

    stats = _compute_stats(mesh)
    fmt_type = "Binary" if mesh.is_binary else "ASCII"

    return format_mesh_report(
        file_name=path.name,
        format_label="STL",
        format_detail=f"{fmt_type} STL",
        solid_name=mesh.name,
        face_count=mesh.triangle_count,
        stats=stats,
        markdown=markdown,
        lang=lang,
    )


def parsing_obj(input_path: str | Path, markdown: bool = True, lang: LangType = "eng") -> str:
    """
    OBJ(Wavefront) 파일을 파싱해 요약 정보를 문자열로 반환한다.

    Args:
        input_path: OBJ 파일 경로 (.obj)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환
        lang: 출력 언어("eng"/"kor")

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    obj = _parse_obj(path.read_text(encoding="utf-8", errors="replace"))

    triangle_vertices = []
    for face in obj.faces:
        triangle_vertices.extend(fan_triangulate(obj.vertices, face))

    stats = compute_triangle_stats(triangle_vertices)

    return format_mesh_report(
        file_name=path.name,
        format_label="OBJ",
        solid_name=obj.name,
        face_count=len(obj.faces),
        stats=stats,
        markdown=markdown,
        lang=lang,
    )


def parsing_ply(input_path: str | Path, markdown: bool = True, lang: LangType = "eng") -> str:
    """
    PLY(Stanford Triangle Format) 파일을 파싱해 요약 정보를 문자열로 반환한다.

    Args:
        input_path: PLY 파일 경로 (.ply)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환
        lang: 출력 언어("eng"/"kor")

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    ply = _parse_ply(path.read_bytes())

    triangle_vertices = []
    for face in ply.faces:
        triangle_vertices.extend(fan_triangulate(ply.vertices, face))

    stats = compute_triangle_stats(triangle_vertices)

    return format_mesh_report(
        file_name=path.name,
        format_label="PLY",
        format_detail="Binary PLY" if ply.is_binary else "ASCII PLY",
        solid_name=path.stem,
        face_count=ply.face_count,
        stats=stats,
        markdown=markdown,
        lang=lang,
    )


def parsing_3mf(input_path: str | Path, markdown: bool = True, lang: LangType = "eng") -> str:
    """
    3MF(3D Manufacturing Format) 파일을 파싱해 요약 정보를 문자열로 반환한다.

    Args:
        input_path: 3MF 파일 경로 (.3mf)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환
        lang: 출력 언어("eng"/"kor")

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    data = _parse_3mf(path)

    triangle_vertices = []
    for v1, v2, v3 in data.triangles:
        triangle_vertices.extend([data.vertices[v1], data.vertices[v2], data.vertices[v3]])

    stats = compute_triangle_stats(triangle_vertices)

    object_detail = f"{data.object_count} objects" if lang == "eng" else f"오브젝트 {data.object_count}개"

    return format_mesh_report(
        file_name=path.name,
        format_label="3MF",
        format_detail=object_detail,
        solid_name=path.stem,
        face_count=len(data.triangles),
        stats=stats,
        markdown=markdown,
        lang=lang,
    )


def parsing_fbx(input_path: str | Path, markdown: bool = True, lang: LangType = "eng") -> str:
    """
    FBX 파일을 파싱해 요약 정보를 문자열로 반환한다.

    ASCII FBX는 Model/Material/Texture 블록을 텍스트로 직접 파싱하고,
    Binary FBX는 regex로 다루기 어려워 pyassimp(Assimp)로 로드해 mesh/material을 추출한다.

    Args:
        input_path: FBX 파일 경로 (.fbx)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환
        lang: 출력 언어("eng"/"kor")

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    raw = path.read_bytes()
    labels = _FBX_LABELS.get(lang, _FBX_LABELS["eng"])

    if _is_binary_fbx(raw):
        fbx = _parse_binary_fbx(path)
        fmt_type = "Binary"
    else:
        fbx = _parse_ascii_fbx(raw.decode("utf-8", errors="replace"))
        fmt_type = "ASCII"

    model_names = [m.name for m in fbx.models]
    material_names = [m.name for m in fbx.materials]
    texture_names = [t.name for t in fbx.textures]

    if markdown:
        lines = [
            f"# {labels['title']}: {path.name}",
            "",
            f"- **{labels['format']}**: {fmt_type} FBX",
            f"- **{labels['model_count']}**: {len(model_names):,}",
            f"- **{labels['model_names']}**: {', '.join(model_names) if model_names else labels['none']}",
            f"- **{labels['material_count']}**: {len(material_names):,}",
            f"- **{labels['material_names']}**: {', '.join(material_names) if material_names else labels['none']}",
        ]
        if texture_names:
            lines.append(f"- **{labels['textures']}**: {', '.join(texture_names)}")
        return "\n".join(lines)
    else:
        lines = [
            f"{labels['title']}: {path.name}",
            f"{labels['format']}: {fmt_type} FBX",
            f"{labels['model_count']}: {len(model_names)}",
            f"{labels['model_names']}: {', '.join(model_names) if model_names else labels['none']}",
            f"{labels['material_count']}: {len(material_names)}",
            f"{labels['material_names']}: {', '.join(material_names) if material_names else labels['none']}",
        ]
        if texture_names:
            lines.append(f"{labels['textures']}: {', '.join(texture_names)}")
        return "\n".join(lines)


def parsing_step(input_path: str | Path, markdown: bool = True, lang: LangType = "eng") -> str:
    """
    STEP/STP(ISO-10303-21) 파일을 파싱해 헤더/PRODUCT 정보를 문자열로 반환한다.

    STEP은 내부적으로 텍스트 기반 entity 구조라 OpenCascade 없이도
    HEADER 섹션(FILE_DESCRIPTION/FILE_NAME/FILE_SCHEMA)과 PRODUCT entity를
    정규식으로 추출한다.

    Args:
        input_path: STEP 파일 경로 (.step/.stp)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환
        lang: 출력 언어("eng"/"kor")

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    text = path.read_text(encoding="utf-8", errors="replace")
    data = _parse_step(text)
    header = data.header
    labels = _STEP_LABELS.get(lang, _STEP_LABELS["eng"])
    none = labels["none"]

    if markdown:
        lines = [
            f"# {labels['title']}: {path.name}",
            "",
            f"- **{labels['description']}**: {header.description or none}",
            f"- **{labels['schema_version']}**: {header.schema_version or none}",
            f"- **{labels['file_name']}**: {header.file_name or none}",
            f"- **{labels['timestamp']}**: {header.timestamp or none}",
            f"- **{labels['author']}**: {', '.join(header.author) if header.author else none}",
            f"- **{labels['organization']}**: {', '.join(header.organization) if header.organization else none}",
            f"- **{labels['schema']}**: {', '.join(header.schema) if header.schema else none}",
            f"- **{labels['product_count']}**: {len(data.product_names):,}",
            f"- **{labels['product_names']}**: {', '.join(data.product_names) if data.product_names else none}",
        ]
        return "\n".join(lines)
    else:
        lines = [
            f"{labels['title']}: {path.name}",
            f"{labels['description']}: {header.description or none}",
            f"{labels['schema_version']}: {header.schema_version or none}",
            f"{labels['file_name']}: {header.file_name or none}",
            f"{labels['timestamp']}: {header.timestamp or none}",
            f"{labels['author']}: {', '.join(header.author) if header.author else none}",
            f"{labels['organization']}: {', '.join(header.organization) if header.organization else none}",
            f"{labels['schema']}: {', '.join(header.schema) if header.schema else none}",
            f"{labels['product_count']}: {len(data.product_names)}",
            f"{labels['product_names']}: {', '.join(data.product_names) if data.product_names else none}",
        ]
        return "\n".join(lines)


def parsing_usd(input_path: str | Path, markdown: bool = True, lang: LangType = "eng") -> str:
    """
    USD/USDA/USDZ 파일을 파싱해 prim 계층 정보를 문자열로 반환한다.

    가능하면 Pixar USD SDK(pxr)로 stage를 순회해 전체 prim 목록을 얻고,
    pxr이 없으면 ASCII USD 텍스트에서 `def Type "Name"` 선언을 정규식으로 추출한다.
    USDZ는 texture/material 등을 담은 zip 패키지이므로 내부 파일 목록도 함께 보여준다.

    Args:
        input_path: USD 파일 경로 (.usd/.usda/.usdz)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환
        lang: 출력 언어("eng"/"kor")

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    is_usdz = _is_usdz(path)
    labels = _USD_LABELS.get(lang, _USD_LABELS["eng"])

    try:
        data = _parse_usd_with_pxr(path)
    except ImportError:
        if is_usdz:
            data = None
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
            data = _parse_usd_text(text)

    prims = data.prims if data is not None else []
    usdz_members = _list_usdz_members(path) if is_usdz else []

    prim_lines = [f"{prim.name} ({prim.type_name})" for prim in prims]
    fmt_type = labels["usdz_detail"] if is_usdz else labels["usd_detail"]

    if markdown:
        lines = [
            f"# {labels['title']}: {path.name}",
            "",
            f"- **{labels['format']}**: {fmt_type}",
            f"- **{labels['prim_count']}**: {len(prims):,}",
        ]
        if prim_lines:
            lines.append(f"- **{labels['prim_list']}**:")
            lines += [f"  - {line}" for line in prim_lines]
        if usdz_members:
            lines.append(f"- **{labels['member_count']}**: {len(usdz_members):,}")
            lines.append(f"- **{labels['member_list']}**:")
            lines += [f"  - {member}" for member in usdz_members]
        return "\n".join(lines)
    else:
        lines = [
            f"{labels['title']}: {path.name}",
            f"{labels['format']}: {fmt_type}",
            f"{labels['prim_count']}: {len(prims)}",
        ]
        if prim_lines:
            lines.append(f"{labels['prim_list']}:")
            lines += [f"  {line}" for line in prim_lines]
        if usdz_members:
            lines.append(f"{labels['member_count']}: {len(usdz_members)}")
            lines.append(f"{labels['member_list']}:")
            lines += [f"  {member}" for member in usdz_members]
        return "\n".join(lines)