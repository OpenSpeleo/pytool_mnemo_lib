#!/usr/bin/env python

import json

from collections import UserList
from pathlib import Path
from typing import Optional
from typing import Union

from mnemo_lib.sections import Section
from mnemo_lib.encoder import SectionJSONEncoder


class SectionList(UserList):
    def to_json(self, filepath: Optional[Union[str, Path]] = None) -> str:
        json_str = json.dumps(
            self.data,
            cls=SectionJSONEncoder,
            indent=4,
            sort_keys=True
        )

        if filepath is not None:
            with open(filepath, mode="w") as file:
                file.write(json_str)

        return json_str


def read_dmp(path: Union[Path, str]) -> SectionList[Section]:
    if not path.exists():
        raise FileNotFoundError()

    with open(path, 'r') as file:
        data = [int(i) for i in file.read().strip().split(";") if i != ""]

    sections = SectionList()
    buffer_start = 0
    while True:
        try:
            buffer = data[buffer_start:]

            if buffer == [77, 78, 50, 79, 118, 101, 114]:
                # ASCII message not removed by Ariane: "MN2OVER"
                raise StopIteration()

            section = Section(buffer)
            buffer_start += section.buffer_len

            sections.append(section)

        except (IndexError, StopIteration):
            break

    return sections
