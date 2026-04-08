"""Command-line interface for RaceModCreate.

Usage examples::

    # Generate an Assetto Corsa track mod
    race-mod-create track --simulator assetto_corsa \\
        --name "Suzuka Circuit" --location "Suzuka, Japan" \\
        --length 5807 --pit-boxes 32 --output ./mods

    # Generate an rFactor car mod
    race-mod-create car --simulator rfactor \\
        --name "GT3 Racer" --manufacturer "SpeedCraft" \\
        --class GT3 --year 2024 \\
        --displacement 3982 --cylinders 6 \\
        --max-power-kw 368 --max-torque-nm 450 --max-rpm 7500 \\
        --mass-kg 1300 --output ./mods
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from race_mod_create.generators.assetto_corsa import AssettoCorsaGenerator
from race_mod_create.generators.rfactor import RFactorGenerator
from race_mod_create.models.car import Car, CarClass, EngineSpec, TyreSpec
from race_mod_create.models.track import Track, SurfaceType

_SIMULATORS = {
    "assetto_corsa": AssettoCorsaGenerator,
    "rfactor": RFactorGenerator,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="race-mod-create",
        description="Generate race simulator MOD files for tracks and cars.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------------ track
    tp = sub.add_parser("track", help="Generate a track (circuit) MOD.")
    tp.add_argument("--simulator", choices=list(_SIMULATORS), required=True,
                    help="Target race simulator.")
    tp.add_argument("--name", required=True, help="Track display name.")
    tp.add_argument("--location", required=True,
                    help='Track location, e.g. "Suzuka, Japan".')
    tp.add_argument("--length", type=float, required=True,
                    help="Track length in metres.")
    tp.add_argument("--pit-boxes", type=int, default=20,
                    help="Number of pit-lane boxes (default: 20).")
    tp.add_argument("--surface",
                    choices=[s.value for s in SurfaceType],
                    default=SurfaceType.ASPHALT.value,
                    help="Primary road surface type (default: asphalt).")
    tp.add_argument("--description", default="", help="Optional description.")
    tp.add_argument("--author", default="Unknown", help="Mod author name.")
    tp.add_argument("--version", default="1.0", help="Mod version string.")
    tp.add_argument("--output", default=".", help="Output directory (default: .).")

    # ------------------------------------------------------------------ car
    cp = sub.add_parser("car", help="Generate a racing car MOD.")
    cp.add_argument("--simulator", choices=list(_SIMULATORS), required=True,
                    help="Target race simulator.")
    cp.add_argument("--name", required=True, help="Car model name.")
    cp.add_argument("--manufacturer", required=True, help="Manufacturer name.")
    cp.add_argument("--class", dest="car_class",
                    choices=[c.value for c in CarClass], required=True,
                    help="Racing class (e.g. GT3, LMP1, Formula).")
    cp.add_argument("--year", type=int, required=True, help="Model year.")
    cp.add_argument("--displacement", type=float, required=True,
                    help="Engine displacement in cc.")
    cp.add_argument("--cylinders", type=int, required=True,
                    help="Number of engine cylinders.")
    cp.add_argument("--max-power-kw", type=float, required=True,
                    help="Maximum engine power in kW.")
    cp.add_argument("--max-torque-nm", type=float, required=True,
                    help="Maximum engine torque in Nm.")
    cp.add_argument("--max-rpm", type=int, required=True,
                    help="Engine rev limit in RPM.")
    cp.add_argument("--turbo", action="store_true",
                    help="Engine has forced induction (turbo/supercharger).")
    cp.add_argument("--mass-kg", type=float, required=True,
                    help="Total vehicle mass in kg.")
    cp.add_argument("--description", default="", help="Optional description.")
    cp.add_argument("--author", default="Unknown", help="Mod author name.")
    cp.add_argument("--version", default="1.0", help="Mod version string.")
    cp.add_argument("--output", default=".", help="Output directory (default: .).")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``race-mod-create`` command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    generator_cls = _SIMULATORS[args.simulator]
    generator = generator_cls(output_dir=args.output)

    if args.command == "track":
        track = Track(
            name=args.name,
            location=args.location,
            length_m=args.length,
            pit_boxes=args.pit_boxes,
            surface=SurfaceType(args.surface),
            description=args.description,
            author=args.author,
            version=args.version,
        )
        result = generator.generate_track(track)
        print(f"[{generator.simulator_name}] Track MOD generated: {result}")

    elif args.command == "car":
        engine = EngineSpec(
            displacement_cc=args.displacement,
            cylinders=args.cylinders,
            max_power_kw=args.max_power_kw,
            max_torque_nm=args.max_torque_nm,
            max_rpm=args.max_rpm,
            naturally_aspirated=not args.turbo,
        )
        car = Car(
            name=args.name,
            manufacturer=args.manufacturer,
            car_class=CarClass(args.car_class),
            year=args.year,
            engine=engine,
            mass_kg=args.mass_kg,
            description=args.description,
            author=args.author,
            version=args.version,
        )
        result = generator.generate_car(car)
        print(f"[{generator.simulator_name}] Car MOD generated: {result}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
