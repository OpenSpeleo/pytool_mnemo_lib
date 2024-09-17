#!/usr/bin/env python

from collections.abc import Iterator
from pathlib import Path

from mnemo_lib.sections import Section
from mnemo_lib.sections import SectionList


def split_dmp_into_sections(data: list[int]) -> Iterator[list[int]]:

    dmp_version = data[0]
    assert dmp_version in range(2, 6)  # Between 2 and 5

    match dmp_version:

        case 2:
            end_seq_pattern = [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        case 5:
            end_seq_pattern = [57, 67, 77, 3] + [0] * 28 + [95, 25, 35]

    len_end_seq = len(end_seq_pattern)

    start_seq_idx = 0

    for current_idx in range(len(data) - len_end_seq + 1):
        window = data[current_idx:current_idx + len_end_seq]

        # new start sequence is found
        if window == end_seq_pattern:

            end_of_sequence_idx = current_idx + len_end_seq

            # return the found section
            yield data[start_seq_idx:end_of_sequence_idx]

            # move the start index to the nex sequence
            start_seq_idx = end_of_sequence_idx


def read_dmp(filepath: Path | str) -> SectionList[Section]:

    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError

    with filepath.open(mode="r") as file:
        data = [int(i) for i in file.read().strip().split(";") if i != ""]

    return SectionList([
        Section(section_dmp)
        for section_dmp in split_dmp_into_sections(data)]
    )
