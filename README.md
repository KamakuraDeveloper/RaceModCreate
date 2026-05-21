# RaceModCreate

好きなサーキットや車のMODを色んな実行環境向けに生成します。

Generate MOD files for racing circuits and cars, compatible with multiple race simulators.

## Supported simulators

| Simulator | Tracks | Cars |
|-----------|--------|------|
| Assetto Corsa | ✅ | ✅ |
| rFactor | ✅ | ✅ |

## Installation

```bash
pip install -e .
```

## Usage

### Command-line interface

**Generate a track MOD (Assetto Corsa)**

```bash
race-mod-create track \
  --simulator assetto_corsa \
  --name "Suzuka Circuit" \
  --location "Suzuka, Japan" \
  --length 5807 \
  --pit-boxes 32 \
  --output ./mods
```

**Generate a car MOD (rFactor)**

```bash
race-mod-create car \
  --simulator rfactor \
  --name "GT3 Racer" \
  --manufacturer "SpeedCraft" \
  --class GT3 \
  --year 2024 \
  --displacement 3982 \
  --cylinders 6 \
  --max-power-kw 368 \
  --max-torque-nm 450 \
  --max-rpm 7500 \
  --mass-kg 1300 \
  --output ./mods
```

Use `--turbo` for forced-induction engines. Use `--surface` (track command only) to specify the road surface (`asphalt`, `concrete`, `gravel`, `dirt`, `grass`).

### Python API

```python
from race_mod_create import (
    Track, Sector, SurfaceType,
    Car, CarClass, EngineSpec, TyreSpec,
    AssettoCorsaGenerator, RFactorGenerator,
)

# Define a track
track = Track(
    name="Suzuka Circuit",
    location="Suzuka, Japan",
    length_m=5807,
    pit_boxes=32,
    sectors=[
        Sector("S1", 1800),
        Sector("S2", 2500),
        Sector("S3", 1507),
    ],
)

# Generate for Assetto Corsa
gen = AssettoCorsaGenerator(output_dir="./mods")
mod_path = gen.generate_track(track)
print(f"Generated: {mod_path}")

# Define a car
engine = EngineSpec(
    displacement_cc=3982, cylinders=6,
    max_power_kw=368, max_torque_nm=450, max_rpm=7500,
)
car = Car(
    name="GT3 Racer", manufacturer="SpeedCraft",
    car_class=CarClass.GT3, year=2024,
    engine=engine, mass_kg=1300,
    tyres=[TyreSpec("Soft", 305, 30, 18)],
)

# Generate for rFactor
gen_rf = RFactorGenerator(output_dir="./mods")
car_path = gen_rf.generate_car(car)
print(f"Generated: {car_path}")
```

## Generated file layout

### Assetto Corsa

```
content/
  tracks/<track_id>/
    ui/ui_track.json
    data/surfaces.ini
    data/map.ini
  cars/<car_id>/
    ui/ui_car.json
    data/car.ini
    data/engine.ini
    data/tyres.ini
```

### rFactor

```
GameData/
  Locations/<TrackID>/
    <TrackID>.gdb
    <TrackID>.scn
  Vehicles/<CarID>/
    <CarID>.veh
    <CarID>.hdv
    <CarID>_engine.ini
```

## Running tests

```bash
pip install pytest
pytest
```

