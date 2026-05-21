"""race-mod-create コマンドラインインターフェース。

@file cli.py
@brief レースシミュレーター用MODファイルを生成するCLIツールです。

@details
  以下のサブコマンドを提供します:

  - track:          手動パラメータからサーキットMODを生成
  - car:            手動パラメータから車両MODを生成
  - course-from-gps: Insta360 GPSデータ（+ オプションのAlfanoデータ）から
                     コースMODを自動生成

  使い方の例::

    # Assetto Corsaのサーキットモジュールを生成
    race-mod-create track --simulator assetto_corsa \\
        --name "Suzuka Circuit" --location "Suzuka, Japan" \\
        --length 5807 --pit-boxes 32 --output ./mods

    # rFactorの車両モジュールを生成
    race-mod-create car --simulator rfactor \\
        --name "GT3 Racer" --manufacturer "SpeedCraft" \\
        --class GT3 --year 2024 \\
        --displacement 3982 --cylinders 6 \\
        --max-power-kw 368 --max-torque-nm 450 --max-rpm 7500 \\
        --mass-kg 1300 --output ./mods

    # Insta360 GPSデータからコースMODを生成
    race-mod-create course-from-gps \\
        --insta360-csv ./gps_data.csv \\
        --alfano-csv ./alfano_data.csv \\
        --simulator assetto_corsa \\
        --output ./mods
"""

from __future__ import annotations

import argparse
import sys

from race_mod_create.generators.assetto_corsa import AssettoCorsaGenerator
from race_mod_create.generators.rfactor import RFactorGenerator
from race_mod_create.models.car import Car, CarClass, EngineSpec
from race_mod_create.models.track import Track, SurfaceType

_SIMULATORS = {
    "assetto_corsa": AssettoCorsaGenerator,
    "rfactor": RFactorGenerator,
}


def _build_parser() -> argparse.ArgumentParser:
    """コマンドライン引数パーサーを構築します。

    @brief race-mod-create の全サブコマンドとオプションを定義します。
    @return 構築済みの ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="race-mod-create",
        description="レースシミュレーター用MODファイルを生成します。",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------------ track
    tp = sub.add_parser("track", help="サーキット（コース）MODを生成します。")
    tp.add_argument("--simulator", choices=list(_SIMULATORS), required=True,
                    help="対象のレースシミュレーター。")
    tp.add_argument("--name", required=True, help="サーキットの表示名。")
    tp.add_argument("--location", required=True,
                    help='サーキットの所在地（例: "Suzuka, Japan"）。')
    tp.add_argument("--length", type=float, required=True,
                    help="コース全長（メートル）。")
    tp.add_argument("--pit-boxes", type=int, default=20,
                    help="ピットボックス数（デフォルト: 20）。")
    tp.add_argument("--surface",
                    choices=[s.value for s in SurfaceType],
                    default=SurfaceType.ASPHALT.value,
                    help="主な路面タイプ（デフォルト: asphalt）。")
    tp.add_argument("--description", default="", help="コースの説明（任意）。")
    tp.add_argument("--author", default="Unknown", help="MOD作者名。")
    tp.add_argument("--version", default="1.0", help="MODバージョン。")
    tp.add_argument("--output", default=".", help="出力ディレクトリ（デフォルト: .）。")

    # ------------------------------------------------------------------ car
    cp = sub.add_parser("car", help="レーシングカーMODを生成します。")
    cp.add_argument("--simulator", choices=list(_SIMULATORS), required=True,
                    help="対象のレースシミュレーター。")
    cp.add_argument("--name", required=True, help="車両モデル名。")
    cp.add_argument("--manufacturer", required=True, help="メーカー名。")
    cp.add_argument("--class", dest="car_class",
                    choices=[c.value for c in CarClass], required=True,
                    help="レーシングクラス（例: GT3, LMP1, Formula）。")
    cp.add_argument("--year", type=int, required=True, help="モデル年式。")
    cp.add_argument("--displacement", type=float, required=True,
                    help="エンジン排気量（cc）。")
    cp.add_argument("--cylinders", type=int, required=True,
                    help="エンジン気筒数。")
    cp.add_argument("--max-power-kw", type=float, required=True,
                    help="最大出力（kW）。")
    cp.add_argument("--max-torque-nm", type=float, required=True,
                    help="最大トルク（Nm）。")
    cp.add_argument("--max-rpm", type=int, required=True,
                    help="最大回転数（RPM）。")
    cp.add_argument("--turbo", action="store_true",
                    help="強制吸気（ターボ/スーパーチャージャー）の場合に指定。")
    cp.add_argument("--mass-kg", type=float, required=True,
                    help="車両総重量（kg）。")
    cp.add_argument("--description", default="", help="車両の説明（任意）。")
    cp.add_argument("--author", default="Unknown", help="MOD作者名。")
    cp.add_argument("--version", default="1.0", help="MODバージョン。")
    cp.add_argument("--output", default=".", help="出力ディレクトリ（デフォルト: .）。")

    # -------------------------------------------------------- course-from-gps
    gp = sub.add_parser(
        "course-from-gps",
        help="Insta360 GPSデータからコースMODを生成します。",
    )
    # Insta360データ入力（CSVまたはGPX、どちらか一つ以上が必要）
    gp.add_argument(
        "--insta360-csv",
        help="Insta360 GPSデータCSVファイルのパス。",
    )
    gp.add_argument(
        "--insta360-gpx",
        help="Insta360 GPSデータGPXファイルのパス。",
    )
    # Alfanoデータ（オプション）
    gp.add_argument(
        "--alfano-csv",
        help="Alfano走行データCSVファイルのパス（オプション）。",
    )
    gp.add_argument(
        "--time-offset",
        type=float,
        default=0.0,
        help="Alfanoデータのタイムオフセット補正値（秒、デフォルト: 0.0）。",
    )
    # シミュレーター（オプション — 指定するとMODも生成）
    gp.add_argument(
        "--simulator",
        choices=list(_SIMULATORS),
        help="MOD生成対象のシミュレーター（省略時はレポートのみ生成）。",
    )
    gp.add_argument("--output", default=".", help="出力ディレクトリ（デフォルト: .）。")

    return parser


def main(argv: list[str] | None = None) -> int:
    """race-mod-create コマンドのエントリーポイント。

    @brief コマンドライン引数を解析し、適切なMOD生成処理を実行します。
    @param argv コマンドライン引数のリスト（Noneの場合は sys.argv を使用）
    @return 終了コード（正常: 0）
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "track":
        return _handle_track(args)
    elif args.command == "car":
        return _handle_car(args)
    elif args.command == "course-from-gps":
        return _handle_course_from_gps(args)

    return 0


def _handle_track(args: argparse.Namespace) -> int:
    """trackサブコマンドを処理します。

    @brief 引数からTrackオブジェクトを構築し、MODを生成します。
    @param args 解析済みコマンドライン引数
    @return 終了コード
    """
    generator_cls = _SIMULATORS[args.simulator]
    generator = generator_cls(output_dir=args.output)

    try:
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
    except ValueError as exc:
        _build_parser().error(str(exc))
    result = generator.generate_track(track)
    print(f"[{generator.simulator_name}] Track MOD generated: {result}")
    return 0


def _handle_car(args: argparse.Namespace) -> int:
    """carサブコマンドを処理します。

    @brief 引数からCarオブジェクトを構築し、MODを生成します。
    @param args 解析済みコマンドライン引数
    @return 終了コード
    """
    generator_cls = _SIMULATORS[args.simulator]
    generator = generator_cls(output_dir=args.output)

    try:
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
    except ValueError as exc:
        _build_parser().error(str(exc))
    result = generator.generate_car(car)
    print(f"[{generator.simulator_name}] Car MOD generated: {result}")
    return 0


def _handle_course_from_gps(args: argparse.Namespace) -> int:
    """course-from-gpsサブコマンドを処理します。

    @brief Insta360 GPSデータとオプションのAlfanoデータからコースMODを生成します。
    @param args 解析済みコマンドライン引数
    @return 終了コード

    @details
      処理の流れ:
        1. Insta360のGPSデータ（CSVまたはGPX）を読み込む
        2. Alfanoデータが指定された場合はそれも読み込む
        3. CourseModBuilderでコースMODとレポートを生成

    @raises SystemExit Insta360データが指定されていない場合
    """
    # Insta360パーサーとAlfanoパーサーのインポート
    from race_mod_create.alfano.data_parser import AlfanoDataParser
    from race_mod_create.course.course_mod_builder import CourseModBuilder
    from race_mod_create.insta360.gps_parser import Insta360GpsParser

    # --- Insta360 GPSデータの読み込み ---
    insta360_parser = Insta360GpsParser()
    insta360_track = None

    if args.insta360_csv:
        insta360_track = insta360_parser.parse_csv(args.insta360_csv)
        print(f"[Insta360] CSVから {len(insta360_track.points)} 個のGPS計測点を読み込みました。")
    elif args.insta360_gpx:
        insta360_track = insta360_parser.parse_gpx(args.insta360_gpx)
        print(f"[Insta360] GPXから {len(insta360_track.points)} 個のGPS計測点を読み込みました。")
    else:
        print("エラー: --insta360-csv または --insta360-gpx のいずれかを指定してください。",
              file=sys.stderr)
        return 1

    # --- Alfanoデータの読み込み（オプション） ---
    alfano_session = None
    if args.alfano_csv:
        alfano_parser = AlfanoDataParser()
        alfano_session = alfano_parser.parse_csv(args.alfano_csv)
        print(
            f"[Alfano] {alfano_session.lap_count} ラップ, "
            f"{len(alfano_session.data_points)} 個のデータポイントを読み込みました。"
        )

    # --- コースMODの生成 ---
    builder = CourseModBuilder(output_dir=args.output)
    result = builder.build_from_gps(
        insta360_track=insta360_track,
        alfano_session=alfano_session,
        time_offset_s=args.time_offset,
        simulator=args.simulator,
    )
    print(f"[CourseModBuilder] コースレポートを生成しました: {result}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
