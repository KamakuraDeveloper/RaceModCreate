"""Insta360 GPSパーサーのテスト。

@file test_insta360.py
@brief Insta360GpsParser の CSV/GPX 読み込み機能をテストします。
       大井松田カートランドのサンプルデータを検証データとして使用しています。
"""

from pathlib import Path

import pytest

from race_mod_create.insta360.gps_parser import Insta360GpsParser
from race_mod_create.models.gps_models import GpsPoint, GpsTrack

# テストデータディレクトリのパス
TEST_DATA_DIR = Path(__file__).parent / "test_data"


class TestInsta360CsvParser:
    """Insta360 CSV形式のGPSデータ解析テスト。"""

    def test_parse_csv_returns_gps_track(self):
        """CSVファイルを読み込んでGpsTrackが返されることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")
        assert isinstance(track, GpsTrack)
        assert track.source == "Insta360"

    def test_parse_csv_point_count(self):
        """サンプルCSVから正しい数の計測点が読み込まれることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")
        assert len(track.points) == 27

    def test_parse_csv_first_point_coordinates(self):
        """最初の計測点の緯度・経度が正しいことを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")
        first = track.points[0]
        assert first.latitude == pytest.approx(35.3416, abs=0.0001)
        assert first.longitude == pytest.approx(139.1513, abs=0.0001)

    def test_parse_csv_has_altitude(self):
        """高度データが正しく読み込まれることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")
        assert track.points[0].altitude == pytest.approx(120.5)

    def test_parse_csv_has_speed(self):
        """速度データが正しく読み込まれることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")
        assert track.points[0].speed_kmh == pytest.approx(0.0)
        assert track.points[1].speed_kmh == pytest.approx(12.5)

    def test_parse_csv_has_timestamps(self):
        """タイムスタンプが正しく解析されることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")
        assert track.points[0].timestamp is not None
        assert track.points[0].timestamp.hour == 10
        assert track.points[0].timestamp.minute == 30

    def test_parse_csv_total_distance(self):
        """走行距離が正の値であることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")
        dist = track.total_distance_m()
        assert dist > 0

    def test_parse_csv_file_not_found(self):
        """存在しないファイルを指定した場合にFileNotFoundErrorが発生。"""
        parser = Insta360GpsParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_csv("/nonexistent/file.csv")


class TestInsta360GpxParser:
    """Insta360 GPX形式のGPSデータ解析テスト。"""

    def test_parse_gpx_returns_gps_track(self):
        """GPXファイルを読み込んでGpsTrackが返されることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_gpx(TEST_DATA_DIR / "sample_insta360.gpx")
        assert isinstance(track, GpsTrack)
        assert track.source == "Insta360"

    def test_parse_gpx_point_count(self):
        """サンプルGPXから正しい数の計測点が読み込まれることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_gpx(TEST_DATA_DIR / "sample_insta360.gpx")
        assert len(track.points) == 11

    def test_parse_gpx_has_altitude(self):
        """GPXから高度が正しく取得されることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_gpx(TEST_DATA_DIR / "sample_insta360.gpx")
        assert track.points[0].altitude == pytest.approx(120.5)

    def test_parse_gpx_has_timestamps(self):
        """GPXからタイムスタンプが取得されることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_gpx(TEST_DATA_DIR / "sample_insta360.gpx")
        assert track.points[0].timestamp is not None

    def test_parse_gpx_file_not_found(self):
        """存在しないファイルを指定した場合にFileNotFoundErrorが発生。"""
        parser = Insta360GpsParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_gpx("/nonexistent/file.gpx")


class TestInsta360DirectoryScanner:
    """ディレクトリスキャンのテスト。"""

    def test_scan_directory(self):
        """テストデータディレクトリをスキャンして走行データが見つかることを確認。"""
        parser = Insta360GpsParser()
        tracks = parser.scan_directory(TEST_DATA_DIR)
        # CSVとGPXの両方が見つかるはず（Alfano CSVも含む可能性あり）
        assert len(tracks) >= 1

    def test_scan_nonexistent_directory(self):
        """存在しないディレクトリをスキャンしても空リストが返ることを確認。"""
        parser = Insta360GpsParser()
        tracks = parser.scan_directory("/nonexistent/directory")
        assert tracks == []


class TestGpsModels:
    """GpsPointとGpsTrackのモデルテスト。"""

    def test_gps_point_creation(self):
        """GpsPointが正しく作成されることを確認。"""
        point = GpsPoint(latitude=35.3416, longitude=139.1513)
        assert point.latitude == pytest.approx(35.3416)
        assert point.longitude == pytest.approx(139.1513)

    def test_gps_point_invalid_latitude(self):
        """不正な緯度でValueErrorが発生することを確認。"""
        with pytest.raises(ValueError, match="latitude"):
            GpsPoint(latitude=91.0, longitude=0.0)

    def test_gps_point_invalid_longitude(self):
        """不正な経度でValueErrorが発生することを確認。"""
        with pytest.raises(ValueError, match="longitude"):
            GpsPoint(latitude=0.0, longitude=181.0)

    def test_gps_point_distance(self):
        """2点間の距離が正しく計算されることを確認。"""
        # 大井松田カートランドの対角2点
        p1 = GpsPoint(latitude=35.3416, longitude=139.1513)
        p2 = GpsPoint(latitude=35.3420, longitude=139.1520)
        dist = p1.distance_to(p2)
        # 数十メートル程度であるはず
        assert 0 < dist < 200

    def test_gps_track_empty_distance(self):
        """空のトラックの距離が0であることを確認。"""
        track = GpsTrack()
        assert track.total_distance_m() == 0.0

    def test_gps_track_bounding_box_empty_raises(self):
        """空のトラックのバウンディングボックスでValueErrorが発生。"""
        track = GpsTrack()
        with pytest.raises(ValueError):
            track.bounding_box()

    def test_gps_track_center_point(self):
        """中心点が正しく計算されることを確認。"""
        track = GpsTrack(points=[
            GpsPoint(latitude=35.0, longitude=139.0),
            GpsPoint(latitude=36.0, longitude=140.0),
        ])
        center = track.center_point()
        assert center.latitude == pytest.approx(35.5)
        assert center.longitude == pytest.approx(139.5)
