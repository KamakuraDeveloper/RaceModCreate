"""race_mod_create – レースシミュレーター用MODファイル生成ツール。

@brief サーキットや車両のMODファイルを各種シミュレーター向けに生成します。
       Insta360の360度カメラGPSデータやAlfanoラップタイマーデータからの
       コースMOD生成にも対応しています。
"""

from race_mod_create.models import (
    Car, CarClass, EngineSpec, Track, TyreSpec, Sector, SurfaceType,
    GpsPoint, GpsTrack,
)
from race_mod_create.generators import AssettoCorsaGenerator, RFactorGenerator
from race_mod_create.insta360 import Insta360GpsParser
from race_mod_create.alfano import AlfanoDataParser
from race_mod_create.course import (
    CircuitIdentifier, CircuitInfo, CourseModBuilder,
    DataSynchronizer, SynchronizedPoint,
)

__version__ = "1.0.0"

__all__ = [
    "__version__",
    # --- 既存モデル ---
    "Car",
    "CarClass",
    "EngineSpec",
    "Track",
    "TyreSpec",
    "Sector",
    "SurfaceType",
    # --- GPSモデル ---
    "GpsPoint",
    "GpsTrack",
    # --- ジェネレーター ---
    "AssettoCorsaGenerator",
    "RFactorGenerator",
    # --- Insta360/Alfano ---
    "Insta360GpsParser",
    "AlfanoDataParser",
    # --- コースMOD ---
    "CircuitIdentifier",
    "CircuitInfo",
    "CourseModBuilder",
    "DataSynchronizer",
    "SynchronizedPoint",
]
