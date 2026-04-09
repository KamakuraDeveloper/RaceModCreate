"""Alfanoラップタイマーのデータ解析モジュール。

Alfanoデバイスからエクスポートされた走行データ（ラップタイム、RPM、速度など）を
解析するためのモジュールです。
"""

from race_mod_create.alfano.data_parser import AlfanoDataParser

__all__ = [
    "AlfanoDataParser",
]
