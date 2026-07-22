from pathlib import Path

from mtt.utils.tools.stl_parser import _is_binary_stl, _parse_binary_stl, _parse_ascii_stl, _compute_stats
from mtt.utils.tools.obj_parser import _parse_obj
from mtt.utils.tools.ply_parser import _parse_ply
from mtt.utils.tools.threemf_parser import _parse_3mf
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