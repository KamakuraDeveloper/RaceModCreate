"""Racing car data model."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class CarClass(str, Enum):
    """Broad racing car class."""

    GT3 = "GT3"
    GT4 = "GT4"
    LMP1 = "LMP1"
    LMP2 = "LMP2"
    FORMULA = "Formula"
    TOURING = "Touring"
    RALLY = "Rally"
    OPEN_WHEEL = "OpenWheel"
    KART = "Kart"


@dataclass
class EngineSpec:
    """Engine specifications.

    Attributes:
        displacement_cc:    Engine displacement in cubic centimetres.
        cylinders:          Number of cylinders.
        max_power_kw:       Maximum power output in kilowatts.
        max_torque_nm:      Maximum torque in Newton-metres.
        max_rpm:            Maximum engine RPM.
        naturally_aspirated: True if naturally aspirated, False if forced induction.
    """

    displacement_cc: float
    cylinders: int
    max_power_kw: float
    max_torque_nm: float
    max_rpm: int
    naturally_aspirated: bool = True

    def __post_init__(self) -> None:
        if self.displacement_cc <= 0:
            raise ValueError("displacement_cc must be positive.")
        if self.cylinders <= 0:
            raise ValueError("cylinders must be positive.")
        if self.max_power_kw <= 0:
            raise ValueError("max_power_kw must be positive.")
        if self.max_torque_nm <= 0:
            raise ValueError("max_torque_nm must be positive.")
        if self.max_rpm <= 0:
            raise ValueError("max_rpm must be positive.")


@dataclass
class TyreSpec:
    """Tyre specification.

    Attributes:
        compound:           Compound name (e.g. "Soft", "Medium", "Hard").
        width_mm:           Tyre width in millimetres.
        aspect_ratio:       Aspect ratio as a percentage (e.g. 50 for 50%).
        rim_diameter_inch:  Rim diameter in inches.
    """

    compound: str
    width_mm: int
    aspect_ratio: int
    rim_diameter_inch: int

    def __post_init__(self) -> None:
        if self.width_mm <= 0:
            raise ValueError("width_mm must be positive.")
        if not (0 < self.aspect_ratio <= 100):
            raise ValueError("aspect_ratio must be between 1 and 100.")
        if self.rim_diameter_inch <= 0:
            raise ValueError("rim_diameter_inch must be positive.")


@dataclass
class Car:
    """Represents a racing car.

    Attributes:
        name:           Display name / model name.
        manufacturer:   Manufacturer name.
        car_class:      Racing class.
        year:           Model year.
        engine:         Engine specification.
        mass_kg:        Total vehicle mass in kilograms.
        tyres:          Available tyre compounds (front and rear combined list).
        wheelbase_mm:   Wheelbase in millimetres (optional).
        front_track_mm: Front axle track width in millimetres (optional).
        rear_track_mm:  Rear axle track width in millimetres (optional).
        fuel_capacity_l: Fuel tank capacity in litres (optional).
        description:    Optional free-text description.
        author:         Mod author name.
        version:        Mod version string (default "1.0").
    """

    name: str
    manufacturer: str
    car_class: CarClass
    year: int
    engine: EngineSpec
    mass_kg: float
    tyres: List[TyreSpec] = field(default_factory=list)
    wheelbase_mm: float = 0.0
    front_track_mm: float = 0.0
    rear_track_mm: float = 0.0
    fuel_capacity_l: float = 0.0
    description: str = ""
    author: str = "Unknown"
    version: str = "1.0"

    def __post_init__(self) -> None:
        if self.mass_kg <= 0:
            raise ValueError("mass_kg must be positive.")
        if not isinstance(self.car_class, CarClass):
            self.car_class = CarClass(self.car_class)
