#!/usr/bin/env python

import json
from collections import UserList
from collections.abc import Iterator
from pathlib import Path

from mnemo_lib.encoder import SectionJSONEncoder
from mnemo_lib.sections import Section


class SectionList(UserList):
    def to_json(self, filepath: str | Path | None = None) -> str:
        json_str = json.dumps(
            self.data,
            cls=SectionJSONEncoder,
            indent=4,
            sort_keys=True
        )

        if filepath is not None:

            if not isinstance(filepath, Path):
                filepath = Path(filepath)

            with filepath.open(mode="w") as file:
                file.write(json_str)

        return json_str

    def to_dmp(self, filepath: str | Path | None = None) -> list[int] | None:
        data = [str(nbr) for section in self.data for nbr in section.to_dmp()]

        if int(data[0]) > 2:  # version > 2
            # adding `MN2OVER` message at the end
            data += [str(nbr) for nbr in [77, 78, 50, 79, 118, 101, 114]]

        if filepath is not None:
            if not isinstance(filepath, Path):
                filepath = Path(filepath)

            with filepath.open(mode="w") as file:
                # always finish with a trailing ";"
                file.write(f"{';'.join(data)};")

        return data


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


