"""Insta360 GPSデータとAlfanoデータの同期モジュール。

@file sync.py
@brief Insta360の360度カメラGPSデータとAlfanoラップタイマーのテレメトリデータを
       タイムスタンプベースで同期し、統合データを生成します。

@details
  Insta360とAlfanoは別々のデバイスでデータを記録するため、
  タイムスタンプにずれが生じます。
  このモジュールでは以下の手順でデータを同期します:

    1. 両方のGPSトラックの開始時刻を基準にオフセットを計算
    2. Insta360の各GPS計測点に対して、最も近い時刻のAlfanoデータを紐付け
    3. 統合された SynchronizedPoint のリストを生成

  使い方::

    from race_mod_create.course import DataSynchronizer
    sync = DataSynchronizer()
    result = sync.synchronize(insta360_track, alfano_track)
    for point in result:
        print(f"位置: ({point.latitude}, {point.longitude})")
        print(f"速度: {point.speed_kmh}, RPM: {point.rpm}")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from race_mod_create.alfano.data_parser import AlfanoDataPoint, AlfanoSession
from race_mod_create.models.gps_models import GpsTrack


@dataclass
class SynchronizedPoint:
    """同期済みの統合データポイント。

    @brief Insta360 GPSデータとAlfanoテレメトリデータを統合した1計測点です。

    @param latitude        緯度（Insta360 GPSから取得）
    @param longitude       経度（Insta360 GPSから取得）
    @param altitude        高度（メートル、Insta360 GPSから取得、任意）
    @param speed_kmh       速度（km/h、Alfanoデータ優先、任意）
    @param rpm             エンジン回転数（Alfanoデータから取得、任意）
    @param temp_c          排気温度（℃、Alfanoデータから取得、任意）
    @param lap_number      ラップ番号（Alfanoデータから取得、任意）
    @param time_offset_s   走行開始からの経過時間（秒）
    """

    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed_kmh: Optional[float] = None
    rpm: Optional[int] = None
    temp_c: Optional[float] = None
    lap_number: Optional[int] = None
    time_offset_s: float = 0.0


class DataSynchronizer:
    """Insta360とAlfanoのデータを同期するクラス。

    @brief 時間軸に基づいてInsta360 GPSデータとAlfanoテレメトリデータを
           マッチングし、統合データを生成します。

    @details
      同期の基本アルゴリズム:
        - Insta360 GPSの各タイムスタンプに対して
        - Alfanoデータ内で時間的に最も近いデータポイントを探索
        - 2つのデータを結合してSynchronizedPointを生成

      時間オフセットの補正:
        - 2つのデバイスの時計のずれを補正するため、
          手動でオフセット秒数を指定することも可能です
    """

    # 同期許容範囲（秒） — この時間差以内のデータをマッチング対象とする
    DEFAULT_TOLERANCE_S = 1.0

    def __init__(self, tolerance_s: float = DEFAULT_TOLERANCE_S) -> None:
        """DataSynchronizerを初期化します。

        @brief 同期の許容時間差を設定します。
        @param tolerance_s 同期許容範囲（秒、デフォルト: 1.0秒）
        """
        self._tolerance_s = tolerance_s

    def synchronize(
        self,
        insta360_track: GpsTrack,
        alfano_session: AlfanoSession,
        time_offset_s: float = 0.0,
    ) -> List[SynchronizedPoint]:
        """Insta360 GPSデータとAlfanoデータを同期します。

        @brief 2つのデータソースをタイムスタンプベースで統合します。
        @param insta360_track  Insta360から取得したGPSトラック
        @param alfano_session  Alfanoから取得した走行セッションデータ
        @param time_offset_s   Alfano側のタイムスタンプに加算するオフセット（秒）。
                               Insta360の方が先にスタートした場合は正の値を指定。
        @return 同期済みデータポイントのリスト

        @details
          同期アルゴリズムの手順:
            1. Insta360 GPSの開始時刻を基準時刻（t=0）とする
            2. 各Insta360 GPS点の経過時間を計算
            3. Alfanoデータの各ポイントにオフセットを適用
            4. 最近傍探索で最も近い時刻のAlfanoデータをマッチング
            5. 許容範囲内であれば統合データポイントを生成
        """
        if not insta360_track.points:
            return []

        # Insta360の基準時刻
        base_time = insta360_track.points[0].timestamp

        results: list[SynchronizedPoint] = []

        for gps_point in insta360_track.points:
            # 経過時間の計算
            if base_time is not None and gps_point.timestamp is not None:
                elapsed_s = (gps_point.timestamp - base_time).total_seconds()
            else:
                elapsed_s = 0.0

            # Alfanoデータとのマッチング
            matched_alfano = self._find_nearest_alfano_point(
                elapsed_s, alfano_session.data_points, time_offset_s
            )

            # 統合データポイントの生成
            sync_point = SynchronizedPoint(
                latitude=gps_point.latitude,
                longitude=gps_point.longitude,
                altitude=gps_point.altitude,
                time_offset_s=elapsed_s,
            )

            # Alfanoデータがマッチした場合、テレメトリ情報を追加
            if matched_alfano is not None:
                sync_point.speed_kmh = matched_alfano.speed_kmh or gps_point.speed_kmh
                sync_point.rpm = matched_alfano.rpm
                sync_point.temp_c = matched_alfano.temp_c
                sync_point.lap_number = matched_alfano.lap_number
            else:
                # Alfanoデータがない場合はGPSの速度情報を使用
                sync_point.speed_kmh = gps_point.speed_kmh

            results.append(sync_point)

        return results

    def synchronize_gps_only(self, gps_track: GpsTrack) -> List[SynchronizedPoint]:
        """GPSデータのみからSynchronizedPointリストを生成します。

        @brief Alfanoデータが無い場合に、GPSデータのみから統合データ形式を作成します。
        @param gps_track GPSトラック
        @return SynchronizedPointのリスト

        @details
          Alfanoデータがオプションの場合に使用します。
          GPSデータに含まれる速度情報のみが利用されます。
        """
        if not gps_track.points:
            return []

        base_time = gps_track.points[0].timestamp

        results: list[SynchronizedPoint] = []
        for point in gps_track.points:
            if base_time is not None and point.timestamp is not None:
                elapsed_s = (point.timestamp - base_time).total_seconds()
            else:
                elapsed_s = 0.0

            results.append(
                SynchronizedPoint(
                    latitude=point.latitude,
                    longitude=point.longitude,
                    altitude=point.altitude,
                    speed_kmh=point.speed_kmh,
                    time_offset_s=elapsed_s,
                )
            )

        return results

    def _find_nearest_alfano_point(
        self,
        target_time_s: float,
        alfano_points: list[AlfanoDataPoint],
        time_offset_s: float,
    ) -> AlfanoDataPoint | None:
        """指定時刻に最も近いAlfanoデータポイントを検索します。

        @brief 二分探索の代わりに線形探索で最近傍のデータポイントを見つけます。
        @param target_time_s  探索対象の経過時間（秒）
        @param alfano_points  Alfanoデータポイントのリスト
        @param time_offset_s  タイムオフセット補正値（秒）
        @return 許容範囲内で最も近いAlfanoDataPoint、なければNone

        @details
          将来的にはデータ量が大きい場合に二分探索に切り替えることを検討してください。
        """
        if not alfano_points:
            return None

        best_point: AlfanoDataPoint | None = None
        best_diff = float("inf")

        for ap in alfano_points:
            adjusted_time = ap.time_s + time_offset_s
            diff = abs(adjusted_time - target_time_s)
            if diff < best_diff:
                best_diff = diff
                best_point = ap

        if best_diff <= self._tolerance_s:
            return best_point

        return None
