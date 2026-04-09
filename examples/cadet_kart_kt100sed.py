#!/usr/bin/env python3
"""Generate a realistic Cadet Kart MOD with Yamaha KT100SED engine and Dunlop SL tyres.

This script creates both Assetto Corsa and rFactor MOD files for a Kids Kart
Cadet-class machine.  All specifications are sourced from real-world data:

Vehicle:
    - Kids Kart Cadet class chassis (CIK-FIA style)
    - Wheelbase: 950 mm
    - Front track: 590 mm, Rear track: 555 mm
    - Minimum total weight (kart + driver): 107 kg
    - Fuel capacity: 5 L (premix)
    - 28 mm chromoly steel tube frame, 30 mm rear axle

Engine – Yamaha KT100SED:
    - 97.6 cc single-cylinder, air-cooled, 2-stroke
    - Bore × Stroke: 52 × 46 mm
    - Max power: ≈ 11.2 kW (15 HP) @ 10 000 RPM
    - Max torque: ≈ 10.0 Nm
    - Rev limit: 14 000 RPM
    - Carburetor: Walbro WB-3A, CDI ignition
    - Naturally aspirated

Tyres – Dunlop SL (Slick, Cadet spec):
    - Front: 10 × 3.60-5  → width 91 mm, aspect ratio 69 %, rim 5″
    - Rear:  11 × 5.00-5  → width 127 mm, aspect ratio 60 %, rim 5″

Usage::

    python examples/cadet_kart_kt100sed.py [OUTPUT_DIR]

Default output is ``./mods``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running directly from the repo root without installing the package.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from race_mod_create import (  # noqa: E402
    AssettoCorsaGenerator,
    Car,
    CarClass,
    EngineSpec,
    RFactorGenerator,
    TyreSpec,
)

# ---------------------------------------------------------------------------
# Engine – Yamaha KT100SED
# ---------------------------------------------------------------------------

engine = EngineSpec(
    displacement_cc=97.6,       # 52 mm bore × 46 mm stroke
    cylinders=1,                # single-cylinder 2-stroke
    max_power_kw=11.2,          # ≈ 15 HP @ 10 000 RPM
    max_torque_nm=10.0,         # measured at peak
    max_rpm=14000,              # rev limit
    naturally_aspirated=True,
)

# ---------------------------------------------------------------------------
# Tyres – Dunlop SL (Cadet slick)
# ---------------------------------------------------------------------------

front_tyre = TyreSpec(
    compound="Dunlop SL Front",
    width_mm=91,                # 3.60 inches
    aspect_ratio=69,            # sidewall height 2.5″ / width 3.60″
    rim_diameter_inch=5,
)

rear_tyre = TyreSpec(
    compound="Dunlop SL Rear",
    width_mm=127,               # 5.00 inches
    aspect_ratio=60,            # sidewall height 3.0″ / width 5.00″
    rim_diameter_inch=5,
)

# ---------------------------------------------------------------------------
# Car – Cadet Kart
# ---------------------------------------------------------------------------

cadet_kart = Car(
    name="Cadet KT100SED",
    manufacturer="Kids Kart",
    car_class=CarClass.KART,
    year=2024,
    engine=engine,
    mass_kg=107.0,              # minimum total weight (kart + driver)
    tyres=[front_tyre, rear_tyre],
    wheelbase_mm=950.0,         # CIK-FIA Cadet standard
    front_track_mm=590.0,
    rear_track_mm=555.0,
    fuel_capacity_l=5.0,        # small premix tank
    description=(
        "Kids Kart Cadet class with Yamaha KT100SED engine (97.6 cc, 15 HP) "
        "and Dunlop SL slick tyres. Realistic specifications for precise "
        "racing simulation."
    ),
    author="RaceModCreate",
    version="1.0",
)


def main(output_dir: str = "./mods") -> None:
    """Generate the Cadet Kart MOD for both simulators."""
    # Assetto Corsa
    ac_gen = AssettoCorsaGenerator(output_dir=output_dir)
    ac_path = ac_gen.generate_car(cadet_kart)
    print(f"[Assetto Corsa] Cadet Kart MOD generated: {ac_path}")

    # rFactor
    rf_gen = RFactorGenerator(output_dir=output_dir)
    rf_path = rf_gen.generate_car(cadet_kart)
    print(f"[rFactor]       Cadet Kart MOD generated: {rf_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "./mods"
    main(out)
