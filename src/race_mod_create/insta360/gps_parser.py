"""Insta360カメラのGPSデータ解析パーサー。

@file gps_parser.py
@brief Insta360の360度カメラで記録されたGPSデータを読み込み、
       GpsTrack オブジェクトに変換するパーサーです。

@details
  Insta360カメラは走行中にGPSデータを動画メタデータとして記録します。
  Insta360 Studioからエクスポートされた以下のCSV形式に対応しています:

  CSV形式（カンマ区切り）:
    timestamp, latitude, longitude, altitude, speed
    2024-01-15T10:30:00, 35.3416, 139.1513, 120.5, 45.2

  また、標準的なGPX（GPS Exchange Format）ファイルの読み込みにも対応します。

  使い方の例::

    from race_mod_create.insta360 import Insta360GpsParser
    parser = Insta360GpsParser()
    track = parser.parse_csv("走行データ.csv")
    print(f"計測点数: {len(track.points)}")
    print(f"走行距離: {track.total_distance_m():.0f}m")
"""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Union

from race_mod_create.models.gps_models import GpsPoint, GpsTrack


class Insta360GpsParser:
    """Insta360カメラのGPSデータを解析するパーサークラス。

    @brief CSV形式またはGPX形式のGPSデータファイルを読み込み、
           GpsTrack オブジェクトを返します。

    @details
      このクラスは以下の入力形式をサポートします:
        1. CSV形式: Insta360 Studioからエクスポートされたカンマ区切りファイル
        2. GPX形式: 標準的なGPS Exchange Formatファイル

      サーキット走行データはInsta360カメラの動画に埋め込まれたGPS情報から
      抽出されます。F:\\work\\Camera01 のようなフォルダ内のデータを対象とします。
    """

    # -----------------------------------------------------------------------
    # CSVパーサー (Insta360 Studio エクスポート形式)
    # -----------------------------------------------------------------------

    # Insta360 CSVファイルで使用される日時フォーマット
    _CSV_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

    # 代替の日時フォーマット（ミリ秒対応）
    _CSV_DATETIME_FORMAT_MS = "%Y-%m-%dT%H:%M:%S.%f"

    def parse_csv(self, file_path: Union[str, Path]) -> GpsTrack:
        """CSVファイルからGPSデータを読み込みます。

        @brief カンマ区切りのCSVファイルを解析し、GpsTrack を返します。
        @param file_path 読み込むCSVファイルのパス
        @return 解析済みのGpsTrackオブジェクト

        @details
          期待するCSVのカラム構成:
            - timestamp:  計測時刻（ISO 8601形式）
            - latitude:   緯度（度数法）
            - longitude:  経度（度数法）
            - altitude:   高度（メートル、省略可）
            - speed:      速度（km/h、省略可）

        @raises FileNotFoundError ファイルが見つからない場合
        @raises ValueError CSVの形式が正しくない場合
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"GPSデータファイルが見つかりません: {file_path}")

        points: list[GpsPoint] = []

        with file_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                point = self._parse_csv_row(row)
                if point is not None:
                    points.append(point)

        return GpsTrack(
            points=points,
            name=file_path.stem,
            source="Insta360",
        )

    def _parse_csv_row(self, row: dict[str, str]) -> GpsPoint | None:
        """CSVの1行を解析してGpsPointに変換します。

        @brief CSVの辞書形式の行データからGpsPointを生成します。
        @param row CSVの1行（辞書形式: カラム名 -> 値）
        @return 解析に成功した場合はGpsPoint、失敗した場合はNone

        @details
          不正なデータ行は警告なくスキップされます。
          これにより、部分的に壊れたデータファイルでも
          有効な計測点だけを抽出できます。
        """
        try:
            lat = float(row.get("latitude", "").strip())
            lon = float(row.get("longitude", "").strip())

            # 高度は省略可能
            alt_str = row.get("altitude", "").strip()
            alt = float(alt_str) if alt_str else None

            # 速度は省略可能
            speed_str = row.get("speed", "").strip()
            speed = float(speed_str) if speed_str else None

            # タイムスタンプの解析
            ts_str = row.get("timestamp", "").strip()
            ts = self._parse_timestamp(ts_str) if ts_str else None

            return GpsPoint(
                latitude=lat,
                longitude=lon,
                altitude=alt,
                timestamp=ts,
                speed_kmh=speed,
            )
        except (ValueError, KeyError):
            return None

    def _parse_timestamp(self, ts_str: str) -> datetime | None:
        """タイムスタンプ文字列をdatetimeに変換します。

        @brief 複数の日時フォーマットに対応して解析を試みます。
        @param ts_str タイムスタンプ文字列（ISO 8601 形式）
        @return 解析されたdatetimeオブジェクト、解析失敗時はNone
        """
        for fmt in (self._CSV_DATETIME_FORMAT, self._CSV_DATETIME_FORMAT_MS):
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue
        return None

    # -----------------------------------------------------------------------
    # GPXパーサー (GPS Exchange Format)
    # -----------------------------------------------------------------------

    # GPX名前空間の定義（GPX 1.1標準）
    _GPX_NS = {"gpx": "http://www.topografix.com/GPX/1/1"}

    def parse_gpx(self, file_path: Union[str, Path]) -> GpsTrack:
        """GPXファイルからGPSデータを読み込みます。

        @brief 標準的なGPX (GPS Exchange Format) ファイルを解析し、
               GpsTrack を返します。
        @param file_path 読み込むGPXファイルのパス
        @return 解析済みのGpsTrackオブジェクト

        @details
          GPXファイルは <trk><trkseg><trkpt> 要素を含む標準XMLフォーマットです。
          各trkpt（トラックポイント）要素からlat/lon属性と、
          子要素の<ele>（高度）、<time>（時刻）を取得します。

        @raises FileNotFoundError ファイルが見つからない場合
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"GPXファイルが見つかりません: {file_path}")

        # XMLを安全に解析します。
        # Python 3.8+ の xml.etree.ElementTree はデフォルトで
        # 外部エンティティの自動読み込みを行わないため安全です。
        tree = ET.parse(file_path)  # noqa: S314
        root = tree.getroot()
        points: list[GpsPoint] = []

        # GPX名前空間あり/なし両方に対応
        trkpts = root.findall(".//gpx:trkpt", self._GPX_NS)
        if not trkpts:
            trkpts = root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt")
        if not trkpts:
            trkpts = root.findall(".//trkpt")

        for trkpt in trkpts:
            point = self._parse_gpx_trkpt(trkpt)
            if point is not None:
                points.append(point)

        return GpsTrack(
            points=points,
            name=file_path.stem,
            source="Insta360",
        )

    def _parse_gpx_trkpt(self, trkpt: ET.Element) -> GpsPoint | None:
        """GPXのtrkpt要素をGpsPointに変換します。

        @brief XMLのトラックポイント要素を解析してGpsPointを生成します。
        @param trkpt GPX XMLのtrkpt要素
        @return 解析に成功した場合はGpsPoint、失敗した場合はNone
        """
        try:
            lat = float(trkpt.get("lat", "0"))
            lon = float(trkpt.get("lon", "0"))

            # 高度（<ele>要素）の取得
            alt = None
            ele_elem = trkpt.find("gpx:ele", self._GPX_NS)
            if ele_elem is None:
                ele_elem = trkpt.find("{http://www.topografix.com/GPX/1/1}ele")
            if ele_elem is None:
                ele_elem = trkpt.find("ele")
            if ele_elem is not None and ele_elem.text:
                alt = float(ele_elem.text)

            # 時刻（<time>要素）の取得
            ts = None
            time_elem = trkpt.find("gpx:time", self._GPX_NS)
            if time_elem is None:
                time_elem = trkpt.find("{http://www.topografix.com/GPX/1/1}time")
            if time_elem is None:
                time_elem = trkpt.find("time")
            if time_elem is not None and time_elem.text:
                ts = self._parse_gpx_time(time_elem.text)

            return GpsPoint(latitude=lat, longitude=lon, altitude=alt, timestamp=ts)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_gpx_time(time_str: str) -> datetime | None:
        """GPXの時刻文字列をdatetimeに変換します。

        @brief ISO 8601 形式の時刻文字列をパースします。
        @param time_str 時刻文字列（例: "2024-01-15T10:30:00Z"）
        @return datetimeオブジェクト、解析失敗時はNone
        """
        # "Z" をUTC "+00:00" に置換して統一的に処理
        cleaned = time_str.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(cleaned)
        except ValueError:
            return None

    # -----------------------------------------------------------------------
    # ディレクトリスキャン
    # -----------------------------------------------------------------------

    def scan_directory(self, dir_path: Union[str, Path]) -> list[GpsTrack]:
        """ディレクトリ内のすべてのGPSデータファイルをスキャンして読み込みます。

        @brief 指定ディレクトリ内のCSV/GPXファイルを自動検出して解析します。
        @param dir_path スキャンするディレクトリのパス
        @return 検出された全走行軌跡のリスト

        @details
          F:\\work\\Camera01 のようなInsta360のデータフォルダを
          丸ごとスキャンして、含まれるすべてのGPSデータを読み込みます。
          対応する拡張子: .csv, .gpx
        """
        dir_path = Path(dir_path)
        tracks: list[GpsTrack] = []

        if not dir_path.is_dir():
            return tracks

        # CSVファイルの読み込み
        for csv_file in sorted(dir_path.glob("**/*.csv")):
            try:
                track = self.parse_csv(csv_file)
                if track.points:
                    tracks.append(track)
            except (FileNotFoundError, ValueError):
                continue

        # GPXファイルの読み込み
        for gpx_file in sorted(dir_path.glob("**/*.gpx")):
            try:
                track = self.parse_gpx(gpx_file)
                if track.points:
                    tracks.append(track)
            except (FileNotFoundError, ValueError):
                continue

        return tracks
