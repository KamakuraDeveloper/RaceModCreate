"""Alfanoラップタイマーのデータ解析パーサー。

@file data_parser.py
@brief Alfano（アルファノ）デバイスからエクスポートされた
       走行データCSVを解析するパーサーです。

@details
  Alfanoは主にカート走行で使用されるラップタイマー・データロガーです。
  デバイスからPCにエクスポートしたCSVファイルには、以下のような
  走行テレメトリ情報が含まれます:

    - ラップタイム
    - エンジン回転数 (RPM)
    - 速度 (km/h)
    - 排気温度 (℃)
    - GPS座標（GPS搭載モデルの場合）

  エクスポート形式の例（Alfano Pro/Astro）::

    lap,time_s,rpm,speed_kmh,temp_c,latitude,longitude
    1,0.000,0,0.0,45.0,35.3416,139.1513
    1,0.100,5200,32.5,48.2,35.3417,139.1514

  使い方::

    from race_mod_create.alfano import AlfanoDataParser
    parser = AlfanoDataParser()
    session = parser.parse_csv("alfano_data.csv")
    print(f"ラップ数: {session.lap_count}")
    print(f"ベストラップ: {session.best_lap_time_s:.3f}秒")
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Union

from race_mod_create.models.gps_models import GpsPoint, GpsTrack


@dataclass
class AlfanoDataPoint:
    """Alfanoの1計測ポイントを表すデータクラス。

    @brief Alfanoデバイスが記録する1回のサンプリングデータです。

    @param lap_number  ラップ番号（1始まり）
    @param time_s      セッション開始からの経過時間（秒）
    @param rpm         エンジン回転数（回転/分、任意）
    @param speed_kmh   車速（km/h、任意）
    @param temp_c      排気温度（℃、任意）
    @param latitude    GPS緯度（度数法、GPS搭載モデルのみ）
    @param longitude   GPS経度（度数法、GPS搭載モデルのみ）
    """

    lap_number: int
    time_s: float
    rpm: Optional[int] = None
    speed_kmh: Optional[float] = None
    temp_c: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class LapSummary:
    """1ラップの要約データ。

    @brief 1周分の走行データを集約した情報です。

    @param lap_number  ラップ番号
    @param lap_time_s  ラップタイム（秒）
    @param max_rpm     最大RPM
    @param max_speed   最高速度（km/h）
    @param avg_speed   平均速度（km/h）
    @param max_temp_c  最高排気温度（℃）
    """

    lap_number: int
    lap_time_s: float
    max_rpm: Optional[int] = None
    max_speed: Optional[float] = None
    avg_speed: Optional[float] = None
    max_temp_c: Optional[float] = None


@dataclass
class AlfanoSession:
    """Alfanoの1セッション（走行全体）を表すデータクラス。

    @brief Alfanoでの1回の走行セッションに含まれる全データを保持します。

    @param data_points  全計測ポイントのリスト
    @param laps         ラップ要約のリスト
    @param name         セッション名（ファイル名など）
    @param session_date セッション日時（任意）
    """

    data_points: List[AlfanoDataPoint] = field(default_factory=list)
    laps: List[LapSummary] = field(default_factory=list)
    name: str = ""
    session_date: Optional[datetime] = None

    @property
    def lap_count(self) -> int:
        """セッション内のラップ数を返します。

        @brief ラップ要約リストの要素数を返します。
        @return ラップ数
        """
        return len(self.laps)

    @property
    def best_lap_time_s(self) -> Optional[float]:
        """ベストラップタイム（秒）を返します。

        @brief 全ラップの中で最も短いラップタイムを返します。
        @return ベストラップタイム（秒）、ラップがない場合はNone
        """
        if not self.laps:
            return None
        return min(lap.lap_time_s for lap in self.laps)

    @property
    def total_time_s(self) -> float:
        """セッションの合計時間（秒）を返します。

        @brief 全ラップタイムの合計を返します。
        @return 合計時間（秒）
        """
        return sum(lap.lap_time_s for lap in self.laps)

    def to_gps_track(self, base_time: Optional[datetime] = None) -> GpsTrack:
        """AlfanoセッションデータをGpsTrackに変換します。

        @brief GPS座標が含まれるデータポイントのみをGpsPointに変換し、
               GpsTrackオブジェクトとして返します。
        @param base_time GPSトラックのベース時刻。
                         Noneの場合はsession_dateまたはエポック時刻を使用。
        @return GpsTrackオブジェクト

        @details
          Alfanoのtime_s（経過秒）をbase_timeに加算して
          各計測点のタイムスタンプを生成します。
        """
        if base_time is None:
            base_time = self.session_date or datetime(2024, 1, 1)

        points: list[GpsPoint] = []
        for dp in self.data_points:
            if dp.latitude is not None and dp.longitude is not None:
                ts = base_time + timedelta(seconds=dp.time_s)
                points.append(
                    GpsPoint(
                        latitude=dp.latitude,
                        longitude=dp.longitude,
                        timestamp=ts,
                        speed_kmh=dp.speed_kmh,
                    )
                )

        return GpsTrack(
            points=points,
            name=self.name,
            source="Alfano",
        )


class AlfanoDataParser:
    """AlfanoデバイスのCSVデータを解析するパーサークラス。

    @brief Alfanoからエクスポートされた走行データCSVを読み込み、
           AlfanoSession オブジェクトを返します。

    @details
      以下のCSVカラムに対応しています:
        - lap:        ラップ番号
        - time_s:     経過時間（秒）
        - rpm:        エンジン回転数（任意カラム）
        - speed_kmh:  速度 km/h（任意カラム）
        - temp_c:     排気温度 ℃（任意カラム）
        - latitude:   緯度（任意カラム — GPS搭載モデル）
        - longitude:  経度（任意カラム — GPS搭載モデル）
    """

    def parse_csv(self, file_path: Union[str, Path]) -> AlfanoSession:
        """CSVファイルからAlfano走行データを読み込みます。

        @brief Alfano CSVファイルを解析し、AlfanoSession を返します。
        @param file_path 読み込むCSVファイルのパス
        @return 解析済みのAlfanoSessionオブジェクト

        @raises FileNotFoundError ファイルが見つからない場合
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Alfanoデータファイルが見つかりません: {file_path}")

        data_points: list[AlfanoDataPoint] = []

        with file_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                point = self._parse_row(row)
                if point is not None:
                    data_points.append(point)

        # ラップ要約を生成
        laps = self._build_lap_summaries(data_points)

        return AlfanoSession(
            data_points=data_points,
            laps=laps,
            name=file_path.stem,
        )

    def _parse_row(self, row: dict[str, str]) -> AlfanoDataPoint | None:
        """CSVの1行をAlfanoDataPointに変換します。

        @brief CSVの辞書形式の行データからAlfanoDataPointを生成します。
        @param row CSVの1行（辞書形式）
        @return 解析に成功した場合はAlfanoDataPoint、失敗した場合はNone
        """
        try:
            lap = int(row.get("lap", "0").strip())
            time_s = float(row.get("time_s", "0").strip())

            # 任意カラムの取得（存在しない場合はNone）
            rpm = self._parse_optional_int(row.get("rpm"))
            speed = self._parse_optional_float(row.get("speed_kmh"))
            temp = self._parse_optional_float(row.get("temp_c"))
            lat = self._parse_optional_float(row.get("latitude"))
            lon = self._parse_optional_float(row.get("longitude"))

            return AlfanoDataPoint(
                lap_number=lap,
                time_s=time_s,
                rpm=rpm,
                speed_kmh=speed,
                temp_c=temp,
                latitude=lat,
                longitude=lon,
            )
        except (ValueError, KeyError):
            return None

    @staticmethod
    def _parse_optional_float(value: str | None) -> float | None:
        """文字列をfloatに変換します（Noneまたは空文字はNoneを返す）。

        @brief 任意カラムの値を安全にfloatに変換するヘルパーです。
        @param value 変換する文字列
        @return 変換されたfloat値、またはNone
        """
        if value is None or value.strip() == "":
            return None
        try:
            return float(value.strip())
        except ValueError:
            return None

    @staticmethod
    def _parse_optional_int(value: str | None) -> int | None:
        """文字列をintに変換します（Noneまたは空文字はNoneを返す）。

        @brief 任意カラムの値を安全にintに変換するヘルパーです。
        @param value 変換する文字列
        @return 変換されたint値、またはNone
        """
        if value is None or value.strip() == "":
            return None
        try:
            return int(float(value.strip()))
        except ValueError:
            return None

    @staticmethod
    def _build_lap_summaries(data_points: list[AlfanoDataPoint]) -> list[LapSummary]:
        """計測ポイントからラップ要約を生成します。

        @brief 各ラップ番号ごとにデータを集約し、LapSummaryのリストを生成します。
        @param data_points 全計測ポイントのリスト
        @return ラップ要約のリスト（ラップ番号順）

        @details
          ラップタイムは、各ラップ内の最大time_sから最小time_sを引いて算出します。
          同じラップの全データポイントから最大RPM、最高速度、平均速度等を求めます。
        """
        if not data_points:
            return []

        # ラップ番号でグループ化
        laps_dict: dict[int, list[AlfanoDataPoint]] = {}
        for dp in data_points:
            laps_dict.setdefault(dp.lap_number, []).append(dp)

        summaries: list[LapSummary] = []
        for lap_num in sorted(laps_dict.keys()):
            lap_points = laps_dict[lap_num]
            times = [p.time_s for p in lap_points]
            lap_time = max(times) - min(times) if len(times) > 1 else 0.0

            # RPMの集約
            rpms = [p.rpm for p in lap_points if p.rpm is not None]
            max_rpm = max(rpms) if rpms else None

            # 速度の集約
            speeds = [p.speed_kmh for p in lap_points if p.speed_kmh is not None]
            max_speed = max(speeds) if speeds else None
            avg_speed = sum(speeds) / len(speeds) if speeds else None

            # 温度の集約
            temps = [p.temp_c for p in lap_points if p.temp_c is not None]
            max_temp = max(temps) if temps else None

            summaries.append(
                LapSummary(
                    lap_number=lap_num,
                    lap_time_s=lap_time,
                    max_rpm=max_rpm,
                    max_speed=max_speed,
                    avg_speed=avg_speed,
                    max_temp_c=max_temp,
                )
            )

        return summaries
