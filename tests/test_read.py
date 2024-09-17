#!/usr/bin/env python

import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from parameterized import parameterized_class

from mnemo_lib.reader import read_dmp


def sha256sum(filepath: str | Path):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    with filepath.open(mode="rb", buffering=0) as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


@parameterized_class(
    ("filepath"),
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

        with Path(str(self._file)[:-3] + "json").open(mode="r") as f:
            json_target = json.load(f)

        assert json.loads(json_str) == json_target

    def test_round_trip(self):
        with TemporaryDirectory() as tmp_dir:
            dmp_fp = Path(tmp_dir) / "output.dmp"
            self._dmp_data.to_dmp(filepath=dmp_fp)

            assert sha256sum(dmp_fp) == sha256sum(self._file)

if __name__ == "__main__":
    unittest.main()
