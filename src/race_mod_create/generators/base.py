"""Abstract base class for all simulator-specific MOD generators."""

from __future__ import annotations

import abc
import os
from pathlib import Path
from typing import Union

from race_mod_create.models.car import Car
from race_mod_create.models.track import Track


class BaseGenerator(abc.ABC):
    """Base class for race simulator MOD generators.

    Sub-classes must implement :meth:`generate_track` and
    :meth:`generate_car`.  Both methods write their output under
    *output_dir* and return the path to the root of the generated mod
    directory.
    """

    #: Human-readable simulator name, e.g. "Assetto Corsa".
    simulator_name: str = "Unknown"

    def __init__(self, output_dir: Union[str, Path] = ".") -> None:
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def generate_track(self, track: Track) -> Path:
        """Generate MOD files for *track*.

        Returns the root directory of the generated track mod.
        """

    @abc.abstractmethod
    def generate_car(self, car: Car) -> Path:
        """Generate MOD files for *car*.

        Returns the root directory of the generated car mod.
        """

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _ensure_dir(self, path: Path) -> Path:
        """Create *path* (and any parents) if it does not already exist."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _write_file(self, path: Path, content: str) -> None:
        """Write *content* to *path*, creating parent directories as needed."""
        self._ensure_dir(path.parent)
        path.write_text(content, encoding="utf-8")
