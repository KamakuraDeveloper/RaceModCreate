"""コースMODビルダーモジュール。

@file course_mod_builder.py
@brief GPS走行データとサーキット情報を組み合わせて、
       レースシミュレーター用のコースMODを生成します。

@details
  このモジュールは、Insta360のGPSデータ（とオプションのAlfanoデータ）から
  取得した走行軌跡情報と、サーキット識別結果を統合して
  コースMODの資料と設定ファイルを生成します。

  生成物:
    - コース情報レポート（JSON形式）:
        サーキットの基本情報、GPS走行データの統計、
        コース特徴などをまとめたレポートファイル
    - 既存のAssetto Corsa/rFactor向けTrack MOD生成と連携

  使い方::

    from race_mod_create.course import CourseModBuilder
    builder = CourseModBuilder(output_dir="./output")
    result = builder.build_from_gps(
        insta360_track=gps_track,
        alfano_session=alfano_session,  # オプション
    )
    print(f"レポート出力先: {result}")
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from race_mod_create.alfano.data_parser import AlfanoSession
from race_mod_create.course.circuit_identifier import CircuitIdentifier, CircuitInfo
from race_mod_create.course.sync import DataSynchronizer, SynchronizedPoint
from race_mod_create.generators.assetto_corsa import AssettoCorsaGenerator
from race_mod_create.generators.rfactor import RFactorGenerator
from race_mod_create.models.gps_models import GpsTrack
from race_mod_create.models.track import SurfaceType, Track


class CourseModBuilder:
    """コースMODを生成するビルダークラス。

    @brief GPS走行データからコースMODの資料と設定ファイルを生成します。

    @details
      生成フロー:
        1. GPS走行データの読み込みと解析
        2. サーキットの自動識別
        3. Alfanoデータとの同期（オプション）
        4. コース情報レポートの生成
        5. シミュレーター用MODファイルの生成（オプション）
    """

    def __init__(self, output_dir: Union[str, Path] = ".") -> None:
        """CourseModBuilderを初期化します。

        @brief 出力先ディレクトリを設定します。
        @param output_dir MODファイルの出力先ディレクトリ
        """
        self._output_dir = Path(output_dir)
        self._circuit_identifier = CircuitIdentifier()
        self._synchronizer = DataSynchronizer()

    def build_from_gps(
        self,
        insta360_track: GpsTrack,
        alfano_session: Optional[AlfanoSession] = None,
        time_offset_s: float = 0.0,
        simulator: Optional[str] = None,
    ) -> Path:
        """GPS走行データからコースMODを生成します。

        @brief Insta360 GPSデータとオプションのAlfanoデータから
               コースMODの資料を生成します。
        @param insta360_track  Insta360から取得したGPS走行軌跡
        @param alfano_session  Alfanoセッションデータ（オプション）
        @param time_offset_s   Alfanoデータの時刻オフセット（秒）
        @param simulator       MOD生成対象のシミュレーター名
                               ("assetto_corsa" または "rfactor"、Noneの場合はレポートのみ)
        @return 生成されたレポートファイルのパス

        @details
          処理の流れ:
            1. GPSトラックからサーキットを識別
            2. Alfanoデータが指定された場合はInsta360データと同期
            3. コースレポート（JSON）を出力
            4. シミュレーターが指定された場合はTrack MODも出力
        """
        # ステップ1: サーキットの識別
        circuit_info = self._circuit_identifier.identify_from_gps_track(insta360_track)

        # ステップ2: データの同期
        if alfano_session is not None:
            sync_points = self._synchronizer.synchronize(
                insta360_track, alfano_session, time_offset_s
            )
        else:
            sync_points = self._synchronizer.synchronize_gps_only(insta360_track)

        # ステップ3: コースレポートの生成
        report_path = self._generate_course_report(
            insta360_track=insta360_track,
            circuit_info=circuit_info,
            sync_points=sync_points,
            alfano_session=alfano_session,
        )

        # ステップ4: シミュレーターMODの生成（オプション）
        if simulator is not None and circuit_info is not None:
            self._generate_simulator_mod(circuit_info, simulator)

        return report_path

    def _generate_course_report(
        self,
        insta360_track: GpsTrack,
        circuit_info: Optional[CircuitInfo],
        sync_points: list[SynchronizedPoint],
        alfano_session: Optional[AlfanoSession],
    ) -> Path:
        """コース情報レポート（JSON）を生成します。

        @brief GPS走行データの分析結果をJSON形式のレポートとして出力します。
        @param insta360_track  Insta360 GPSトラック
        @param circuit_info    識別されたサーキット情報（None可）
        @param sync_points     同期済みデータポイント
        @param alfano_session  Alfanoセッションデータ（None可）
        @return レポートファイルのパス
        """
        report: dict = {
            "generated_at": datetime.now().isoformat(),
            "generator": "RaceModCreate CourseModBuilder",
        }

        # --- GPSデータの統計 ---
        report["gps_data"] = {
            "source": insta360_track.source,
            "point_count": len(insta360_track.points),
            "total_distance_m": round(insta360_track.total_distance_m(), 1),
            "duration_s": insta360_track.duration_seconds(),
        }

        # バウンディングボックスと中心点
        if insta360_track.points:
            bbox = insta360_track.bounding_box()
            center = insta360_track.center_point()
            report["gps_data"]["bounding_box"] = {
                "min_lat": bbox[0],
                "min_lon": bbox[1],
                "max_lat": bbox[2],
                "max_lon": bbox[3],
            }
            report["gps_data"]["center"] = {
                "latitude": round(center.latitude, 6),
                "longitude": round(center.longitude, 6),
            }

        # --- サーキット情報 ---
        if circuit_info is not None:
            report["circuit"] = {
                "name": circuit_info.name,
                "name_en": circuit_info.name_en,
                "location": circuit_info.location,
                "length_m": circuit_info.length_m,
                "surface": circuit_info.surface,
                "description": circuit_info.description,
                "features": circuit_info.features,
                "pit_boxes": circuit_info.pit_boxes,
                "kart_circuit": circuit_info.kart_circuit,
            }
        else:
            report["circuit"] = {
                "name": "不明なサーキット",
                "name_en": "Unknown Circuit",
                "description": "GPS座標から既知のサーキットを特定できませんでした。",
            }

        # --- Alfanoデータの統計 ---
        if alfano_session is not None:
            alfano_stats: dict = {
                "source": "Alfano",
                "data_point_count": len(alfano_session.data_points),
                "lap_count": alfano_session.lap_count,
                "total_time_s": round(alfano_session.total_time_s, 3),
            }
            if alfano_session.best_lap_time_s is not None:
                alfano_stats["best_lap_time_s"] = round(
                    alfano_session.best_lap_time_s, 3
                )

            # ラップ詳細
            alfano_stats["laps"] = []
            for lap in alfano_session.laps:
                lap_dict: dict = {
                    "lap_number": lap.lap_number,
                    "lap_time_s": round(lap.lap_time_s, 3),
                }
                if lap.max_rpm is not None:
                    lap_dict["max_rpm"] = lap.max_rpm
                if lap.max_speed is not None:
                    lap_dict["max_speed_kmh"] = round(lap.max_speed, 1)
                if lap.avg_speed is not None:
                    lap_dict["avg_speed_kmh"] = round(lap.avg_speed, 1)
                alfano_stats["laps"].append(lap_dict)

            report["alfano_data"] = alfano_stats

        # --- 同期データの統計 ---
        report["synchronized_data"] = {
            "point_count": len(sync_points),
            "has_rpm_data": any(p.rpm is not None for p in sync_points),
            "has_speed_data": any(p.speed_kmh is not None for p in sync_points),
            "has_temp_data": any(p.temp_c is not None for p in sync_points),
        }

        # レポートファイルの出力
        report_dir = self._output_dir / "course_report"
        report_dir.mkdir(parents=True, exist_ok=True)

        # ファイル名はサーキット名またはGPSトラック名から生成
        if circuit_info is not None:
            filename = f"{circuit_info.name_en.replace(' ', '_').lower()}_report.json"
        else:
            safe_name = insta360_track.name or "unknown"
            filename = f"{safe_name}_report.json"

        report_path = report_dir / filename
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return report_path

    def _generate_simulator_mod(
        self, circuit_info: CircuitInfo, simulator: str
    ) -> Path:
        """サーキット情報からシミュレーター用MODを生成します。

        @brief CircuitInfoをTrackモデルに変換し、指定シミュレーター用のMODを出力します。
        @param circuit_info サーキット情報
        @param simulator シミュレーター名（"assetto_corsa" または "rfactor"）
        @return MOD出力ディレクトリのパス

        @raises ValueError サポートされていないシミュレーター名が指定された場合
        """
        # CircuitInfo → Track モデルへの変換
        track = Track(
            name=circuit_info.name_en,
            location=circuit_info.location,
            length_m=circuit_info.length_m,
            pit_boxes=circuit_info.pit_boxes,
            surface=SurfaceType(circuit_info.surface),
            description=circuit_info.description,
            author="RaceModCreate (GPS-based)",
            version="1.0",
        )

        # シミュレーター別のジェネレーターを選択
        generators = {
            "assetto_corsa": AssettoCorsaGenerator,
            "rfactor": RFactorGenerator,
        }

        if simulator not in generators:
            raise ValueError(
                f"サポートされていないシミュレーター: {simulator}"
                f"（対応: {', '.join(generators.keys())}）"
            )

        generator = generators[simulator](output_dir=self._output_dir)
        return generator.generate_track(track)
