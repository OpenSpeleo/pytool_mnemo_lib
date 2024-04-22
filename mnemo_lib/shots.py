#!/usr/bin/env python

import dataclasses
from typing import Optional

from mnemo_lib.types import ShotType


@dataclasses.dataclass
class Shot(object):
    type: ShotType
    head_in: float
    head_out: float
    length: float
    depth_in: float
    depth_out: float
    pitch_in: float
    pitch_out: float
    marker_idx: int

    # fileVersion >= 4
    left: Optional[int] = None
    right: Optional[int] = None
    up: Optional[int] = None
    down: Optional[int] = None

    # File Version >= 3
    temperature: Optional[int] = 0

    # File Version >= 3
    hours: Optional[int] = 0
    minutes: Optional[int] = 0
    seconds: Optional[int] = 0

    # Magic Values, version >= 5
    shotStartValueA = 57
    shotStartValueB = 67
    shotStartValueC = 77

    shotEndValueA = 95
    shotEndValueB = 25
    shotEndValueC = 35

    @property
    def buff_len(self):
        return self._cursor

    def __getitem__(self, idx: int) -> int:
        return self._bytearray[idx]

    def _read_next_item(self):
        data = self[self._cursor]
        self._cursor += 1
        return data

    def _read_next_Int16BE(self) -> float:
        lsb = self._read_next_item()
        msb = self._read_next_item()

        if msb < 0:
            msb = 2**8 + msb

        return lsb * 2 ** 8 + msb

    @property
    def version(self):
        return self._version

    @staticmethod
    def validate_magic(val, ref):
        if val != ref:
            raise AssertionError(
                f"Magic Number Error: Expected `{ref}`, Received: `{val}`"
            )

    def __init__(self, version, buff):
        self._version = version
        self._bytearray = buff
        self._cursor = 0

        if self.version >=5:
            self.validate_magic(self._read_next_item(), self.shotStartValueA)
            self.validate_magic(self._read_next_item(), self.shotStartValueB)
            self.validate_magic(self._read_next_item(), self.shotStartValueC)

        self.type = ShotType(self._read_next_item())

        self.head_in = self._read_next_Int16BE() / 10.0
        self.head_out = self._read_next_Int16BE() / 10.0
        self.length = self._read_next_Int16BE() / 100.0
        self.depth_in = self._read_next_Int16BE() / 100.0
        self.depth_out = self._read_next_Int16BE() / 100.0
        self.pitch_in = self._read_next_Int16BE() / 10.0
        self.pitch_out = self._read_next_Int16BE() / 10.0

        if version >= 4:
            self.left = self._read_next_Int16BE() / 100.0
            self.right = self._read_next_Int16BE() / 100.0
            self.up = self._read_next_Int16BE() / 100.0
            self.down = self._read_next_Int16BE() / 100.0

        if version >= 3:
            self.temperature = self._read_next_Int16BE() / 10.0
            self.hours = int(self._read_next_item())
            self.minutes = int(self._read_next_item())
            self.seconds = int(self._read_next_item())

        self.marker_idx = self._read_next_item()

        if self.version >=5:
            self.validate_magic(self._read_next_item(), self.shotEndValueA)
            self.validate_magic(self._read_next_item(), self.shotEndValueB)
            self.validate_magic(self._read_next_item(), self.shotEndValueC)

    def asdict(self):
        return dataclasses.asdict(self)

    def __repr__(self):
        attrs = [
            f"type: {self.type.name}",
            f"head_in: {self.head_in:5.1f}",
            f"head_out: {self.head_out:5.1f}",
            f"length: {self.length:6.2f}",
            f"depth_in: {self.depth_in:6.2f}",
            f"depth_out: {self.depth_out:6.2f}",
            f"pitch_in: {self.pitch_in:5.1f}",
            f"pitch_out: {self.pitch_out:5.1f}",
            f"marker_idx: {self.marker_idx:3d}",
        ]

        if self.version >= 4:
            attrs += [
                f", left: {self.left:5.1f}",
                f", right: {self.right:5.1f}",
                f", up: {self.up:5.1f}",
                f", down: {self.down:5.1f}",
            ]

        if self.version >= 3:
            attrs += [
                f", temperature: {self.temperature:5.1f}",
                f", hours: {self.hours:5.1f}",
                f", minutes: {self.minutes:5.1f}",
                f", seconds: {self.seconds:5.1f}",
            ]

        return f"{self.__class__.__name__}(" + ", ".join([i for i in attrs if i != ""]) + ")"
