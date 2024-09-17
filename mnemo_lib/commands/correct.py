# #!/usr/bin/env python3

import argparse
from pathlib import Path

from mnemo_lib.reader import read_dmp


def correct(args: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="mnemo correct")

    parser.add_argument(
        "--input_file",
        type=str,
        default=None,
        required=True,
        help="Mnemo DMP Source File."
    )

    parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        required=True,
        help="Path to save the converted file at."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwrite an already existing file.",
        default=False,
    )

    parser.add_argument(
        "--length_scaling",
        type=float,
        required=False,
        default=None,
        help="Apply post-survey recalibration scaling factor to a DMP file."
    )

    parser.add_argument(
        "--compass_offset",
        type=float,
        required=False,
        default=None,
        help="Apply post-survey recalibration compass offset to a DMP file."
    )

    parser.add_argument(
        "--depth_offset",
        type=float,
        required=False,
        default=None,
        help=(
            "Apply post-survey depth offset to a DMP file. "
            "`offset > 0` => correcting deeper. "
            "`offset < 0` => correcting shallower."
        )
    )

    parsed_args = parser.parse_args(args)

    dmp_file = Path(parsed_args.input_file)
    if not dmp_file.exists():
        raise FileNotFoundError(f"Impossible to find: `{dmp_file}`.")

    output_file = Path(parsed_args.output_file)
    if output_file.exists() and not parsed_args.overwrite:
        raise FileExistsError(f"The file {output_file} already existing. "
                              "Please pass the flag `--overwrite` to ignore.")

    sections = read_dmp(dmp_file)

    for section in sections:
        for shot in section.shots:
            if parsed_args.length_scaling is not None:
                shot.length = round(shot.length * parsed_args.length_scaling, ndigits=2)

            if parsed_args.compass_offset is not None:
                shot.head_in = (shot.head_in + parsed_args.compass_offset) % 360
                shot.head_out = (shot.head_out + parsed_args.compass_offset) % 360

            if parsed_args.depth_offset is not None:
                shot.depth_in = round(shot.depth_in + parsed_args.depth_offset, ndigits=2)  # noqa: E501
                shot.depth_out = round(shot.depth_out + parsed_args.depth_offset, ndigits=2)  # noqa: E501

    sections.to_dmp(output_file)

    return 0
