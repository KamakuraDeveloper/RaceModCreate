"""course-from-gps CLIサブコマンドのテスト。

@file test_cli_course.py
@brief CLIのcourse-from-gpsコマンドが正しく動作することをテストします。
       大井松田カートランドのサンプルデータを使用しています。
"""

from pathlib import Path

from race_mod_create.cli import main

# テストデータディレクトリのパス
TEST_DATA_DIR = Path(__file__).parent / "test_data"


class TestCLICourseFromGps:
    """course-from-gps CLIコマンドのテスト。"""

    def test_csv_only(self, tmp_path):
        """CSVデータのみでのコースMOD生成を確認。"""
        exit_code = main([
            "course-from-gps",
            "--insta360-csv", str(TEST_DATA_DIR / "sample_insta360_gps.csv"),
            "--output", str(tmp_path),
        ])
        assert exit_code == 0
        report_dir = tmp_path / "course_report"
        assert report_dir.exists()
        reports = list(report_dir.glob("*.json"))
        assert len(reports) == 1

    def test_gpx_only(self, tmp_path):
        """GPXデータのみでのコースMOD生成を確認。"""
        exit_code = main([
            "course-from-gps",
            "--insta360-gpx", str(TEST_DATA_DIR / "sample_insta360.gpx"),
            "--output", str(tmp_path),
        ])
        assert exit_code == 0
        report_dir = tmp_path / "course_report"
        assert report_dir.exists()

    def test_csv_with_alfano(self, tmp_path):
        """CSVデータ + Alfanoデータでのコースモジュール生成を確認。"""
        exit_code = main([
            "course-from-gps",
            "--insta360-csv", str(TEST_DATA_DIR / "sample_insta360_gps.csv"),
            "--alfano-csv", str(TEST_DATA_DIR / "sample_alfano.csv"),
            "--output", str(tmp_path),
        ])
        assert exit_code == 0

    def test_with_assetto_corsa_simulator(self, tmp_path):
        """Assetto Corsa MOD生成付きのコマンドを確認。"""
        exit_code = main([
            "course-from-gps",
            "--insta360-csv", str(TEST_DATA_DIR / "sample_insta360_gps.csv"),
            "--simulator", "assetto_corsa",
            "--output", str(tmp_path),
        ])
        assert exit_code == 0
        # Assetto Corsa MODが生成されていることを確認
        ac_dir = tmp_path / "content" / "tracks"
        assert ac_dir.exists()

    def test_with_rfactor_simulator(self, tmp_path):
        """rFactor MOD生成付きのコマンドを確認。"""
        exit_code = main([
            "course-from-gps",
            "--insta360-csv", str(TEST_DATA_DIR / "sample_insta360_gps.csv"),
            "--simulator", "rfactor",
            "--output", str(tmp_path),
        ])
        assert exit_code == 0
        rf_dir = tmp_path / "GameData" / "Locations"
        assert rf_dir.exists()

    def test_no_insta360_data_returns_error(self, tmp_path):
        """Insta360データ未指定時にエラーコード1が返されることを確認。"""
        exit_code = main([
            "course-from-gps",
            "--output", str(tmp_path),
        ])
        assert exit_code == 1
