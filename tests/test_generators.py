"""Tests for Assetto Corsa and rFactor MOD generators."""

import json
import re
from pathlib import Path

import pytest

from race_mod_create.generators.assetto_corsa import AssettoCorsaGenerator
from race_mod_create.generators.rfactor import RFactorGenerator
from race_mod_create.models.car import Car, CarClass, EngineSpec, TyreSpec
from race_mod_create.models.track import Track, Sector, SurfaceType


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_track():
    return Track(
        name="Suzuka Circuit",
        location="Suzuka, Japan",
        length_m=5807.0,
        pit_boxes=32,
        surface=SurfaceType.ASPHALT,
        sectors=[Sector("S1", 1800.0), Sector("S2", 2500.0), Sector("S3", 1507.0)],
        description="The legendary figure-8 circuit.",
        author="TestAuthor",
        version="2.0",
    )


@pytest.fixture
def sample_car():
    engine = EngineSpec(
        displacement_cc=3982.0,
        cylinders=6,
        max_power_kw=368.0,
        max_torque_nm=450.0,
        max_rpm=7500,
        naturally_aspirated=True,
    )
    return Car(
        name="GT3 Racer",
        manufacturer="SpeedCraft",
        car_class=CarClass.GT3,
        year=2024,
        engine=engine,
        mass_kg=1300.0,
        tyres=[
            TyreSpec("Soft", 305, 30, 18),
            TyreSpec("Medium", 305, 30, 18),
            TyreSpec("Hard", 305, 30, 18),
        ],
        description="A competitive GT3 car.",
        author="TestAuthor",
        version="1.5",
    )


# ---------------------------------------------------------------------------
# Assetto Corsa – Track
# ---------------------------------------------------------------------------

class TestAssettoCorsaTrack:
    def test_returns_path_under_output_dir(self, tmp_path, sample_track):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        result = gen.generate_track(sample_track)
        assert result.is_dir()
        assert str(tmp_path) in str(result)

    def test_creates_ui_json(self, tmp_path, sample_track):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_track(sample_track)
        ui_file = root / "ui" / "ui_track.json"
        assert ui_file.exists()
        data = json.loads(ui_file.read_text())
        assert data["name"] == sample_track.name
        assert data["author"] == sample_track.author
        assert data["version"] == sample_track.version
        assert data["pitboxes"] == str(sample_track.pit_boxes)

    def test_creates_surfaces_ini(self, tmp_path, sample_track):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_track(sample_track)
        surfaces = root / "data" / "surfaces.ini"
        assert surfaces.exists()
        content = surfaces.read_text()
        assert "ASPHALT" in content
        assert "IS_VALID_TRACK=1" in content

    def test_creates_map_ini(self, tmp_path, sample_track):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_track(sample_track)
        map_ini = root / "data" / "map.ini"
        assert map_ini.exists()
        content = map_ini.read_text()
        assert f"TRACK_LENGTH={int(sample_track.length_m)}" in content
        # Three sectors should produce three sector lines
        assert "SECTOR_1=" in content
        assert "SECTOR_2=" in content
        assert "SECTOR_3=" in content

    def test_no_sectors_produces_default_sector(self, tmp_path):
        track = Track(name="Mini Track", location="Test", length_m=1000.0)
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_track(track)
        content = (root / "data" / "map.ini").read_text()
        assert "SECTOR_1=1.000000" in content

    def test_track_id_is_sanitised(self, tmp_path):
        track = Track(name="My Track (v2)!", location="X", length_m=1000.0)
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_track(track)
        assert re.match(r"^[a-z0-9_]+$", root.name)


# ---------------------------------------------------------------------------
# Assetto Corsa – Car
# ---------------------------------------------------------------------------

class TestAssettoCorsaCar:
    def test_returns_path_under_output_dir(self, tmp_path, sample_car):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        result = gen.generate_car(sample_car)
        assert result.is_dir()

    def test_creates_ui_json(self, tmp_path, sample_car):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(sample_car)
        ui_file = root / "ui" / "ui_car.json"
        assert ui_file.exists()
        data = json.loads(ui_file.read_text())
        assert sample_car.name in data["name"]
        assert sample_car.manufacturer in data["name"]
        assert data["class"] == sample_car.car_class.value

    def test_creates_car_ini(self, tmp_path, sample_car):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(sample_car)
        car_ini = root / "data" / "car.ini"
        assert car_ini.exists()
        content = car_ini.read_text()
        assert f"TOTALMASS={int(sample_car.mass_kg)}" in content

    def test_creates_engine_ini(self, tmp_path, sample_car):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(sample_car)
        engine_ini = root / "data" / "engine.ini"
        assert engine_ini.exists()
        content = engine_ini.read_text()
        assert f"LIMITER={sample_car.engine.max_rpm}" in content
        assert "NATURALLY_ASPIRATED=1" in content

    def test_creates_tyres_ini(self, tmp_path, sample_car):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(sample_car)
        tyres_ini = root / "data" / "tyres.ini"
        assert tyres_ini.exists()
        content = tyres_ini.read_text()
        assert "Soft" in content
        assert "Medium" in content
        assert "Hard" in content

    def test_empty_tyres_creates_empty_ini(self, tmp_path):
        engine = EngineSpec(2000, 4, 150.0, 250.0, 6500)
        car = Car("TestCar", "TestMaker", CarClass.TOURING, 2020, engine, 1100.0)
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(car)
        assert (root / "data" / "tyres.ini").read_text() == ""


# ---------------------------------------------------------------------------
# rFactor – Track
# ---------------------------------------------------------------------------

class TestRFactorTrack:
    def test_returns_path_under_output_dir(self, tmp_path, sample_track):
        gen = RFactorGenerator(output_dir=tmp_path)
        result = gen.generate_track(sample_track)
        assert result.is_dir()

    def test_creates_gdb_file(self, tmp_path, sample_track):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_track(sample_track)
        gdb_files = list(root.glob("*.gdb"))
        assert len(gdb_files) == 1
        content = gdb_files[0].read_text()
        assert sample_track.name in content
        assert sample_track.location in content
        assert sample_track.author in content

    def test_gdb_contains_sectors(self, tmp_path, sample_track):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_track(sample_track)
        gdb = list(root.glob("*.gdb"))[0].read_text()
        assert "Sector1End" in gdb
        assert "Sector2End" in gdb

    def test_creates_scn_file(self, tmp_path, sample_track):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_track(sample_track)
        scn_files = list(root.glob("*.scn"))
        assert len(scn_files) == 1

    def test_track_id_is_capitalised(self, tmp_path):
        track = Track(name="monaco grand prix", location="Monaco", length_m=3337.0)
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_track(track)
        # rFactor IDs use CamelCase
        assert root.name[0].isupper()


# ---------------------------------------------------------------------------
# rFactor – Car
# ---------------------------------------------------------------------------

class TestRFactorCar:
    def test_returns_path_under_output_dir(self, tmp_path, sample_car):
        gen = RFactorGenerator(output_dir=tmp_path)
        result = gen.generate_car(sample_car)
        assert result.is_dir()

    def test_creates_veh_file(self, tmp_path, sample_car):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_car(sample_car)
        veh_files = list(root.glob("*.veh"))
        assert len(veh_files) == 1
        content = veh_files[0].read_text()
        assert sample_car.manufacturer in content
        assert sample_car.name in content
        assert sample_car.car_class.value in content

    def test_creates_hdv_file(self, tmp_path, sample_car):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_car(sample_car)
        hdv_files = list(root.glob("*.hdv"))
        assert len(hdv_files) == 1
        content = hdv_files[0].read_text()
        assert f"Mass = {sample_car.mass_kg:.1f}" in content

    def test_creates_engine_ini(self, tmp_path, sample_car):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_car(sample_car)
        engine_files = list(root.glob("*_engine.ini"))
        assert len(engine_files) == 1
        content = engine_files[0].read_text()
        assert f"RevLimitRPM = {sample_car.engine.max_rpm}" in content
        assert "NaturallyAspirated = 1" in content

    def test_turbo_engine_flag(self, tmp_path):
        engine = EngineSpec(2000, 4, 300.0, 500.0, 6000, naturally_aspirated=False)
        car = Car("Turbo Car", "TestMaker", CarClass.GT3, 2023, engine, 1200.0)
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_car(car)
        engine_ini = list(root.glob("*_engine.ini"))[0].read_text()
        assert "NaturallyAspirated = 0" in engine_ini
