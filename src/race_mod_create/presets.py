"""Predefined circuit (track) presets for common racing series.

The JKT Kanto (Junior Karting Trophy) series circuits are sourced from
https://jkt-kanto.jp/ and represent the 2026 season venues.
"""

from __future__ import annotations

import copy

from race_mod_create.models.track import SurfaceType, Track

# ---------------------------------------------------------------------------
# JKT Kanto (Junior Karting Trophy) – 2026 season circuits
# Reference: https://jkt-kanto.jp/
# ---------------------------------------------------------------------------

JKT_KANTO_CIRCUITS: dict[str, Track] = {
    "haruna": Track(
        name="榛名モータースポーツランド",
        location="Gunma, Japan",
        length_m=900.0,
        pit_boxes=10,
        surface=SurfaceType.ASPHALT,
        description="JKT関東シリーズ開催サーキット。高低差のあるテクニカルなカートコース。",
    ),
    "festika_tochigi": Track(
        name="フェスティカサーキット栃木",
        location="Tochigi, Japan",
        length_m=628.0,
        pit_boxes=10,
        surface=SurfaceType.ASPHALT,
        description="JKT関東シリーズ開催サーキット。初心者から上級者まで楽しめるカートコース。",
    ),
    "quick_itako": Track(
        name="クイック潮来",
        location="Ibaraki, Japan",
        length_m=700.0,
        pit_boxes=10,
        surface=SurfaceType.ASPHALT,
        description="JKT関東シリーズ開催サーキット。関東最大級のカートコース。",
    ),
    "mobara_twin": Track(
        name="茂原ツインサーキット",
        location="Chiba, Japan",
        length_m=700.0,
        pit_boxes=10,
        surface=SurfaceType.ASPHALT,
        description="JKT関東シリーズ開催サーキット（西コース）。テクニカルなレイアウト。",
    ),
    "akigase": Track(
        name="サーキット秋ヶ瀬",
        location="Saitama, Japan",
        length_m=608.0,
        pit_boxes=10,
        surface=SurfaceType.ASPHALT,
        description="JKT関東シリーズ開催サーキット。都心から最も近いサーキット。",
    ),
}

# ---------------------------------------------------------------------------
# JKT KIDS (Kids Challenge) only – circuits that host exclusively
# the Kids Challenge class in the JKT Kanto series.
# Reference: https://jkt-kanto.jp/
# ---------------------------------------------------------------------------

JKT_KIDS_CIRCUITS: dict[str, Track] = {
    "nakai_inter": Track(
        name="中井インターサーキット",
        location="Kanagawa, Japan",
        length_m=400.0,
        pit_boxes=5,
        surface=SurfaceType.ASPHALT,
        description="JKT KIDSチャレンジ専用開催サーキット。高低差のあるキッズ向けカートコース。",
    ),
    "reon": Track(
        name="レオンサーキット",
        location="Ibaraki, Japan",
        length_m=330.0,
        pit_boxes=5,
        surface=SurfaceType.ASPHALT,
        description="JKT KIDSチャレンジ専用開催サーキット。キッズカートに特化した本格サーキット。",
    ),
}

# All JKT-related presets combined for easy lookup.
_ALL_PRESETS: dict[str, Track] = {**JKT_KANTO_CIRCUITS, **JKT_KIDS_CIRCUITS}


def get_preset(name: str) -> Track:
    """Return a *copy* of the preset track identified by *name*.

    Raises :class:`KeyError` when *name* is not a known preset.
    """
    if name not in _ALL_PRESETS:
        available = ", ".join(sorted(_ALL_PRESETS))
        raise KeyError(
            f"Unknown preset '{name}'. Available presets: {available}"
        )
    return copy.deepcopy(_ALL_PRESETS[name])


def list_presets() -> list[str]:
    """Return sorted list of available preset names."""
    return sorted(_ALL_PRESETS)
