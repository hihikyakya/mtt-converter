from __future__ import annotations


def fan_triangulate(
    vertices: list[tuple[float, float, float]], face_indices: list[int]
) -> list[tuple[float, float, float]]:
    '''다각형 face(0-indexed vertex index list)를 fan 방식으로 삼각분할해 flat 삼각형 정점 리스트를 만든다.'''
    triangles = []
    for i in range(1, len(face_indices) - 1):
        triangles.extend([
            vertices[face_indices[0]],
            vertices[face_indices[i]],
            vertices[face_indices[i + 1]],
        ])
    return triangles


def compute_triangle_stats(vertices: list[tuple[float, float, float]]) -> dict:
    '''flat 삼각형 정점 리스트(3개씩 한 삼각형)에서 바운딩 박스/표면적/부피를 계산한다.'''
    if not vertices:
        return {"bbox_min": None, "bbox_max": None, "surface_area": 0.0, "signed_volume": 0.0}

    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    bbox_min = (min(xs), min(ys), min(zs))
    bbox_max = (max(xs), max(ys), max(zs))

    surface_area = 0.0
    signed_volume = 0.0
    triangle_count = len(vertices) // 3

    for i in range(triangle_count):
        v0 = vertices[i * 3]
        v1 = vertices[i * 3 + 1]
        v2 = vertices[i * 3 + 2]

        ux, uy, uz = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
        vx, vy, vz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
        cx = uy * vz - uz * vy
        cy = uz * vx - ux * vz
        cz = ux * vy - uy * vx
        surface_area += 0.5 * (cx ** 2 + cy ** 2 + cz ** 2) ** 0.5

        signed_volume += (
            v0[0] * (v1[1] * v2[2] - v2[1] * v1[2])
            - v0[1] * (v1[0] * v2[2] - v2[0] * v1[2])
            + v0[2] * (v1[0] * v2[1] - v2[0] * v1[1])
        ) / 6.0

    return {
        "bbox_min": bbox_min,
        "bbox_max": bbox_max,
        "surface_area": surface_area,
        "signed_volume": signed_volume,
    }


def format_mesh_report(
    file_name: str,
    format_label: str,
    solid_name: str,
    face_count: int,
    stats: dict,
    markdown: bool = True,
    format_detail: str | None = None,
) -> str:
    '''3D 메시 파싱 결과(obj/ply/3mf 공통)를 요약 문자열로 포맷한다.'''
    bbox_min = stats["bbox_min"]
    bbox_max = stats["bbox_max"]
    size = None
    if bbox_min and bbox_max:
        size = tuple(round(bmax - bmin, 4) for bmin, bmax in zip(bbox_min, bbox_max))

    if markdown:
        lines = [f"# {format_label} 파싱 결과: {file_name}", ""]
        if format_detail:
            lines.append(f"- **포맷**: {format_detail}")
        lines += [
            f"- **솔리드 이름**: {solid_name}",
            f"- **삼각형(facet) 개수**: {face_count:,}",
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
        lines = [f"{format_label} 파싱 결과: {file_name}"]
        if format_detail:
            lines.append(f"포맷: {format_detail}")
        lines += [
            f"솔리드 이름: {solid_name}",
            f"삼각형 개수: {face_count}",
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
