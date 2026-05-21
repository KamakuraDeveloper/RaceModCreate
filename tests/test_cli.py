"""Tests for the CLI entry point."""

import pytest

from race_mod_create.cli import main


class TestCLITrack:
    def test_assetto_corsa_track(self, tmp_path):
        exit_code = main([
            "track",
            "--simulator", "assetto_corsa",
            "--name", "Fuji Speedway",
            "--location", "Oyama, Japan",
            "--length", "4563",
            "--pit-boxes", "28",
            "--output", str(tmp_path),
        ])
        assert exit_code == 0
        # Check a key output file exists
        track_dir = tmp_path / "content" / "tracks" / "fuji_speedway"
        assert (track_dir / "ui" / "ui_track.json").exists()

    def test_rfactor_track(self, tmp_path):
        exit_code = main([
            "track",
            "--simulator", "rfactor",
            "--name", "Fuji Speedway",
            "--location", "Oyama, Japan",
            "--length", "4563",
            "--output", str(tmp_path),
        ])
        assert exit_code == 0
        track_dir = tmp_path / "GameData" / "Locations" / "FujiSpeedway"
        gdb_files = list(track_dir.glob("*.gdb"))
        assert len(gdb_files) == 1

    def test_surface_option(self, tmp_path):
        exit_code = main([
            "track",
            "--simulator", "assetto_corsa",
            "--name", "Dirt Track",
            "--location", "Somewhere",
            "--length", "2000",
            "--surface", "dirt",
            "--output", str(tmp_path),
        ])
        assert exit_code == 0


class TestCLICar:
    def _base_car_args(self, tmp_path):
        return [
            "car",
            "--simulator", "assetto_corsa",
            "--name", "Racer X",
            "--manufacturer", "TestCo",
            "--class", "GT3",
            "--year", "2024",
            "--displacement", "3982",
            "--cylinders", "6",
            "--max-power-kw", "368",
            "--max-torque-nm", "450",
            "--max-rpm", "7500",
            "--mass-kg", "1300",
            "--output", str(tmp_path),
        ]

    def test_assetto_corsa_car(self, tmp_path):
        exit_code = main(self._base_car_args(tmp_path))
        assert exit_code == 0
        car_dir = tmp_path / "content" / "cars" / "testco_racer_x"
        assert (car_dir / "ui" / "ui_car.json").exists()

    def test_rfactor_car(self, tmp_path):
        args = self._base_car_args(tmp_path)
        args[2] = "rfactor"  # change simulator
        exit_code = main(args)
        assert exit_code == 0
        car_dir = tmp_path / "GameData" / "Vehicles" / "TestcoRacerX"
        veh_files = list(car_dir.glob("*.veh"))
        assert len(veh_files) == 1

    def test_turbo_flag(self, tmp_path):
        args = self._base_car_args(tmp_path) + ["--turbo"]
        exit_code = main(args)
        assert exit_code == 0
        car_dir = tmp_path / "content" / "cars" / "testco_racer_x"
        engine_ini = (car_dir / "data" / "engine.ini").read_text()
        assert "NATURALLY_ASPIRATED=0" in engine_ini

    def test_invalid_mass_shows_error(self, tmp_path):
        args = self._base_car_args(tmp_path)
        # Replace --mass-kg 1300 with 0 (invalid)
        idx = args.index("--mass-kg") + 1
        args[idx] = "0"
        with pytest.raises(SystemExit):
            main(args)
