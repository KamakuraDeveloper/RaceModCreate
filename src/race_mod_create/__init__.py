"""race_mod_create – Generate race simulator MOD files."""

from race_mod_create.models import Car, CarClass, EngineSpec, Track, TyreSpec, Sector, SurfaceType
from race_mod_create.generators import AssettoCorsaGenerator, RFactorGenerator
from race_mod_create.presets import JKT_KANTO_CIRCUITS, JKT_KIDS_CIRCUITS, get_preset, list_presets

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "Car",
    "CarClass",
    "EngineSpec",
    "Track",
    "TyreSpec",
    "Sector",
    "SurfaceType",
    "AssettoCorsaGenerator",
    "RFactorGenerator",
    "JKT_KANTO_CIRCUITS",
    "JKT_KIDS_CIRCUITS",
    "get_preset",
    "list_presets",
]
