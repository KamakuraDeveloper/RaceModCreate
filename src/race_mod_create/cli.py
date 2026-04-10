"""Command-line interface for RaceModCreate.

Usage examples::

    # Generate an Assetto Corsa track mod
    race-mod-create track --simulator assetto_corsa \\
        --name "Suzuka Circuit" --location "Suzuka, Japan" \\
        --length 5807 --pit-boxes 32 --output ./mods

    # Generate a track mod from a JKT Kanto preset
    race-mod-create track --simulator assetto_corsa \\
        --preset haruna --output ./mods

    # List available presets
    race-mod-create presets

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

from race_mod_create.generators.assetto_corsa import AssettoCorsaGenerator
from race_mod_create.generators.rfactor import RFactorGenerator
from race_mod_create.models.car import Car, CarClass, EngineSpec
from race_mod_create.models.track import Track, SurfaceType
from race_mod_create.presets import JKT_KANTO_CIRCUITS, get_preset, list_presets

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

    # ------------------------------------------------------------------ presets
    sub.add_parser("presets", help="List available track presets.")

    # ------------------------------------------------------------------ track
    tp = sub.add_parser("track", help="Generate a track (circuit) MOD.")
    tp.add_argument("--simulator", choices=list(_SIMULATORS), required=True,
                    help="Target race simulator.")
    tp.add_argument("--preset", choices=list_presets(),
                    help="Use a predefined JKT Kanto circuit preset.")
    tp.add_argument("--name", help="Track display name.")
    tp.add_argument("--location",
                    help='Track location, e.g. "Suzuka, Japan".')
    tp.add_argument("--length", type=float,
                    help="Track length in metres.")
    tp.add_argument("--pit-boxes", type=int, default=None,
                    help="Number of pit-lane boxes (default: 20).")
    tp.add_argument("--surface",
                    choices=[s.value for s in SurfaceType],
                    default=None,
                    help="Primary road surface type (default: asphalt).")
    tp.add_argument("--description", default=None, help="Optional description.")
    tp.add_argument("--author", default=None, help="Mod author name.")
    tp.add_argument("--version", default=None, help="Mod version string.")
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

    # ---- presets listing ---------------------------------------------------
    if args.command == "presets":
        print("Available track presets (JKT Kanto series):")
        for name in list_presets():
            t = JKT_KANTO_CIRCUITS[name]
            print(f"  {name:20s}  {t.name} ({t.location}, {t.length_m:.0f}m)")
        return 0

    # ---- track / car generation -------------------------------------------
    generator_cls = _SIMULATORS[args.simulator]
    generator = generator_cls(output_dir=args.output)

    if args.command == "track":
        if args.preset:
            track = get_preset(args.preset)
            # Allow CLI flags to override preset values
            if args.name is not None:
                track.name = args.name
            if args.location is not None:
                track.location = args.location
            if args.length is not None:
                track.length_m = args.length
            if args.pit_boxes is not None:
                track.pit_boxes = args.pit_boxes
            if args.surface is not None:
                track.surface = SurfaceType(args.surface)
            if args.description is not None:
                track.description = args.description
            if args.author is not None:
                track.author = args.author
            if args.version is not None:
                track.version = args.version
        else:
            # Manual mode – name, location, and length are required
            if not args.name or not args.location or args.length is None:
                parser.error(
                    "When --preset is not used, --name, --location, and --length "
                    "are required."
                )
            track = Track(
                name=args.name,
                location=args.location,
                length_m=args.length,
                pit_boxes=args.pit_boxes if args.pit_boxes is not None else 20,
                surface=SurfaceType(args.surface) if args.surface else SurfaceType.ASPHALT,
                description=args.description or "",
                author=args.author or "Unknown",
                version=args.version or "1.0",
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
            description=args.description or "",
            author=args.author or "Unknown",
            version=args.version or "1.0",
        )
        result = generator.generate_car(car)
        print(f"[{generator.simulator_name}] Car MOD generated: {result}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
