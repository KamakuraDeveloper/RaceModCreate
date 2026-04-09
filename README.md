# RaceModCreate

好きなサーキットや車のMODを色んな実行環境向けに生成します。

Generate MOD files for racing circuits and cars, compatible with multiple race simulators.

## Supported simulators

| Simulator | Tracks | Cars |
|-----------|--------|------|
| Assetto Corsa | ✅ | ✅ |
| rFactor | ✅ | ✅ |

## Features / 機能

- **手動パラメータからのMOD生成**: サーキット名、コース長などを指定してMODファイルを生成
- **Insta360 GPSデータからのコースMOD生成**: 360度カメラの走行データからサーキットを自動識別
- **Alfanoデータとの同期**: Alfanoラップタイマーの走行テレメトリ（RPM、速度、温度）とInsta360 GPSデータを統合
- **サーキット自動識別**: GPS座標から既知のサーキット（大井松田カートランド、鈴鹿サーキット等）を自動特定
- **コースレポート生成**: 走行データの統計情報をJSON形式で出力

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

**Generate a course MOD from Insta360 GPS data**

```bash
# GPSデータのみ（Insta360 CSV形式）
race-mod-create course-from-gps \
  --insta360-csv ./gps_data.csv \
  --output ./mods

# GPSデータ + Alfanoデータ + シミュレーターMOD生成
race-mod-create course-from-gps \
  --insta360-csv ./gps_data.csv \
  --alfano-csv ./alfano_data.csv \
  --simulator assetto_corsa \
  --output ./mods

# GPX形式のGPSデータ
race-mod-create course-from-gps \
  --insta360-gpx ./gps_data.gpx \
  --simulator rfactor \
  --output ./mods
```

Use `--turbo` for forced-induction engines. Use `--surface` to specify the road surface (`asphalt`, `concrete`, `gravel`, `dirt`, `grass`).

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

### GPS-based Course MOD Generation / GPSベースのコースMOD生成

```python
from race_mod_create import (
    Insta360GpsParser, AlfanoDataParser,
    CourseModBuilder, CircuitIdentifier,
)

# Insta360 GPSデータの読み込み
parser = Insta360GpsParser()
gps_track = parser.parse_csv("F:/work/Camera01/gps_data.csv")
print(f"計測点数: {len(gps_track.points)}")
print(f"走行距離: {gps_track.total_distance_m():.0f}m")

# サーキットの自動識別
identifier = CircuitIdentifier()
circuit = identifier.identify_from_gps_track(gps_track)
if circuit:
    print(f"サーキット名: {circuit.name}")
    print(f"コース長: {circuit.length_m}m")
    print(f"特徴: {', '.join(circuit.features)}")

# Alfanoデータの読み込み（オプション）
alfano_parser = AlfanoDataParser()
alfano_session = alfano_parser.parse_csv("alfano_export.csv")
print(f"ラップ数: {alfano_session.lap_count}")
print(f"ベストラップ: {alfano_session.best_lap_time_s:.3f}秒")

# コースMODの生成（レポート + Assetto Corsa MOD）
builder = CourseModBuilder(output_dir="./mods")
report_path = builder.build_from_gps(
    insta360_track=gps_track,
    alfano_session=alfano_session,
    simulator="assetto_corsa",
)
print(f"レポート: {report_path}")
```

## Supported Insta360 GPS data formats / 対応するGPSデータ形式

| Format | Extension | Description |
|--------|-----------|-------------|
| CSV | `.csv` | Insta360 Studio からエクスポートされたカンマ区切りファイル |
| GPX | `.gpx` | GPS Exchange Format（標準XML形式） |

## Known circuits / 登録済みサーキット

| サーキット名 | 英語名 | 所在地 | コース長 |
|------------|--------|--------|---------|
| 大井松田カートランド | Oimatsuda Kartland | 神奈川県 | 670m |
| フェスティカサーキット栃木 | Festika Circuit Tochigi | 栃木県 | 780m |
| 新東京サーキット | Shin-Tokyo Circuit | 千葉県 | 1003m |
| 本庄サーキット | Honjo Circuit | 埼玉県 | 550m |
| 幸田サーキット | Kota Circuit | 愛知県 | 700m |
| 鈴鹿サーキット | Suzuka Circuit | 三重県 | 5807m |
| モビリティリゾートもてぎ | Mobility Resort Motegi | 栃木県 | 4801m |

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

### Course Report (GPS-based)

```
course_report/
  <circuit_name>_report.json
```

## Running tests

```bash
pip install pytest
pytest
```

