#!/usr/bin/env python

import json
import unittest

from pathlib import Path

from mnemo_lib.reader import read_dmp
from parameterized import parameterized_class

@parameterized_class(
    ('filepath'),
    [
        ("tests/test_v2.dmp",),
        ("tests/test_v5.dmp",)
    ]
)
class ReadDMPFileTest(unittest.TestCase):

    def test_load(self):
        dmp_file = Path(self.filepath)
        read_dmp(dmp_file)

    def test_export_to_json(self):
        dmp_file = Path(self.filepath)
        json_str = read_dmp(dmp_file).to_json()

        with open(str(dmp_file)[:-3] + "json", "r") as f:
            json_target = json.load(f)

        self.assertEqual(json.loads(json_str), json_target)


if __name__ == '__main__':
    unittest.main()
