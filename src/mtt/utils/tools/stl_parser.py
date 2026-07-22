from __future__ import annotations
 
import struct
from dataclasses import dataclass, field
 
 
@dataclass
class STLData:
    name: str
    is_binary: bool
    triangle_count: int
    # 각 삼각형: (normal(3), v0(3), v1(3), v2(3))
    normals: list[tuple[float, float, float]] = field(default_factory=list)
    vertices: list[tuple[float, float, float]] = field(default_factory=list)  # flat, 3개씩 삼각형
 
 
def _is_binary_stl(data: bytes) -> bool:
    """
    STL이 ASCII인지 Binary인지 판별.
 
    함정: 일부 binary STL은 헤더 80바이트 안에 우연히 'solid'라는
    단어가 들어갈 수 있음. 그래서 단순히 앞 5글자만 보고 판단하면 안 되고,
    'solid'로 시작하더라도 실제로 ASCII 문법(facet/vertex 키워드)이
    이어지는지까지 확인해야 안전하다.
    """
    if len(data) < 84:
        return False
 
    starts_with_solid = data[:5].lower() == b"solid"
 
    if not starts_with_solid:
        return True  # solid로 시작 안 하면 무조건 binary
 
    # solid로 시작하더라도, binary 헤더(80byte)+triangle count 뒤의
    # 파일 크기가 실제로 "80 + 4 + N*50" 공식과 맞아떨어지면 binary로 판단
    triangle_count = struct.unpack("<I", data[80:84])[0]
    expected_binary_size = 84 + triangle_count * 50
    if expected_binary_size == len(data):
        return False if b"facet" in data[:200].lower() and b"endsolid" in data.lower()[-200:] else True
 
    return False
 
 
def _parse_binary_stl(data: bytes) -> STLData:
    header = data[0:80].rstrip(b"\x00").decode("ascii", errors="replace").strip()
    (triangle_count,) = struct.unpack("<I", data[80:84])
 
    normals = []
    vertices = []
    offset = 84
    # 삼각형 1개 = 50바이트: normal(12) + v0(12) + v1(12) + v2(12) + attr(2)
    record_fmt = "<12fH"
    record_size = struct.calcsize(record_fmt)
 
    for _ in range(triangle_count):
        chunk = data[offset: offset + record_size]
        if len(chunk) < record_size:
            break  # 파일이 잘려있는 경우 방어
        nx, ny, nz, v0x, v0y, v0z, v1x, v1y, v1z, v2x, v2y, v2z, _attr = struct.unpack(record_fmt, chunk)
        normals.append((nx, ny, nz))
        vertices.extend([(v0x, v0y, v0z), (v1x, v1y, v1z), (v2x, v2y, v2z)])
        offset += record_size
 
    return STLData(
        name=header or "(binary)",
        is_binary=True,
        triangle_count=len(normals),
        normals=normals,
        vertices=vertices,
    )
 
 
def _parse_ascii_stl(text: str) -> STLData:
    lines = text.splitlines()
    name = "(ascii)"
    normals: list[tuple[float, float, float]] = []
    vertices: list[tuple[float, float, float]] = []
 
    current_normal = None
    current_verts: list[tuple[float, float, float]] = []
 
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        tokens = line.split()
        keyword = tokens[0].lower()
 
        if keyword == "solid":
            name = " ".join(tokens[1:]) or name
        elif keyword == "facet" and len(tokens) >= 5:
            # facet normal nx ny nz
            current_normal = tuple(float(x) for x in tokens[2:5])
            current_verts = []
        elif keyword == "vertex" and len(tokens) >= 4:
            current_verts.append(tuple(float(x) for x in tokens[1:4]))
        elif keyword == "endfacet":
            if current_normal is not None and len(current_verts) == 3:
                normals.append(current_normal)
                vertices.extend(current_verts)
            current_normal = None
            current_verts = []
 
    return STLData(
        name=name,
        is_binary=False,
        triangle_count=len(normals),
        normals=normals,
        vertices=vertices,
    )
 
 
def _compute_stats(mesh: STLData) -> dict:
    if mesh.triangle_count == 0:
        return {
            "bbox_min": None,
            "bbox_max": None,
            "surface_area": 0.0,
            "signed_volume": 0.0,
        }
 
    xs = [v[0] for v in mesh.vertices]
    ys = [v[1] for v in mesh.vertices]
    zs = [v[2] for v in mesh.vertices]
    bbox_min = (min(xs), min(ys), min(zs))
    bbox_max = (max(xs), max(ys), max(zs))
 
    surface_area = 0.0
    signed_volume = 0.0
 
    for i in range(mesh.triangle_count):
        v0 = mesh.vertices[i * 3]
        v1 = mesh.vertices[i * 3 + 1]
        v2 = mesh.vertices[i * 3 + 2]
 
        # 면적: 두 변의 외적 크기 / 2
        ux, uy, uz = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
        vx, vy, vz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
        cx = uy * vz - uz * vy
        cy = uz * vx - ux * vz
        cz = ux * vy - uy * vx
        surface_area += 0.5 * (cx ** 2 + cy ** 2 + cz ** 2) ** 0.5
 
        # 부피: signed tetrahedron volume 합 (divergence theorem)
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