"""Insta360カメラのGPSデータ解析モジュール。

Insta360の360度カメラで撮影されたサーキット走行データから、
GPSの位置情報を抽出・解析するためのモジュールです。
"""

from race_mod_create.insta360.gps_parser import Insta360GpsParser

__all__ = [
    "Insta360GpsParser",
]
