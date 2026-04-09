"""Track (circuit) data model."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class SurfaceType(str, Enum):
    """Road surface type."""

    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    GRAVEL = "gravel"
    DIRT = "dirt"
    GRASS = "grass"


@dataclass
class Sector:
    """A timed sector on the track."""

    name: str
    length_m: float  # metres


@dataclass
class Track:
    """Represents a racing circuit (course).

    Attributes:
        name:           Display name of the track.
        location:       City / country string (e.g. "Suzuka, Japan").
        length_m:       Total track length in metres.
        pit_boxes:      Number of pit-lane garage boxes.
        surface:        Primary road surface type.
        sectors:        Ordered list of timing sectors.
        description:    Optional free-text description.
        author:         Mod author name.
        version:        Mod version string (default "1.0").
    """

    name: str
    location: str
    length_m: float
    pit_boxes: int = 20
    surface: SurfaceType = SurfaceType.ASPHALT
    sectors: List[Sector] = field(default_factory=list)
    description: str = ""
    author: str = "Unknown"
    version: str = "1.0"

    def __post_init__(self) -> None:
        if self.length_m <= 0:
            raise ValueError("length_m must be a positive number.")
        if self.pit_boxes < 0:
            raise ValueError("pit_boxes must be a non-negative integer.")
        if not isinstance(self.surface, SurfaceType):
            self.surface = SurfaceType(self.surface)
