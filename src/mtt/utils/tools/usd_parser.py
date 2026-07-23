from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# ASCII USD(.usd/.usda)의 `def Type "Name" { ... }` prim 선언을 매칭
_DEF_RE = re.compile(r'\bdef\s+(\w+)\s+"([^"]+)"')


@dataclass
class USDPrim:
    name: str
    type_name: str


@dataclass
class USDData:
    prims: list[USDPrim] = field(default_factory=list)


def _is_usdz(input_path: str | Path) -> bool:
    return str(input_path).lower().endswith(".usdz")


def _list_usdz_members(input_path: str | Path) -> list[str]:
    '''USDZ는 USD + texture/material 등을 담은 zip 패키지라 내부 파일 목록만으로도 구조를 알 수 있다.'''
    with zipfile.ZipFile(input_path) as archive:
        return archive.namelist()


def _parse_usd_with_pxr(input_path: str | Path) -> USDData:
    '''Pixar USD SDK(pxr)로 stage를 열어 전체 prim 계층을 순회한다. 미설치 시 ImportError.'''
    from pxr import Usd

    stage = Usd.Stage.Open(str(input_path))
    if stage is None:
        raise ValueError(f"USD stage를 열 수 없습니다: {input_path}")

    prims = [USDPrim(name=str(prim.GetPath()), type_name=prim.GetTypeName()) for prim in stage.Traverse()]
    return USDData(prims=prims)


def _parse_usd_text(text: str) -> USDData:
    '''pxr 없이 ASCII USD 텍스트에서 `def Type "Name"` 선언만 정규식으로 추출한다.'''
    prims = [USDPrim(name=name, type_name=type_name) for type_name, name in _DEF_RE.findall(text)]
    return USDData(prims=prims)
