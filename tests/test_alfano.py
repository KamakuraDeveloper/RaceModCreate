"""Alfanoデータパーサーのテスト。

@file test_alfano.py
@brief AlfanoDataParser のCSV読み込み機能と
       AlfanoSessionの集約機能をテストします。
       大井松田カートランドのサンプルデータを使用しています。
"""

from pathlib import Path

import pytest

from race_mod_create.alfano.data_parser import (
    AlfanoDataParser,
    AlfanoSession,
)

# テストデータディレクトリのパス
TEST_DATA_DIR = Path(__file__).parent / "test_data"


class TestAlfanoCsvParser:
    """Alfano CSV読み込みテスト。"""

    def test_parse_csv_returns_session(self):
        """CSVファイルからAlfanoSessionが返されることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        assert isinstance(session, AlfanoSession)

    def test_parse_csv_data_point_count(self):
        """正しい数のデータポイントが読み込まれることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        assert len(session.data_points) > 0

    def test_parse_csv_lap_count(self):
        """2ラップ分のデータが検出されることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        assert session.lap_count == 2

    def test_parse_csv_has_rpm(self):
        """RPMデータが読み込まれていることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        rpms = [dp.rpm for dp in session.data_points if dp.rpm is not None]
        assert len(rpms) > 0
        assert max(rpms) > 10000  # カートエンジンは高回転

    def test_parse_csv_has_speed(self):
        """速度データが読み込まれていることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        speeds = [dp.speed_kmh for dp in session.data_points if dp.speed_kmh is not None]
        assert len(speeds) > 0
        assert max(speeds) > 30  # カートは30km/h以上出る

    def test_parse_csv_has_temperature(self):
        """排気温度データが読み込まれていることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        temps = [dp.temp_c for dp in session.data_points if dp.temp_c is not None]
        assert len(temps) > 0
        assert all(30 < t < 100 for t in temps)  # 排気温度の妥当な範囲

    def test_parse_csv_has_gps(self):
        """GPS座標が読み込まれていることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        gps_points = [
            dp for dp in session.data_points
            if dp.latitude is not None and dp.longitude is not None
        ]
        assert len(gps_points) > 0

    def test_parse_csv_file_not_found(self):
        """存在しないファイルを指定した場合にFileNotFoundErrorが発生。"""
        parser = AlfanoDataParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_csv("/nonexistent/alfano_data.csv")


class TestLapSummary:
    """ラップ要約のテスト。"""

    def test_lap_summary_has_lap_time(self):
        """各ラップのラップタイムが正の値であることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        for lap in session.laps:
            assert lap.lap_time_s >= 0

    def test_lap_summary_has_max_rpm(self):
        """ラップ要約に最大RPMが含まれることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        for lap in session.laps:
            assert lap.max_rpm is not None
            assert lap.max_rpm > 0

    def test_best_lap_time(self):
        """ベストラップタイムが正しく取得されることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        best = session.best_lap_time_s
        assert best is not None
        assert best > 0


class TestAlfanoToGpsTrack:
    """AlfanoSessionからGpsTrackへの変換テスト。"""

    def test_to_gps_track_returns_track(self):
        """AlfanoSessionからGpsTrackが生成されることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        track = session.to_gps_track()
        assert len(track.points) > 0
        assert track.source == "Alfano"

    def test_to_gps_track_has_timestamps(self):
        """変換後のGpsPointにタイムスタンプがあることを確認。"""
        parser = AlfanoDataParser()
        session = parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")
        track = session.to_gps_track()
        assert all(p.timestamp is not None for p in track.points)
