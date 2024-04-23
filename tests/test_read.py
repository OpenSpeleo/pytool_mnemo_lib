#!/usr/bin/env python

import json
import unittest

from pathlib import Path

from mnemo_lib.reader import read_dmp
from parameterized import parameterized_class

@parameterized_class(
    ('filepath'),
    [
        ("tests/artifacts/test_v2.dmp",),
        ("tests/artifacts/test_v5.dmp",)
    ]
)
class ReadDMPFileTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._file = Path(cls.filepath)
        if not cls._file.exists():
            raise FileNotFoundError(f"File not found: `{cls._file}`")

    def setUp(self) -> None:
        self._dmp_data = read_dmp(self._file)

    def test_export_to_json(self):
        if self._dmp_data is None:
            raise ValueError("the DMP data has not been read.")

        json_str = self._dmp_data.to_json()

        with open(str(self._file)[:-3] + "json", "r") as f:
            json_target = json.load(f)

        self.assertEqual(json.loads(json_str), json_target)


if __name__ == '__main__':
    unittest.main()
