"""Assetto Corsa MOD generator.

Assetto Corsa stores its data in INI-style text files.

Track layout (under ``content/tracks/<track_id>/``):
  - ``ui/ui_track.json``   – display metadata shown in the launcher
  - ``data/surfaces.ini``  – surface grip / dust definitions
  - ``data/map.ini``       – timing / layout settings

Car layout (under ``content/cars/<car_id>/``):
  - ``ui/ui_car.json``     – display metadata shown in the launcher
  - ``data/car.ini``       – mass and basic geometry
  - ``data/engine.ini``    – engine power curve summary
  - ``data/tyres.ini``     – tyre compound definitions
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from race_mod_create.generators.base import BaseGenerator
from race_mod_create.models.car import Car
from race_mod_create.models.track import Track

# 1 kW = ~1.341 brake horsepower (BHP) (used for Assetto Corsa ui_car.json display)
KW_TO_BHP = 1.341

# Friction coefficients per surface type for Assetto Corsa surfaces.ini
_SURFACE_FRICTION: dict[str, float] = {
    "ASPHALT": 0.96,
    "CONCRETE": 0.94,
    "GRAVEL": 0.65,
    "DIRT": 0.60,
    "GRASS": 0.55,
}


def _to_id(name: str) -> str:
    """Convert a display name to a lowercase ASCII identifier."""
    return re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_")


class AssettoCorsaGenerator(BaseGenerator):
    """Generates Assetto Corsa–compatible MOD files."""

    simulator_name = "Assetto Corsa"

    # ------------------------------------------------------------------
    # Track
    # ------------------------------------------------------------------

    def generate_track(self, track: Track) -> Path:
        """Generate Assetto Corsa track mod files for *track*.

        Returns the root mod directory (``content/tracks/<id>``).
        """
        track_id = _to_id(track.name)
        root = self.output_dir / "content" / "tracks" / track_id
        self._ensure_dir(root)

        self._write_track_ui(root, track)
        self._write_surfaces_ini(root, track)
        self._write_map_ini(root, track)

        return root

    def _write_track_ui(self, root: Path, track: Track) -> None:
        data = {
            "name": track.name,
            "description": track.description,
            "tags": [track.surface.value, "circuit"],
            "geotags": [track.location],
            "country": track.location,
            "city": track.location,
            "length": f"{track.length_m:.0f}",
            "pitboxes": str(track.pit_boxes),
            "run": "circuit",
            "author": track.author,
            "version": track.version,
        }
        self._write_file(
            root / "ui" / "ui_track.json",
            json.dumps(data, ensure_ascii=False, indent=2),
        )

    def _write_surfaces_ini(self, root: Path, track: Track) -> None:
        surface = track.surface.value.upper()
        friction = _SURFACE_FRICTION.get(surface, 0.96)
        lines = [
            "[SURFACE_0]",
            f"KEY={surface}",
            f"FRICTION={friction}",
            "DAMPING=0.0",
            "WAV=",
            "WAV_PITCH=0",
            "FF_EFFECT=NULL",
            "DIRT_ADDITIVE=0",
            "IS_VALID_TRACK=1",
            "BLACK_FLAG_TIME=0",
            "SIN_HEIGHT=0",
            "SIN_LENGTH=0",
            "IS_PITLANE=0",
            "VIBRATION_GAIN=0",
            "VIBRATION_LENGTH=0",
        ]
        self._write_file(root / "data" / "surfaces.ini", "\n".join(lines) + "\n")

    def _write_map_ini(self, root: Path, track: Track) -> None:
        sector_lines = []
        cumulative = 0.0
        for i, sector in enumerate(track.sectors):
            cumulative += sector.length_m
            sector_lines.append(f"SECTOR_{i + 1}={cumulative / track.length_m:.6f}")

        sector_block = "\n".join(sector_lines) if sector_lines else "SECTOR_1=1.000000"

        content = (
            "[RACE]\n"
            f"TRACK_LENGTH={track.length_m:.0f}\n"
            f"PITLANE_BOXCOUNT={track.pit_boxes}\n"
            "\n"
            "[SECTORS]\n"
            f"{sector_block}\n"
        )
        self._write_file(root / "data" / "map.ini", content)

    # ------------------------------------------------------------------
    # Car
    # ------------------------------------------------------------------

    def generate_car(self, car: Car) -> Path:
        """Generate Assetto Corsa car mod files for *car*.

        Returns the root mod directory (``content/cars/<id>``).
        """
        car_id = _to_id(f"{car.manufacturer}_{car.name}")
        root = self.output_dir / "content" / "cars" / car_id
        self._ensure_dir(root)

        self._write_car_ui(root, car)
        self._write_car_ini(root, car)
        self._write_engine_ini(root, car)
        self._write_tyres_ini(root, car)

        return root

    def _write_car_ui(self, root: Path, car: Car) -> None:
        data = {
            "name": f"{car.manufacturer} {car.name}",
            "description": car.description,
            "tags": [car.car_class.value, str(car.year)],
            "class": car.car_class.value,
            "specs": {
                "bhp": f"{car.engine.max_power_kw * KW_TO_BHP:.0f}",
                "torque": f"{car.engine.max_torque_nm:.0f}Nm",
                "weight": f"{car.mass_kg:.0f}kg",
                "topspeed": "",
                "acceleration": "",
                "pwratio": f"{car.mass_kg / (car.engine.max_power_kw * KW_TO_BHP):.2f}",
            },
            "author": car.author,
            "version": car.version,
        }
        self._write_file(
            root / "ui" / "ui_car.json",
            json.dumps(data, ensure_ascii=False, indent=2),
        )

    def _write_car_ini(self, root: Path, car: Car) -> None:
        content = (
            "[BASIC]\n"
            f"MODEL={car.manufacturer} {car.name}\n"
            f"SCREEN_NAME={car.manufacturer} {car.name}\n"
            f"TOTALMASS={car.mass_kg:.0f}\n"
            "INERTIA=1500 1700 200\n"
            "FUEL=100\n"
        )
        self._write_file(root / "data" / "car.ini", content)

    def _write_engine_ini(self, root: Path, car: Car) -> None:
        eng = car.engine
        content = (
            "[ENGINE_DATA]\n"
            f"LIMITER={eng.max_rpm}\n"
            "MINIMUM=900\n"
            "FUEL_CONSUMPTION=2.65\n"
            "\n"
            "[HEADER]\n"
            f"DISPLACEMENT={eng.displacement_cc:.0f}\n"
            f"CYLINDERS={eng.cylinders}\n"
            f"NATURALLY_ASPIRATED={'1' if eng.naturally_aspirated else '0'}\n"
            f"MAX_POWER_KW={eng.max_power_kw:.1f}\n"
            f"MAX_TORQUE_NM={eng.max_torque_nm:.1f}\n"
        )
        self._write_file(root / "data" / "engine.ini", content)

    def _write_tyres_ini(self, root: Path, car: Car) -> None:
        if not car.tyres:
            self._write_file(root / "data" / "tyres.ini", "")
            return

        blocks = []
        for i, tyre in enumerate(car.tyres):
            block = (
                f"[COMPOUND_{i}]\n"
                f"NAME={tyre.compound}\n"
                f"WIDTH={tyre.width_mm}\n"
                f"ASPECT_RATIO={tyre.aspect_ratio}\n"
                f"RIM={tyre.rim_diameter_inch}\n"
            )
            blocks.append(block)

        self._write_file(root / "data" / "tyres.ini", "\n".join(blocks))
