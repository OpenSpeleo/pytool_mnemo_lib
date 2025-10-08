from __future__ import annotations

import tempfile
import unittest
from abc import ABC
from abc import abstractmethod
from pathlib import Path


class BaseCMDTestCase(ABC, unittest.TestCase):
    def setUp(self):
        self._file = Path(self.input_file)
        if not self._file.exists():
            raise FileNotFoundError(f"File not found: `{self._file}`")

        self._temp_dir_ctx = tempfile.TemporaryDirectory()
        self._temp_dir = Path(self._temp_dir_ctx.__enter__())

    def tearDown(self):
        self._temp_dir_ctx.__exit__(None, None, None)

    def get_test_cmd(self, *args, **kwargs):
        return self.command_template.format(*args, **kwargs).strip()

    @abstractmethod
    def command_template(self) -> str:
        raise NotImplementedError
