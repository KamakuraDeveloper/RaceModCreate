"""Tests for the Cadet Kart (KT100SED) MOD generation."""

import json

import pytest

from race_mod_create.generators.assetto_corsa import AssettoCorsaGenerator
from race_mod_create.generators.rfactor import RFactorGenerator
from race_mod_create.models.car import Car, CarClass, EngineSpec, TyreSpec


# ---------------------------------------------------------------------------
# Fixture – Cadet Kart
# ---------------------------------------------------------------------------

@pytest.fixture
def cadet_kart():
    engine = EngineSpec(
        displacement_cc=97.6,
        cylinders=1,
        max_power_kw=11.2,
        max_torque_nm=10.0,
        max_rpm=14000,
        naturally_aspirated=True,
    )
    return Car(
        name="Cadet KT100SED",
        manufacturer="Kids Kart",
        car_class=CarClass.KART,
        year=2024,
        engine=engine,
        mass_kg=107.0,
        tyres=[
            TyreSpec("Dunlop SL Front", 91, 69, 5),
            TyreSpec("Dunlop SL Rear", 127, 60, 5),
        ],
        wheelbase_mm=950.0,
        front_track_mm=590.0,
        rear_track_mm=555.0,
        fuel_capacity_l=5.0,
        description="Cadet kart with Yamaha KT100SED engine and Dunlop SL tyres.",
        author="RaceModCreate",
        version="1.0",
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestKartModel:
    def test_kart_class_exists(self):
        assert CarClass.KART.value == "Kart"

    def test_kart_class_from_string(self):
        car = Car(
            name="Test",
            manufacturer="Test",
            car_class="Kart",
            year=2024,
            engine=EngineSpec(97.6, 1, 11.2, 10.0, 14000),
            mass_kg=107.0,
        )
        assert car.car_class == CarClass.KART

    def test_chassis_dimensions(self, cadet_kart):
        assert cadet_kart.wheelbase_mm == 950.0
        assert cadet_kart.front_track_mm == 590.0
        assert cadet_kart.rear_track_mm == 555.0
        assert cadet_kart.fuel_capacity_l == 5.0

    def test_chassis_defaults_to_zero(self):
        engine = EngineSpec(2000, 4, 200.0, 300.0, 7000)
        car = Car("X", "Y", CarClass.GT3, 2024, engine, 1300.0)
        assert car.wheelbase_mm == 0.0
        assert car.front_track_mm == 0.0
        assert car.rear_track_mm == 0.0
        assert car.fuel_capacity_l == 0.0


# ---------------------------------------------------------------------------
# Assetto Corsa – Kart
# ---------------------------------------------------------------------------

class TestAssettoCorsaKart:
    def test_generates_all_files(self, tmp_path, cadet_kart):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        assert (root / "ui" / "ui_car.json").exists()
        assert (root / "data" / "car.ini").exists()
        assert (root / "data" / "engine.ini").exists()
        assert (root / "data" / "tyres.ini").exists()

    def test_ui_json_has_kart_class(self, tmp_path, cadet_kart):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        data = json.loads((root / "ui" / "ui_car.json").read_text())
        assert data["class"] == "Kart"
        assert "Kids Kart" in data["name"]
        assert "Cadet KT100SED" in data["name"]

    def test_car_ini_uses_fuel_capacity(self, tmp_path, cadet_kart):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        content = (root / "data" / "car.ini").read_text()
        assert "TOTALMASS=107" in content
        assert "FUEL=5" in content

    def test_car_ini_inertia_scales_with_mass(self, tmp_path, cadet_kart):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        content = (root / "data" / "car.ini").read_text()
        # 107 kg kart should have much smaller inertia than 1300 kg car
        assert "INERTIA=" in content
        # Inertia values should all be < 200 for a 107 kg kart
        for line in content.splitlines():
            if line.startswith("INERTIA="):
                values = [float(v) for v in line.split("=")[1].split()]
                assert all(v < 200 for v in values)

    def test_engine_ini_kt100sed(self, tmp_path, cadet_kart):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        content = (root / "data" / "engine.ini").read_text()
        assert "LIMITER=14000" in content
        assert "DISPLACEMENT=98" in content
        assert "CYLINDERS=1" in content
        assert "NATURALLY_ASPIRATED=1" in content

    def test_tyres_ini_has_dunlop_sl(self, tmp_path, cadet_kart):
        gen = AssettoCorsaGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        content = (root / "data" / "tyres.ini").read_text()
        assert "Dunlop SL Front" in content
        assert "Dunlop SL Rear" in content
        assert "WIDTH=91" in content
        assert "WIDTH=127" in content
        assert "RIM=5" in content


# ---------------------------------------------------------------------------
# rFactor – Kart
# ---------------------------------------------------------------------------

class TestRFactorKart:
    def test_generates_all_files(self, tmp_path, cadet_kart):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        assert len(list(root.glob("*.veh"))) == 1
        assert len(list(root.glob("*.hdv"))) == 1
        assert len(list(root.glob("*_engine.ini"))) == 1

    def test_veh_has_kart_class(self, tmp_path, cadet_kart):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        content = list(root.glob("*.veh"))[0].read_text()
        assert "Type = Kart" in content
        assert "Manufacturer = Kids Kart" in content

    def test_hdv_uses_chassis_dimensions(self, tmp_path, cadet_kart):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        content = list(root.glob("*.hdv"))[0].read_text()
        assert "Mass = 107.0" in content
        # Wheelbase 950 mm → 0.475 m each half
        assert "FrontWheelbase = 0.475" in content
        assert "RearWheelbase  = 0.475" in content
        # Front track 590 mm → 0.590 m
        assert "FrontTrackWidth = 0.590" in content
        # Rear track 555 mm → 0.555 m
        assert "RearTrackWidth  = 0.555" in content

    def test_engine_ini_kt100sed(self, tmp_path, cadet_kart):
        gen = RFactorGenerator(output_dir=tmp_path)
        root = gen.generate_car(cadet_kart)
        content = list(root.glob("*_engine.ini"))[0].read_text()
        assert "Displacement = 98" in content
        assert "Cylinders = 1" in content
        assert "RevLimitRPM = 14000" in content
        assert "NaturallyAspirated = 1" in content
