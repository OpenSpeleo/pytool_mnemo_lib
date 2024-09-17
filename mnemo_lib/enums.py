#!/usr/bin/env python

from enum import IntEnum


class Direction(IntEnum):
    In = 0
    Out = 1


class ShotType(IntEnum):
    CSA = 0  # Reference Shot A
    CSB = 1  # Reference Shot B
    STD = 2  # Standard aka. Real
    EOC = 3  # End of Cave


class UnitType(IntEnum):
    METRIC = 0
    IMPERIAL = 1
