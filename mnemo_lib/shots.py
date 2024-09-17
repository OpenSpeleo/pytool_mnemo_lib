#!/usr/bin/env python

import dataclasses
from pathlib import Path

from mnemo_lib.types import ShotType


@dataclasses.dataclass
class Shot:
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
    left: int | None = None
    right: int | None = None
    up: int | None = None
    down: int | None = None

    # File Version >= 3
    temperature: int | None = 0

    # File Version >= 3
    hours: int | None = 0
    minutes: int | None = 0
    seconds: int | None = 0

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

    def _readInt8_from_buff(self) -> int:  # noqa: N802
        data = self[self._cursor]
        self._cursor += 1
        return int(data)

    def _readInt16BE_from_buff(self) -> float:  # noqa: N802
        lsb = self._readInt8_from_buff()
        msb = self._readInt8_from_buff()

        # ---- old method ---- #
        # if msb < 0:
        #     msb = 2**8 + msb
        #
        # return lsb * 2**8 + msb
        # -------------------- #
        return (lsb * 2**8) + (msb & 0xff)

    def _writeInt16BE(self, value: int) -> tuple[int, int]:  # noqa: N802
        value = round(value)
        first = (value >> 8) & 0xff if value >= 0 else value // 255

        # last is in [-128, 128[
        last = value & 0xff
        last = last - 2**8 if last >= 128 else last

        return first, last

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
            self.validate_magic(self._readInt8_from_buff(), self.shotStartValueA)
            self.validate_magic(self._readInt8_from_buff(), self.shotStartValueB)
            self.validate_magic(self._readInt8_from_buff(), self.shotStartValueC)

        self.type = ShotType(self._readInt8_from_buff())

        self.head_in = self._readInt16BE_from_buff() / 10.0
        self.head_out = self._readInt16BE_from_buff() / 10.0
        self.length = self._readInt16BE_from_buff() / 100.0
        self.depth_in = self._readInt16BE_from_buff() / 100.0
        self.depth_out = self._readInt16BE_from_buff() / 100.0
        self.pitch_in = self._readInt16BE_from_buff() / 10.0
        self.pitch_out = self._readInt16BE_from_buff() / 10.0

        if version >= 4:
            self.left = self._readInt16BE_from_buff() / 100.0
            self.right = self._readInt16BE_from_buff() / 100.0
            self.up = self._readInt16BE_from_buff() / 100.0
            self.down = self._readInt16BE_from_buff() / 100.0

        if version >= 3:
            self.temperature = self._readInt16BE_from_buff() / 10.0
            self.hours = int(self._readInt8_from_buff())
            self.minutes = int(self._readInt8_from_buff())
            self.seconds = int(self._readInt8_from_buff())

        self.marker_idx = self._readInt8_from_buff()

        if self.version >=5:
            self.validate_magic(self._readInt8_from_buff(), self.shotEndValueA)
            self.validate_magic(self._readInt8_from_buff(), self.shotEndValueB)
            self.validate_magic(self._readInt8_from_buff(), self.shotEndValueC)

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

        return f"{self.__class__.__name__}(" + ", ".join([i for i in attrs if i != ""]) + ")"  # noqa: E501

    def to_dmp(self, filepath: str | Path | None = None) -> list[int] | None:
        data = []

        # Magic Numbers
        if self.version >=5:
            data += [
                57,
                67,
                77
            ]

        data += [
            self.type.value,
            *self._writeInt16BE(self.head_in * 10.0),
            *self._writeInt16BE(self.head_out * 10.0),
            *self._writeInt16BE(self.length * 100.0),
            *self._writeInt16BE(self.depth_in * 100.0),
            *self._writeInt16BE(self.depth_out * 100.0),
            *self._writeInt16BE(self.pitch_in * 10.0),
            *self._writeInt16BE(self.pitch_out * 10.0),
        ]

        if self.version >= 4:
            data += [
                *self._writeInt16BE(self.left * 100.0),
                *self._writeInt16BE(self.right * 100.0),
                *self._writeInt16BE(self.up * 100.0),
                *self._writeInt16BE(self.down * 100.0),
            ]

        if self.version >= 3:
            data += [
                *self._writeInt16BE(self.temperature * 10.0),
                self.hours,
                self.minutes,
                self.seconds,
            ]

        data += [self.marker_idx]

        if self.version >=5:
            data += [
                95,
                25,
                35
            ]

        return data
