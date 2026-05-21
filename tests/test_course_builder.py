"""コースMODビルダーのテスト。

@file test_course_builder.py
@brief CircuitIdentifier、DataSynchronizer、CourseModBuilder の
       機能をテストします。
       大井松田カートランドのサンプルデータを検証データとして使用しています。
"""

from pathlib import Path

import pytest

from race_mod_create.alfano.data_parser import AlfanoDataParser
from race_mod_create.course.circuit_identifier import CircuitIdentifier, CircuitInfo
from race_mod_create.course.course_mod_builder import CourseModBuilder
from race_mod_create.course.sync import DataSynchronizer
from race_mod_create.insta360.gps_parser import Insta360GpsParser
from race_mod_create.models.gps_models import GpsTrack

# テストデータディレクトリのパス
TEST_DATA_DIR = Path(__file__).parent / "test_data"


# ---------------------------------------------------------------------------
# サーキット識別テスト
# ---------------------------------------------------------------------------


class TestCircuitIdentifier:
    """サーキット識別のテスト。"""

    def test_identify_oimatsuda_from_coordinates(self):
        """大井松田カートランドの座標からサーキットを識別できることを確認。"""
        identifier = CircuitIdentifier()
        result = identifier.identify_from_coordinates(35.3416, 139.1513)
        assert result is not None
        assert "大井松田" in result.name

    def test_identify_oimatsuda_from_gps_track(self):
        """GPSトラックから大井松田カートランドを識別できることを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        identifier = CircuitIdentifier()
        result = identifier.identify_from_gps_track(track)
        assert result is not None
        assert "大井松田" in result.name

    def test_identify_suzuka(self):
        """鈴鹿サーキットの座標からの識別を確認。"""
        identifier = CircuitIdentifier()
        result = identifier.identify_from_coordinates(34.8431, 136.5410)
        assert result is not None
        assert "鈴鹿" in result.name

    def test_identify_unknown_location(self):
        """未知の座標の場合にNoneが返されることを確認。"""
        identifier = CircuitIdentifier()
        # 太平洋上の座標
        result = identifier.identify_from_coordinates(0.0, 0.0)
        assert result is None

    def test_identify_empty_track(self):
        """空のGPSトラックでNoneが返されることを確認。"""
        identifier = CircuitIdentifier()
        result = identifier.identify_from_gps_track(GpsTrack())
        assert result is None

    def test_search_by_name_japanese(self):
        """日本語名でのサーキット検索を確認。"""
        identifier = CircuitIdentifier()
        results = identifier.search_by_name("大井松田")
        assert len(results) >= 1
        assert results[0].name == "大井松田カートランド"

    def test_search_by_name_english(self):
        """英語名でのサーキット検索を確認。"""
        identifier = CircuitIdentifier()
        results = identifier.search_by_name("Oimatsuda")
        assert len(results) >= 1

    def test_add_custom_circuit(self):
        """カスタムサーキットの追加を確認。"""
        identifier = CircuitIdentifier()
        initial_count = len(identifier.circuits)
        custom = CircuitInfo(
            name="テストサーキット",
            name_en="Test Circuit",
            location="東京, 日本",
            latitude=35.6762,
            longitude=139.6503,
            length_m=1000.0,
        )
        identifier.add_circuit(custom)
        assert len(identifier.circuits) == initial_count + 1

    def test_circuit_info_properties(self):
        """大井松田カートランドの情報が正しいことを確認。"""
        identifier = CircuitIdentifier()
        result = identifier.identify_from_coordinates(35.3416, 139.1513)
        assert result is not None
        assert result.length_m == pytest.approx(670.0)
        assert result.kart_circuit is True
        assert len(result.features) > 0


# ---------------------------------------------------------------------------
# データ同期テスト
# ---------------------------------------------------------------------------


class TestDataSynchronizer:
    """Insta360/Alfano データ同期テスト。"""

    def test_synchronize_gps_only(self):
        """GPSデータのみの同期が動作することを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        sync = DataSynchronizer()
        result = sync.synchronize_gps_only(track)
        assert len(result) == len(track.points)
        assert all(p.latitude is not None for p in result)

    def test_synchronize_with_alfano(self):
        """Insta360とAlfanoの同期が動作することを確認。"""
        insta360_parser = Insta360GpsParser()
        track = insta360_parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        alfano_parser = AlfanoDataParser()
        session = alfano_parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")

        sync = DataSynchronizer()
        result = sync.synchronize(track, session)
        assert len(result) == len(track.points)

    def test_synchronized_points_have_rpm(self):
        """同期済みポイントにRPMデータが含まれることを確認。"""
        insta360_parser = Insta360GpsParser()
        track = insta360_parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        alfano_parser = AlfanoDataParser()
        session = alfano_parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")

        sync = DataSynchronizer()
        result = sync.synchronize(track, session)
        rpm_points = [p for p in result if p.rpm is not None]
        assert len(rpm_points) > 0

    def test_synchronize_empty_track(self):
        """空のトラックでの同期が空リストを返すことを確認。"""
        sync = DataSynchronizer()
        result = sync.synchronize_gps_only(GpsTrack())
        assert result == []


# ---------------------------------------------------------------------------
# コースMODビルダーテスト
# ---------------------------------------------------------------------------


class TestCourseModBuilder:
    """コースMOD生成のテスト。"""

    def test_build_report_only(self, tmp_path):
        """レポートのみの生成が正常に動作することを確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        builder = CourseModBuilder(output_dir=tmp_path)
        result = builder.build_from_gps(insta360_track=track)
        assert result.exists()
        assert result.suffix == ".json"

    def test_build_with_alfano(self, tmp_path):
        """Alfanoデータ付きの生成が正常に動作することを確認。"""
        insta360_parser = Insta360GpsParser()
        track = insta360_parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        alfano_parser = AlfanoDataParser()
        session = alfano_parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")

        builder = CourseModBuilder(output_dir=tmp_path)
        result = builder.build_from_gps(
            insta360_track=track,
            alfano_session=session,
        )
        assert result.exists()

    def test_build_with_assetto_corsa(self, tmp_path):
        """Assetto Corsa MOD付きの生成を確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        builder = CourseModBuilder(output_dir=tmp_path)
        result = builder.build_from_gps(
            insta360_track=track,
            simulator="assetto_corsa",
        )
        assert result.exists()
        # Assetto Corsa のMODディレクトリも生成されているはず
        ac_dir = tmp_path / "content" / "tracks"
        assert ac_dir.exists()

    def test_build_with_rfactor(self, tmp_path):
        """rFactor MOD付きの生成を確認。"""
        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        builder = CourseModBuilder(output_dir=tmp_path)
        result = builder.build_from_gps(
            insta360_track=track,
            simulator="rfactor",
        )
        assert result.exists()
        # rFactor のMODディレクトリも生成されているはず
        rf_dir = tmp_path / "GameData" / "Locations"
        assert rf_dir.exists()

    def test_report_contains_circuit_info(self, tmp_path):
        """レポートにサーキット情報が含まれることを確認。"""
        import json

        parser = Insta360GpsParser()
        track = parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        builder = CourseModBuilder(output_dir=tmp_path)
        result = builder.build_from_gps(insta360_track=track)

        report = json.loads(result.read_text(encoding="utf-8"))
        assert "circuit" in report
        assert "大井松田" in report["circuit"]["name"]

    def test_report_contains_alfano_stats(self, tmp_path):
        """Alfanoデータ付きレポートにラップ統計が含まれることを確認。"""
        import json

        insta360_parser = Insta360GpsParser()
        track = insta360_parser.parse_csv(TEST_DATA_DIR / "sample_insta360_gps.csv")

        alfano_parser = AlfanoDataParser()
        session = alfano_parser.parse_csv(TEST_DATA_DIR / "sample_alfano.csv")

        builder = CourseModBuilder(output_dir=tmp_path)
        result = builder.build_from_gps(
            insta360_track=track,
            alfano_session=session,
        )

        report = json.loads(result.read_text(encoding="utf-8"))
        assert "alfano_data" in report
        assert report["alfano_data"]["lap_count"] == 2
