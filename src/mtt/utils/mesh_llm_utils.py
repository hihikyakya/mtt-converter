from pathlib import Path

from mtt.utils.tools.stl_parser import _is_binary_stl, _parse_binary_stl, _parse_ascii_stl, _compute_stats
from mtt.utils.tools.obj_parser import _parse_obj
from mtt.utils.tools.ply_parser import _parse_ply
from mtt.utils.tools.threemf_parser import _parse_3mf
from mtt.utils.tools.fbx_parser import _is_binary_fbx, _parse_ascii_fbx, _parse_binary_fbx
from mtt.utils.tools.step_parser import _parse_step
from mtt.utils.tools.usd_parser import _is_usdz, _list_usdz_members, _parse_usd_with_pxr, _parse_usd_text
from mtt.utils.tools.mesh_geometry import fan_triangulate, compute_triangle_stats, format_mesh_report


def parsing_stl(input_path: str | Path, markdown: bool = True) -> str:
    """
    STL 파일을 파싱해 요약 정보를 문자열로 반환한다.
 
    Args:
        input_path: STL 파일 경로 (.stl)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환
 
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
    bbox_min = stats["bbox_min"]
    bbox_max = stats["bbox_max"]
    size = None
    if bbox_min and bbox_max:
        size = tuple(round(bmax - bmin, 4) for bmin, bmax in zip(bbox_min, bbox_max))
 
    if markdown:
        lines = [
            f"# STL 파싱 결과: {path.name}",
            "",
            f"- **포맷**: {fmt_type} STL",
            f"- **솔리드 이름**: {mesh.name}",
            f"- **삼각형(facet) 개수**: {mesh.triangle_count:,}",
        ]
        if bbox_min and bbox_max:
            lines += [
                f"- **바운딩 박스 최소값 (x,y,z)**: {tuple(round(v, 4) for v in bbox_min)}",
                f"- **바운딩 박스 최대값 (x,y,z)**: {tuple(round(v, 4) for v in bbox_max)}",
                f"- **모델 크기 (dx,dy,dz)**: {size}",
            ]
        lines += [
            f"- **표면적(surface area)**: {stats['surface_area']:.4f}",
            f"- **부피(volume, 근사)**: {abs(stats['signed_volume']):.4f}"
            + ("" if stats['signed_volume'] >= 0 else "  ⚠️ (법선 방향이 뒤집혀 있을 수 있음)"),
        ]
        return "\n".join(lines)
    else:
        lines = [
            f"STL 파싱 결과: {path.name}",
            f"포맷: {fmt_type} STL",
            f"솔리드 이름: {mesh.name}",
            f"삼각형 개수: {mesh.triangle_count}",
        ]
        if bbox_min and bbox_max:
            lines += [
                f"바운딩 박스 최소값: {tuple(round(v, 4) for v in bbox_min)}",
                f"바운딩 박스 최대값: {tuple(round(v, 4) for v in bbox_max)}",
                f"모델 크기: {size}",
            ]
        lines += [
            f"표면적: {stats['surface_area']:.4f}",
            f"부피(근사): {abs(stats['signed_volume']):.4f}",
        ]
        return "\n".join(lines)


def parsing_obj(input_path: str | Path, markdown: bool = True) -> str:
    """
    OBJ(Wavefront) 파일을 파싱해 요약 정보를 문자열로 반환한다.

    Args:
        input_path: OBJ 파일 경로 (.obj)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환

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
    )


def parsing_ply(input_path: str | Path, markdown: bool = True) -> str:
    """
    PLY(Stanford Triangle Format) 파일을 파싱해 요약 정보를 문자열로 반환한다.

    Args:
        input_path: PLY 파일 경로 (.ply)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환

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
    )


def parsing_3mf(input_path: str | Path, markdown: bool = True) -> str:
    """
    3MF(3D Manufacturing Format) 파일을 파싱해 요약 정보를 문자열로 반환한다.

    Args:
        input_path: 3MF 파일 경로 (.3mf)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    data = _parse_3mf(path)

    triangle_vertices = []
    for v1, v2, v3 in data.triangles:
        triangle_vertices.extend([data.vertices[v1], data.vertices[v2], data.vertices[v3]])

    stats = compute_triangle_stats(triangle_vertices)

    return format_mesh_report(
        file_name=path.name,
        format_label="3MF",
        format_detail=f"오브젝트 {data.object_count}개",
        solid_name=path.stem,
        face_count=len(data.triangles),
        stats=stats,
        markdown=markdown,
    )


def parsing_fbx(input_path: str | Path, markdown: bool = True) -> str:
    """
    FBX 파일을 파싱해 요약 정보를 문자열로 반환한다.

    ASCII FBX는 Model/Material/Texture 블록을 텍스트로 직접 파싱하고,
    Binary FBX는 regex로 다루기 어려워 pyassimp(Assimp)로 로드해 mesh/material을 추출한다.

    Args:
        input_path: FBX 파일 경로 (.fbx)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    raw = path.read_bytes()

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
            f"# FBX 파싱 결과: {path.name}",
            "",
            f"- **포맷**: {fmt_type} FBX",
            f"- **모델/메시 개수**: {len(model_names):,}",
            f"- **모델/메시 이름**: {', '.join(model_names) if model_names else '(없음)'}",
            f"- **머티리얼 개수**: {len(material_names):,}",
            f"- **머티리얼 이름**: {', '.join(material_names) if material_names else '(없음)'}",
        ]
        if texture_names:
            lines.append(f"- **텍스처**: {', '.join(texture_names)}")
        return "\n".join(lines)
    else:
        lines = [
            f"FBX 파싱 결과: {path.name}",
            f"포맷: {fmt_type} FBX",
            f"모델/메시 개수: {len(model_names)}",
            f"모델/메시 이름: {', '.join(model_names) if model_names else '(없음)'}",
            f"머티리얼 개수: {len(material_names)}",
            f"머티리얼 이름: {', '.join(material_names) if material_names else '(없음)'}",
        ]
        if texture_names:
            lines.append(f"텍스처: {', '.join(texture_names)}")
        return "\n".join(lines)


def parsing_step(input_path: str | Path, markdown: bool = True) -> str:
    """
    STEP/STP(ISO-10303-21) 파일을 파싱해 헤더/PRODUCT 정보를 문자열로 반환한다.

    STEP은 내부적으로 텍스트 기반 entity 구조라 OpenCascade 없이도
    HEADER 섹션(FILE_DESCRIPTION/FILE_NAME/FILE_SCHEMA)과 PRODUCT entity를
    정규식으로 추출한다.

    Args:
        input_path: STEP 파일 경로 (.step/.stp)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    text = path.read_text(encoding="utf-8", errors="replace")
    data = _parse_step(text)
    header = data.header

    if markdown:
        lines = [
            f"# STEP 파싱 결과: {path.name}",
            "",
            f"- **설명(DESCRIPTION)**: {header.description or '(없음)'}",
            f"- **스키마 버전**: {header.schema_version or '(없음)'}",
            f"- **원본 파일명**: {header.file_name or '(없음)'}",
            f"- **작성 시각**: {header.timestamp or '(없음)'}",
            f"- **작성자(AUTHOR)**: {', '.join(header.author) if header.author else '(없음)'}",
            f"- **조직(ORGANIZATION)**: {', '.join(header.organization) if header.organization else '(없음)'}",
            f"- **FILE_SCHEMA**: {', '.join(header.schema) if header.schema else '(없음)'}",
            f"- **PRODUCT 개수**: {len(data.product_names):,}",
            f"- **PRODUCT 이름**: {', '.join(data.product_names) if data.product_names else '(없음)'}",
        ]
        return "\n".join(lines)
    else:
        lines = [
            f"STEP 파싱 결과: {path.name}",
            f"설명: {header.description or '(없음)'}",
            f"스키마 버전: {header.schema_version or '(없음)'}",
            f"원본 파일명: {header.file_name or '(없음)'}",
            f"작성 시각: {header.timestamp or '(없음)'}",
            f"작성자: {', '.join(header.author) if header.author else '(없음)'}",
            f"조직: {', '.join(header.organization) if header.organization else '(없음)'}",
            f"FILE_SCHEMA: {', '.join(header.schema) if header.schema else '(없음)'}",
            f"PRODUCT 개수: {len(data.product_names)}",
            f"PRODUCT 이름: {', '.join(data.product_names) if data.product_names else '(없음)'}",
        ]
        return "\n".join(lines)


def parsing_usd(input_path: str | Path, markdown: bool = True) -> str:
    """
    USD/USDA/USDZ 파일을 파싱해 prim 계층 정보를 문자열로 반환한다.

    가능하면 Pixar USD SDK(pxr)로 stage를 순회해 전체 prim 목록을 얻고,
    pxr이 없으면 ASCII USD 텍스트에서 `def Type "Name"` 선언을 정규식으로 추출한다.
    USDZ는 texture/material 등을 담은 zip 패키지이므로 내부 파일 목록도 함께 보여준다.

    Args:
        input_path: USD 파일 경로 (.usd/.usda/.usdz)
        markdown: True면 마크다운 형식, False면 일반 텍스트로 반환

    Returns:
        파싱 결과 요약 문자열
    """
    path = Path(input_path)
    is_usdz = _is_usdz(path)

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
    fmt_type = "USDZ (zip 패키지)" if is_usdz else "USD/USDA"

    if markdown:
        lines = [
            f"# USD 파싱 결과: {path.name}",
            "",
            f"- **포맷**: {fmt_type}",
            f"- **Prim 개수**: {len(prims):,}",
        ]
        if prim_lines:
            lines.append("- **Prim 목록**:")
            lines += [f"  - {line}" for line in prim_lines]
        if usdz_members:
            lines.append(f"- **내부 파일 개수**: {len(usdz_members):,}")
            lines.append("- **내부 파일 목록**:")
            lines += [f"  - {member}" for member in usdz_members]
        return "\n".join(lines)
    else:
        lines = [
            f"USD 파싱 결과: {path.name}",
            f"포맷: {fmt_type}",
            f"Prim 개수: {len(prims)}",
        ]
        if prim_lines:
            lines.append("Prim 목록:")
            lines += [f"  {line}" for line in prim_lines]
        if usdz_members:
            lines.append(f"내부 파일 개수: {len(usdz_members)}")
            lines.append("내부 파일 목록:")
            lines += [f"  {member}" for member in usdz_members]
        return "\n".join(lines)