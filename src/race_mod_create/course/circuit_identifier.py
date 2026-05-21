"""サーキット（コース）識別モジュール。

@file circuit_identifier.py
@brief GPS座標からサーキットの名前やコース特徴を検索・識別するモジュールです。

@details
  既知のサーキットデータベースとGPS走行データを照合し、
  走行したサーキットを自動的に特定します。

  識別アルゴリズム:
    1. GPSトラックの中心座標を計算
    2. 既知サーキットデータベース内の各サーキット中心座標との距離を計算
    3. 設定した閾値（デフォルト: 2km）以内の最も近いサーキットを返す

  現在、以下の日本のカートサーキットがデータベースに登録されています:
    - 大井松田カートランド（神奈川県）
    - フェスティカサーキット栃木（栃木県）
    - 新東京サーキット（千葉県）
    - 本庄サーキット（埼玉県）
    - 幸田サーキット（愛知県）
    - 鈴鹿サーキット（三重県）
    - もてぎ（栃木県）

  使い方::

    from race_mod_create.course import CircuitIdentifier
    identifier = CircuitIdentifier()
    info = identifier.identify_from_gps_track(gps_track)
    if info:
        print(f"サーキット名: {info.name}")
        print(f"コース長: {info.length_m}m")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from race_mod_create.models.gps_models import GpsPoint, GpsTrack


@dataclass
class CircuitInfo:
    """サーキットの情報を格納するデータクラス。

    @brief サーキットの名前、所在地、コース特徴などの情報を保持します。

    @param name             サーキット名
    @param name_en          サーキット名（英語）
    @param location         所在地（例: "神奈川県, 日本"）
    @param latitude         サーキット中心の緯度
    @param longitude        サーキット中心の経度
    @param length_m         コース全長（メートル）
    @param surface          路面タイプ（例: "asphalt"）
    @param description      コースの説明
    @param features         コースの特徴リスト（例: ["テクニカル", "高速S字"]）
    @param pit_boxes        ピットボックス数
    @param kart_circuit     カートサーキットかどうか
    """

    name: str
    name_en: str
    location: str
    latitude: float
    longitude: float
    length_m: float
    surface: str = "asphalt"
    description: str = ""
    features: List[str] = field(default_factory=list)
    pit_boxes: int = 20
    kart_circuit: bool = False


# ---------------------------------------------------------------------------
# 既知のサーキットデータベース
# ---------------------------------------------------------------------------
# 日本国内の主要サーキットを登録しています。
# 大井松田カートランドのデータを検証用として使用します。
# ---------------------------------------------------------------------------

KNOWN_CIRCUITS: list[CircuitInfo] = [
    CircuitInfo(
        name="大井松田カートランド",
        name_en="Oimatsuda Kartland",
        location="神奈川県足柄上郡, 日本",
        latitude=35.3416,
        longitude=139.1513,
        length_m=670.0,
        surface="asphalt",
        description="神奈川県足柄上郡大井町にあるカートサーキット。"
        "テクニカルなレイアウトで、初心者から上級者まで楽しめるコースです。",
        features=[
            "テクニカルコース",
            "タイトなヘアピン",
            "高速S字カーブ",
            "初心者〜上級者向け",
        ],
        pit_boxes=15,
        kart_circuit=True,
    ),
    CircuitInfo(
        name="フェスティカサーキット栃木",
        name_en="Festika Circuit Tochigi",
        location="栃木県佐野市, 日本",
        latitude=36.3094,
        longitude=139.5875,
        length_m=780.0,
        surface="asphalt",
        description="栃木県佐野市にあるカートサーキット。"
        "高低差のあるテクニカルコースで、全日本カート選手権の開催実績があります。",
        features=[
            "高低差あり",
            "テクニカル",
            "全日本選手権開催",
        ],
        pit_boxes=20,
        kart_circuit=True,
    ),
    CircuitInfo(
        name="新東京サーキット",
        name_en="Shin-Tokyo Circuit",
        location="千葉県市原市, 日本",
        latitude=35.4533,
        longitude=140.1000,
        length_m=1003.0,
        surface="asphalt",
        description="千葉県市原市にあるカート専用サーキット。"
        "長いストレートとテクニカルセクションが特徴です。",
        features=[
            "長いストレート",
            "テクニカルセクション",
            "全日本選手権開催",
        ],
        pit_boxes=30,
        kart_circuit=True,
    ),
    CircuitInfo(
        name="本庄サーキット",
        name_en="Honjo Circuit",
        location="埼玉県本庄市, 日本",
        latitude=36.2236,
        longitude=139.1892,
        length_m=550.0,
        surface="asphalt",
        description="埼玉県本庄市にあるコンパクトなカートサーキット。",
        features=[
            "コンパクトレイアウト",
            "初心者向け",
        ],
        pit_boxes=12,
        kart_circuit=True,
    ),
    CircuitInfo(
        name="幸田サーキット",
        name_en="Kota Circuit",
        location="愛知県額田郡幸田町, 日本",
        latitude=34.8603,
        longitude=137.1650,
        length_m=700.0,
        surface="asphalt",
        description="愛知県幸田町にあるカートサーキット。"
        "中部地方のカートレースの拠点です。",
        features=[
            "中部地方の拠点",
            "バランスの良いレイアウト",
        ],
        pit_boxes=18,
        kart_circuit=True,
    ),
    CircuitInfo(
        name="鈴鹿サーキット",
        name_en="Suzuka Circuit",
        location="三重県鈴鹿市, 日本",
        latitude=34.8431,
        longitude=136.5410,
        length_m=5807.0,
        surface="asphalt",
        description="三重県鈴鹿市にある国際サーキット。"
        "F1日本グランプリの開催地として世界的に有名です。",
        features=[
            "国際サーキット",
            "8の字レイアウト",
            "130R",
            "シケイン",
            "スプーンカーブ",
            "デグナーカーブ",
        ],
        pit_boxes=56,
        kart_circuit=False,
    ),
    CircuitInfo(
        name="モビリティリゾートもてぎ",
        name_en="Mobility Resort Motegi",
        location="栃木県茂木町, 日本",
        latitude=36.5322,
        longitude=140.2281,
        length_m=4801.0,
        surface="asphalt",
        description="栃木県茂木町にある国際サーキット。"
        "MotoGP日本グランプリの開催地です。",
        features=[
            "国際サーキット",
            "ストップ＆ゴー",
            "90度コーナー",
            "ヘアピン",
        ],
        pit_boxes=50,
        kart_circuit=False,
    ),
]


class CircuitIdentifier:
    """GPSデータからサーキットを識別するクラス。

    @brief GPS走行軌跡データから、走行したサーキットを自動的に特定します。

    @details
      既知のサーキットデータベースとGPS座標を照合して、
      閾値距離以内で最も近いサーキットを返します。
      カスタムサーキットの追加も可能です。
    """

    # 識別閾値（メートル） — サーキット中心からこの距離以内なら一致とみなす
    DEFAULT_THRESHOLD_M = 2000.0

    def __init__(
        self,
        circuits: list[CircuitInfo] | None = None,
        threshold_m: float = DEFAULT_THRESHOLD_M,
    ) -> None:
        """CircuitIdentifierを初期化します。

        @brief 既知のサーキットリストと識別閾値を設定します。
        @param circuits カスタムサーキットリスト（Noneの場合は内蔵データベースを使用）
        @param threshold_m 識別閾値（メートル、デフォルト: 2000m）
        """
        self._circuits = circuits if circuits is not None else list(KNOWN_CIRCUITS)
        self._threshold_m = threshold_m

    @property
    def circuits(self) -> list[CircuitInfo]:
        """登録されているサーキットのリストを返します。

        @return サーキット情報のリスト
        """
        return self._circuits

    def add_circuit(self, circuit: CircuitInfo) -> None:
        """サーキットをデータベースに追加します。

        @brief カスタムサーキットを登録します。
        @param circuit 追加するサーキット情報
        """
        self._circuits.append(circuit)

    def identify_from_gps_track(self, track: GpsTrack) -> Optional[CircuitInfo]:
        """GPSトラックからサーキットを識別します。

        @brief GPS走行軌跡の中心座標と既知サーキットの座標を照合し、
               最も近いサーキットを返します。
        @param track GPS走行軌跡データ
        @return 識別されたサーキット情報、見つからない場合はNone

        @details
          アルゴリズム:
            1. GPSトラックの中心点（重心）を算出
            2. 全既知サーキットとの距離を計算
            3. 閾値以内で最も近いサーキットを返却
        """
        if not track.points:
            return None

        center = track.center_point()
        return self.identify_from_coordinates(center.latitude, center.longitude)

    def identify_from_coordinates(
        self, latitude: float, longitude: float
    ) -> Optional[CircuitInfo]:
        """GPS座標からサーキットを識別します。

        @brief 指定された緯度・経度に最も近い既知のサーキットを返します。
        @param latitude 緯度
        @param longitude 経度
        @return 識別されたサーキット情報、見つからない場合はNone
        """
        ref_point = GpsPoint(latitude=latitude, longitude=longitude)

        best_circuit: Optional[CircuitInfo] = None
        best_distance = float("inf")

        for circuit in self._circuits:
            circuit_point = GpsPoint(
                latitude=circuit.latitude,
                longitude=circuit.longitude,
            )
            dist = ref_point.distance_to(circuit_point)
            if dist < best_distance and dist <= self._threshold_m:
                best_distance = dist
                best_circuit = circuit

        return best_circuit

    def search_by_name(self, keyword: str) -> list[CircuitInfo]:
        """サーキット名でキーワード検索します。

        @brief サーキット名（日本語・英語）に部分一致するサーキットを検索します。
        @param keyword 検索キーワード
        @return 一致したサーキットのリスト
        """
        keyword_lower = keyword.lower()
        results: list[CircuitInfo] = []
        for circuit in self._circuits:
            if (
                keyword_lower in circuit.name.lower()
                or keyword_lower in circuit.name_en.lower()
            ):
                results.append(circuit)
        return results
