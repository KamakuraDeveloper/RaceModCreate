"""Tests for JKT Kanto circuit presets."""

import pytest

from race_mod_create.presets import (
    JKT_KANTO_CIRCUITS,
    JKT_KIDS_CIRCUITS,
    get_preset,
    list_presets,
)
from race_mod_create.models.track import Track, SurfaceType


# ---------------------------------------------------------------------------
# JKT Kanto series circuits
# ---------------------------------------------------------------------------

class TestJKTKantoCircuits:
    def test_all_five_circuits_present(self):
        assert len(JKT_KANTO_CIRCUITS) == 5

    def test_expected_keys(self):
        expected = {"haruna", "festika_tochigi", "quick_itako", "mobara_twin", "akigase"}
        assert set(JKT_KANTO_CIRCUITS) == expected

    def test_each_circuit_is_a_track(self):
        for name, track in JKT_KANTO_CIRCUITS.items():
            assert isinstance(track, Track), f"{name} is not a Track instance"

    def test_haruna_details(self):
        t = JKT_KANTO_CIRCUITS["haruna"]
        assert t.name == "榛名モータースポーツランド"
        assert t.location == "Gunma, Japan"
        assert t.length_m == 900.0
        assert t.surface == SurfaceType.ASPHALT

    def test_festika_tochigi_details(self):
        t = JKT_KANTO_CIRCUITS["festika_tochigi"]
        assert t.name == "フェスティカサーキット栃木"
        assert t.location == "Tochigi, Japan"
        assert t.length_m == 628.0

    def test_quick_itako_details(self):
        t = JKT_KANTO_CIRCUITS["quick_itako"]
        assert t.name == "クイック潮来"
        assert t.location == "Ibaraki, Japan"
        assert t.length_m == 700.0

    def test_mobara_twin_details(self):
        t = JKT_KANTO_CIRCUITS["mobara_twin"]
        assert t.name == "茂原ツインサーキット"
        assert t.location == "Chiba, Japan"
        assert t.length_m == 700.0

    def test_akigase_details(self):
        t = JKT_KANTO_CIRCUITS["akigase"]
        assert t.name == "サーキット秋ヶ瀬"
        assert t.location == "Saitama, Japan"
        assert t.length_m == 608.0


# ---------------------------------------------------------------------------
# JKT KIDS (Kids Challenge) only circuits
# ---------------------------------------------------------------------------

class TestJKTKidsCircuits:
    def test_two_kids_circuits_present(self):
        assert len(JKT_KIDS_CIRCUITS) == 2

    def test_expected_keys(self):
        expected = {"nakai_inter", "reon"}
        assert set(JKT_KIDS_CIRCUITS) == expected

    def test_each_circuit_is_a_track(self):
        for name, track in JKT_KIDS_CIRCUITS.items():
            assert isinstance(track, Track), f"{name} is not a Track instance"

    def test_nakai_inter_details(self):
        t = JKT_KIDS_CIRCUITS["nakai_inter"]
        assert t.name == "中井インターサーキット"
        assert t.location == "Kanagawa, Japan"
        assert t.length_m == 400.0
        assert t.surface == SurfaceType.ASPHALT

    def test_reon_details(self):
        t = JKT_KIDS_CIRCUITS["reon"]
        assert t.name == "レオンサーキット"
        assert t.location == "Ibaraki, Japan"
        assert t.length_m == 330.0
        assert t.surface == SurfaceType.ASPHALT

    def test_no_overlap_with_kanto_circuits(self):
        assert set(JKT_KIDS_CIRCUITS).isdisjoint(set(JKT_KANTO_CIRCUITS))


# ---------------------------------------------------------------------------
# get_preset / list_presets helpers
# ---------------------------------------------------------------------------

class TestGetPreset:
    def test_returns_correct_track(self):
        track = get_preset("haruna")
        assert track.name == "榛名モータースポーツランド"

    def test_returns_kids_track(self):
        track = get_preset("nakai_inter")
        assert track.name == "中井インターサーキット"

    def test_returns_deep_copy(self):
        t1 = get_preset("haruna")
        t2 = get_preset("haruna")
        assert t1 is not t2
        t1.name = "modified"
        assert JKT_KANTO_CIRCUITS["haruna"].name != "modified"

    def test_unknown_preset_raises_key_error(self):
        with pytest.raises(KeyError, match="Unknown preset"):
            get_preset("nonexistent")


class TestListPresets:
    def test_returns_sorted_list(self):
        names = list_presets()
        assert names == sorted(names)
        assert len(names) == 7

    def test_includes_kanto_and_kids(self):
        names = list_presets()
        assert "haruna" in names
        assert "nakai_inter" in names
        assert "reon" in names

    def test_all_names_retrievable(self):
        for name in list_presets():
            track = get_preset(name)
            assert isinstance(track, Track)
