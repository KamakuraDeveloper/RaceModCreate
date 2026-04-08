"""Tests for Track and Car data models."""

import pytest

from race_mod_create.models.car import Car, CarClass, EngineSpec, TyreSpec
from race_mod_create.models.track import Track, Sector, SurfaceType


# ---------------------------------------------------------------------------
# Track model tests
# ---------------------------------------------------------------------------

class TestTrack:
    def _make_track(self, **kwargs):
        defaults = dict(
            name="Test Circuit",
            location="Tokyo, Japan",
            length_m=4000.0,
            pit_boxes=20,
            surface=SurfaceType.ASPHALT,
        )
        defaults.update(kwargs)
        return Track(**defaults)

    def test_basic_creation(self):
        track = self._make_track()
        assert track.name == "Test Circuit"
        assert track.location == "Tokyo, Japan"
        assert track.length_m == 4000.0
        assert track.pit_boxes == 20
        assert track.surface == SurfaceType.ASPHALT

    def test_surface_from_string(self):
        track = self._make_track(surface="concrete")
        assert track.surface == SurfaceType.CONCRETE

    def test_sectors_default_empty(self):
        track = self._make_track()
        assert track.sectors == []

    def test_sectors_assigned(self):
        sectors = [Sector("S1", 1500.0), Sector("S2", 2500.0)]
        track = self._make_track(sectors=sectors)
        assert len(track.sectors) == 2
        assert track.sectors[0].name == "S1"

    def test_invalid_length_raises(self):
        with pytest.raises(ValueError, match="length_m"):
            self._make_track(length_m=0)

    def test_invalid_negative_length_raises(self):
        with pytest.raises(ValueError, match="length_m"):
            self._make_track(length_m=-100)

    def test_invalid_pit_boxes_raises(self):
        with pytest.raises(ValueError, match="pit_boxes"):
            self._make_track(pit_boxes=-1)

    def test_default_author_and_version(self):
        track = self._make_track()
        assert track.author == "Unknown"
        assert track.version == "1.0"


# ---------------------------------------------------------------------------
# Sector model tests
# ---------------------------------------------------------------------------

class TestSector:
    def test_sector_creation(self):
        s = Sector("Sector 1", 1200.5)
        assert s.name == "Sector 1"
        assert s.length_m == 1200.5


# ---------------------------------------------------------------------------
# EngineSpec model tests
# ---------------------------------------------------------------------------

class TestEngineSpec:
    def _make_engine(self, **kwargs):
        defaults = dict(
            displacement_cc=2000.0,
            cylinders=4,
            max_power_kw=200.0,
            max_torque_nm=300.0,
            max_rpm=7000,
        )
        defaults.update(kwargs)
        return EngineSpec(**defaults)

    def test_basic_creation(self):
        eng = self._make_engine()
        assert eng.displacement_cc == 2000.0
        assert eng.cylinders == 4
        assert eng.naturally_aspirated is True

    def test_forced_induction(self):
        eng = self._make_engine(naturally_aspirated=False)
        assert eng.naturally_aspirated is False

    def test_invalid_displacement_raises(self):
        with pytest.raises(ValueError, match="displacement_cc"):
            self._make_engine(displacement_cc=0)

    def test_invalid_cylinders_raises(self):
        with pytest.raises(ValueError, match="cylinders"):
            self._make_engine(cylinders=0)

    def test_invalid_power_raises(self):
        with pytest.raises(ValueError, match="max_power_kw"):
            self._make_engine(max_power_kw=-1)

    def test_invalid_torque_raises(self):
        with pytest.raises(ValueError, match="max_torque_nm"):
            self._make_engine(max_torque_nm=0)

    def test_invalid_rpm_raises(self):
        with pytest.raises(ValueError, match="max_rpm"):
            self._make_engine(max_rpm=0)


# ---------------------------------------------------------------------------
# TyreSpec model tests
# ---------------------------------------------------------------------------

class TestTyreSpec:
    def test_basic_creation(self):
        t = TyreSpec("Soft", 305, 30, 18)
        assert t.compound == "Soft"
        assert t.width_mm == 305
        assert t.aspect_ratio == 30
        assert t.rim_diameter_inch == 18

    def test_invalid_width_raises(self):
        with pytest.raises(ValueError, match="width_mm"):
            TyreSpec("Soft", 0, 30, 18)

    def test_invalid_aspect_ratio_raises(self):
        with pytest.raises(ValueError, match="aspect_ratio"):
            TyreSpec("Soft", 305, 0, 18)

    def test_aspect_ratio_over_100_raises(self):
        with pytest.raises(ValueError, match="aspect_ratio"):
            TyreSpec("Soft", 305, 101, 18)

    def test_invalid_rim_raises(self):
        with pytest.raises(ValueError, match="rim_diameter_inch"):
            TyreSpec("Soft", 305, 30, 0)


# ---------------------------------------------------------------------------
# Car model tests
# ---------------------------------------------------------------------------

class TestCar:
    def _make_engine(self):
        return EngineSpec(3982, 6, 368.0, 450.0, 7500)

    def _make_car(self, **kwargs):
        defaults = dict(
            name="GT3 Racer",
            manufacturer="SpeedCraft",
            car_class=CarClass.GT3,
            year=2024,
            engine=self._make_engine(),
            mass_kg=1300.0,
        )
        defaults.update(kwargs)
        return Car(**defaults)

    def test_basic_creation(self):
        car = self._make_car()
        assert car.name == "GT3 Racer"
        assert car.manufacturer == "SpeedCraft"
        assert car.car_class == CarClass.GT3
        assert car.mass_kg == 1300.0

    def test_car_class_from_string(self):
        car = self._make_car(car_class="LMP1")
        assert car.car_class == CarClass.LMP1

    def test_invalid_mass_raises(self):
        with pytest.raises(ValueError, match="mass_kg"):
            self._make_car(mass_kg=0)

    def test_tyres_default_empty(self):
        car = self._make_car()
        assert car.tyres == []

    def test_tyres_assigned(self):
        tyres = [TyreSpec("Soft", 305, 30, 18), TyreSpec("Hard", 305, 30, 18)]
        car = self._make_car(tyres=tyres)
        assert len(car.tyres) == 2

    def test_default_author_and_version(self):
        car = self._make_car()
        assert car.author == "Unknown"
        assert car.version == "1.0"
