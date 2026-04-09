"""GPS位置データモデル。

@file gps_models.py
@brief GPS座標とトラック（走行軌跡）を表現するデータモデルを定義します。

Insta360カメラやAlfanoラップタイマーから取得したGPSデータを
統一的に扱うためのデータクラスを提供します。

@details
  - GpsPoint: 単一のGPS計測点（緯度・経度・高度・時刻）
  - GpsTrack: 複数のGpsPointからなる走行軌跡
  - ここで定義するモデルは、Insta360パーサーとAlfanoパーサーの両方から使用されます。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ---------------------------------------------------------------------------
# 地球の平均半径（メートル単位） — Haversine公式で距離計算に使用
# ---------------------------------------------------------------------------
EARTH_RADIUS_M = 6_371_000.0


@dataclass
class GpsPoint:
    """単一のGPS計測点を表すデータクラス。

    @brief 緯度・経度・高度・タイムスタンプを保持します。

    @param latitude   緯度（度数法、-90.0 〜 +90.0）
    @param longitude  経度（度数法、-180.0 〜 +180.0）
    @param altitude   高度（メートル単位、任意）
    @param timestamp  計測時刻（datetime型、任意）
    @param speed_kmh  計測時の速度（km/h、任意 — Alfanoデータ等で利用）
    """

    latitude: float
    longitude: float
    altitude: Optional[float] = None
    timestamp: Optional[datetime] = None
    speed_kmh: Optional[float] = None

    def __post_init__(self) -> None:
        """入力値のバリデーションを行います。

        @brief 緯度が -90〜+90、経度が -180〜+180 の範囲にあるかを検証します。
        @raises ValueError 緯度または経度が範囲外の場合
        """
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError(
                f"latitude は -90.0 から 90.0 の範囲でなければなりません（入力値: {self.latitude}）"
            )
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError(
                f"longitude は -180.0 から 180.0 の範囲でなければなりません（入力値: {self.longitude}）"
            )

    def distance_to(self, other: GpsPoint) -> float:
        """Haversine公式で2点間の距離（メートル）を計算します。

        @brief 地球を球体とみなし、2つのGPS座標間の大圏距離を求めます。
        @param other 距離を計算する相手のGpsPoint
        @return 2点間の距離（メートル）

        @details
          Haversine公式:
            a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
            c = 2 * atan2(√a, √(1-a))
            距離 = 地球半径 * c
        """
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        dlat = math.radians(other.latitude - self.latitude)
        dlon = math.radians(other.longitude - self.longitude)

        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return EARTH_RADIUS_M * c


@dataclass
class GpsTrack:
    """GPS計測点の列からなる走行軌跡を表すデータクラス。

    @brief 複数のGpsPointをまとめて管理し、走行データの集約情報を提供します。

    @param points  GPS計測点のリスト（時系列順）
    @param name    走行軌跡の名前（ファイル名やセッション名など、任意）
    @param source  データの取得元（例: "Insta360", "Alfano"）
    """

    points: List[GpsPoint] = field(default_factory=list)
    name: str = ""
    source: str = ""

    def total_distance_m(self) -> float:
        """走行軌跡の総距離（メートル）を計算します。

        @brief 隣接する計測点間の距離を合計し、走行全体の距離を返します。
        @return 走行軌跡の総距離（メートル単位）
        """
        if len(self.points) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(self.points)):
            total += self.points[i - 1].distance_to(self.points[i])
        return total

    def bounding_box(self) -> tuple[float, float, float, float]:
        """走行軌跡を囲む最小の矩形（バウンディングボックス）を返します。

        @brief 全GPS計測点の最小/最大の緯度・経度を求めます。
        @return (最小緯度, 最小経度, 最大緯度, 最大経度) のタプル
        @raises ValueError 計測点がゼロ件の場合
        """
        if not self.points:
            raise ValueError("バウンディングボックスを計算するには1つ以上の計測点が必要です。")
        lats = [p.latitude for p in self.points]
        lons = [p.longitude for p in self.points]
        return (min(lats), min(lons), max(lats), max(lons))

    def center_point(self) -> GpsPoint:
        """走行軌跡の中心点（重心）を計算します。

        @brief 全GPS計測点の緯度・経度の算術平均を取り、中心座標とします。
        @return 中心座標のGpsPoint
        @raises ValueError 計測点がゼロ件の場合
        """
        if not self.points:
            raise ValueError("中心点を計算するには1つ以上の計測点が必要です。")
        avg_lat = sum(p.latitude for p in self.points) / len(self.points)
        avg_lon = sum(p.longitude for p in self.points) / len(self.points)
        return GpsPoint(latitude=avg_lat, longitude=avg_lon)

    def duration_seconds(self) -> Optional[float]:
        """走行の所要時間（秒）を返します。

        @brief 最初と最後の計測点のタイムスタンプ差から算出します。
        @return 所要時間（秒）、タイムスタンプが存在しない場合はNone
        """
        if (
            len(self.points) < 2
            or self.points[0].timestamp is None
            or self.points[-1].timestamp is None
        ):
            return None
        delta = self.points[-1].timestamp - self.points[0].timestamp
        return delta.total_seconds()
