#!/usr/bin/env python
import hashlib
import shlex
import subprocess
import unittest
from pathlib import Path

from parameterized import parameterized
from parameterized import parameterized_class

from tests.commands.base import BaseCMDTestCase


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA1 checksum of a file."""
    sha1 = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(8192):  # Read in chunks of 8KB
            sha1.update(chunk)
    return sha1.hexdigest()


class CMDTestCase(BaseCMDTestCase):
    command_template = (
        "mnemo correct --input_file={input_f} --output_file={output_f} {extra}"
    )

    @property
    def outfile(self) -> str:
        return self._temp_dir / "output.dmp"


@parameterized_class(
    ("input_file"),
    [
        ("tests/artifacts/test_v2.dmp",),
        ("tests/artifacts/test_v5.dmp",),
        ("tests/artifacts/test_v5_buggy_EOS.dmp",),
    ],
)
class CorrectCMDTest(CMDTestCase):
    def run_command(self, command: str):
        return subprocess.run(  # noqa: S603
            shlex.split(command),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_convert_file_doesnt_exist(self):
        cmd = self.get_test_cmd(input_f="1223443255", output_f=self.outfile, extra="")
        result = self.run_command(cmd)
        assert result.returncode == 1

    def test_empty_command_do_nothing(self):
        cmd = self.get_test_cmd(input_f=self._file, output_f=self.outfile, extra="")
        result = self.run_command(cmd)
        assert result.returncode == 0
        assert compute_sha256(self._file) == compute_sha256(self.outfile)

        # with overwrite `-w`
        cmd = self.get_test_cmd(input_f=self._file, output_f=self.outfile, extra="-w")
        result = self.run_command(cmd)
        assert result.returncode == 0
        assert compute_sha256(self._file) == compute_sha256(self.outfile)

        # with overwrite `--overwrite`
        cmd = self.get_test_cmd(
            input_f=self._file,
            output_f=self.outfile,
            extra="--overwrite",
        )
        result = self.run_command(cmd)
        assert result.returncode == 0
        assert compute_sha256(self._file) == compute_sha256(self.outfile)

    def test_no_overwrite_failure(self):
        cmd = self.get_test_cmd(input_f=self._file, output_f=self._file, extra="")
        result = self.run_command(cmd)
        assert result.returncode == 1

    @parameterized.expand(
        [
            ("2025-02-17", 0),  # valid date
            ("2025-02-30", 2),  # invalid date
            ("abcd-ef-gh", 2),  # incorrect format
            ("2100-12-12", 2),  # future date
        ]
    )
    def test_change_date(self, date_str, expected_returncode):
        cmd = self.get_test_cmd(
            input_f=self._file, output_f=self.outfile, extra=f"--date={date_str}"
        )
        result = self.run_command(cmd)
        assert result.returncode == expected_returncode
        if result.returncode == 0:
            assert compute_sha256(self._file) != compute_sha256(self.outfile)

    @parameterized.expand(
        [
            ("0.6", 0),  # valid scaling
            ("1.0", 0),  # valid scaling
            ("1.6", 0),  # valid scaling
            ("0.0", 2),  # null scaling makes no sense
            ("-1.2", 2),  # negative scaling makes no sense
            ("abc", 2),  # non-float value
        ]
    )
    def test_scale_length(self, scaling_factor, expected_returncode):
        cmd = self.get_test_cmd(
            input_f=self._file,
            output_f=self.outfile,
            extra=f"--length_scaling={scaling_factor}",
        )
        result = self.run_command(cmd)
        assert result.returncode == expected_returncode, (
            result.returncode,
            result.stdout,
            result.stderr,
        )
        if result.returncode == 0:
            if scaling_factor != "1.0":
                assert compute_sha256(self._file) != compute_sha256(self.outfile)
            else:
                assert compute_sha256(self._file) == compute_sha256(self.outfile)

    def test_reverse_azimuth(self):
        cmd = self.get_test_cmd(
            input_f=self._file, output_f=self.outfile, extra="--reverse_azimuth"
        )
        result = self.run_command(cmd)
        assert result.returncode == 0
        assert compute_sha256(self._file) != compute_sha256(self.outfile)

    @parameterized.expand(
        [
            ("0", 0),  # valid offset - no effect
            ("240", 0),  # valid offset
            ("360", 2),  # invalid offset - >= 360
            ("500", 2),  # invalid offset - >= 360
            ("-1", 2),  # invalid offset - < 0
            ("abc", 2),  # non-float value
        ]
    )
    def test_compass_offset(self, compass_offset, expected_returncode):
        cmd = self.get_test_cmd(
            input_f=self._file,
            output_f=self.outfile,
            extra=f"--compass_offset={compass_offset}",
        )
        result = self.run_command(cmd)
        assert result.returncode == expected_returncode, (
            result.returncode,
            result.stdout,
            result.stderr,
        )
        if result.returncode == 0:
            if compass_offset != "0.0":
                assert compute_sha256(self._file) != compute_sha256(self.outfile)
            else:
                assert compute_sha256(self._file) == compute_sha256(self.outfile)

    @parameterized.expand(
        [
            ("0.0", 0),  # valid offset - no effect
            ("-1.0", 0),  # valid offset - shallower
            ("1.6", 0),  # valid offset - deeper
            ("abc", 2),  # non-float value
        ]
    )
    def test_depth_offset(self, depth_offset, expected_returncode):
        cmd = self.get_test_cmd(
            input_f=self._file,
            output_f=self.outfile,
            extra=f"--depth_offset={depth_offset}",
        )
        result = self.run_command(cmd)
        assert result.returncode == expected_returncode, (
            result.returncode,
            result.stdout,
            result.stderr,
        )
        if result.returncode == 0:
            if depth_offset != "0.0":
                assert compute_sha256(self._file) != compute_sha256(self.outfile)
            else:
                assert compute_sha256(self._file) == compute_sha256(self.outfile)


if __name__ == "__main__":
    unittest.main()
