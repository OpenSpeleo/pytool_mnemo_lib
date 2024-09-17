#!/usr/bin/env python

from datetime import datetime
from functools import cached_property
from pathlib import Path

from mnemo_lib.shots import Shot
from mnemo_lib.types import Direction
from mnemo_lib.types import ShotType
from mnemo_lib.types import UnitType


class Section:

    def __init__(self, bytearr: list[int]) -> None:
        self._bytearray = bytearr
        self._max_buffer_idx = -1
        self._unit_type = UnitType.METRIC

        if self.version not in range(2, 6):
            raise ValueError(
                "Invalid File Format. Expected DMP version `[2, 5]`, "
                f"got `{self.version}`"
            )

    @property
    def _start_offset(self):
        # V5 and above start by reading 3 magic number just after the version
        return 0 if self.version < 5 else 3

    @property
    def unit_type(self):
        return self._unit_type

    @property
    def unit_conversion_factor(self):
        return 1.0 if self.unit_type == UnitType.METRIC else 3.28084
        # V5 and above start by reading 3 magic number just after the version
        return 0 if self.version < 5 else 3

    def __getitem__(self, index: int | slice) -> int:
        return self._bytearray[index]

    @cached_property
    def version(self):
        return self[0]

    @property
    def buffer_len(self):
        # Make sure the shots have been read => full buffer read
        _ = self.shots
        return len(self._bytearray)

    @cached_property
    def date(self) -> datetime:

        year = self[self._start_offset + 1] + 2000
        if year not in range(2016, 2100):
            raise ValueError(f"Invalid year: `{year}`")

        return datetime(  # noqa: DTZ001
            year=year,
            month=self[self._start_offset + 2],
            day=self[self._start_offset + 3],
            hour=self[self._start_offset + 4],
            minute=self[self._start_offset + 5],
        )

    @cached_property
    def name(self) -> str:
        return "".join([
            chr(i)
            for i in
                self._bytearray[self._start_offset + 6: self._start_offset + 9]
        ])

    def _read_single_shot(self, buff_offset:int) -> Shot:
        buff = self[buff_offset:]
        if buff == [77, 78, 50, 79, 118, 101, 114]:
            # ASCII message not removed by Ariane: "MN2OVER"
            raise StopIteration

        return Shot(version=self.version, buff=buff)

    @cached_property
    def shots(self) -> list[Shot]:
        shots = []

        buff_offset = 10 + self._start_offset # Initial value

        # `while True` loop equivalent with exit bound
        # There will never be more than 9999 shots in one section.
        for _ in range(9999):
            try:
                shot = self._read_single_shot(buff_offset=buff_offset)
                buff_offset += shot.buff_len
                shots.append(shot)

                if shot.type == ShotType.EOC:
                    break

            except StopIteration:
                break

        # Trim the bytearray to the end.
        self._bytearray = self._bytearray[0:buff_offset]
        return shots

    @cached_property
    def direction(self) -> Direction:
        return Direction(self[self._start_offset + 9])

    def __repr_shots__(self, spaces=8) -> str:
        rslt = ""
        for shot in self.shots:
            rslt += f"{' ' * spaces}{shot},\n"
        return rslt.rstrip()[:-1]  # remove trailing "\n" and ","

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}(
    version: {self.version},
    buffer_length: {self.buffer_len},
    name: {self.name},
    date: {self.date},
    direction: {self.direction.name.upper()},
    shots: [
{self.__repr_shots__()}
    ],
)"""

    def asdict(self):
        return {
            "version": self.version,
            "name": self.name,
            "date": self.date,
            "direction": self.direction,
            "shots": [shot.asdict() for shot in self.shots]
        }

    def to_dmp(self, filepath: str | Path | None = None) -> list[int] | None:

        # =================== DMP HEADER =================== #
        data = [
            self.version
        ]

        if self.version > 2:  # magic numbers
            data += [68, 89, 101]

        data += [
            self.date.year % 100,  # 2023 -> 23
            self.date.month,
            self.date.day,
            self.date.hour,
            self.date.minute,
            ord(self.name[0]),
            ord(self.name[1]),
            ord(self.name[2]),
            self.direction.value
        ]
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

        for shot in self.shots:
            data += shot.to_dmp()

        if filepath is not None:
            if not isinstance(filepath, Path):
                filepath = Path(filepath)

            with filepath.open(mode="w") as file:
                file.write(";".join(data))

        return data
