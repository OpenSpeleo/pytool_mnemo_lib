from pathlib import Path

from mnemo_lib.reader import read_dmp

if __name__ == "__main__":
    paths = [
        "tests/artifacts/test_v5.dmp",
        "tests/artifacts/test_v2.dmp"
    ]

    for fp in paths:
        dmp_file = Path(fp)
        print("-------------------------------------------------------")
        sections = read_dmp(dmp_file)
        print(sections.to_json(filepath=fp[:-3] + "json"))
