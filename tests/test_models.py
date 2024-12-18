import json
import unittest
from pathlib import Path

import jsondiff
import pytest
from pydantic import ValidationError

from mnemo_lib.models import DMPFile
from mnemo_lib.models import Section
from mnemo_lib.models import Shot


class TestShot(unittest.TestCase):
    """
    Test suite for the Shot Pydantic model.
    """

    def test_valid_shot(self):
        """
        Test creating a valid Shot instance.
        """
        data = {
            "depth_in": 9.39,
            "depth_out": 11.03,
            "down": 0.0,
            "head_in": 276.1,
            "head_out": 279.9,
            "hours": 15,
            "left": 0.0,
            "length": 3.29,
            "marker_idx": 0,
            "minutes": 20,
            "pitch_in": -29.9,
            "pitch_out": -30.9,
            "right": 0.0,
            "seconds": 55,
            "temperature": 25.3,
            "type": 2,
            "up": 0.0,
        }
        shot = Shot(**data)

        differences = jsondiff.diff(shot.model_dump(), data)
        assert not differences, f"Serialization altered JSON: {differences}"

    def test_invalid_shot_missing_field(self):
        """
        Test Shot model with missing required fields.
        """
        data = {
            "depth_in": 10.0,
            "depth_out": 12.0,
            # Missing 'down' and other required fields
        }
        with pytest.raises(ValidationError) as excinfo:
            Shot(**data)
        assert "Field required" in str(excinfo.value)

    def test_invalid_shot_field_type(self):
        """
        Test Shot model with invalid field types.
        """
        data = {
            "depth_in": "invalid",  # Should be a float
            "depth_out": 12.0,
            "down": 0.5,
            "head_in": 30.0,
            "head_out": 35.0,
            "hours": 1,
            "left": 1.0,
            "length": 5.0,
            "marker_idx": 2,
            "minutes": 15,
            "pitch_in": 10.0,
            "pitch_out": 12.0,
            "right": 0.8,
            "seconds": 45,
            "temperature": 20.0,
            "type": 1,
            "up": 0.4,
        }
        with pytest.raises(ValidationError) as excinfo:
            Shot(**data)
        assert "Input should be a valid number" in str(excinfo.value)

    def test_shot_round_trip_json_ShotJsonShot(self):  # noqa: N802
        """
        Test JSON serialization and deserialization for Shot.
        Shot -> JSON -> Shot
        """
        data = {
            "depth_in": 9.39,
            "depth_out": 11.03,
            "down": 0.0,
            "head_in": 276.1,
            "head_out": 279.9,
            "hours": 15,
            "left": 0.0,
            "length": 3.29,
            "marker_idx": 0,
            "minutes": 20,
            "pitch_in": -29.9,
            "pitch_out": -30.9,
            "right": 0.0,
            "seconds": 55,
            "temperature": 25.3,
            "type": 2,
            "up": 0.0,
        }
        shot = Shot(**data)
        json_data = shot.model_dump_json()
        recreated_shot = Shot.model_validate_json(json_data)
        assert recreated_shot == shot

    def test_shot_round_trip_json_JsonShotJson(self):  # noqa: N802
        """
        Test JSON serialization and deserialization for Shot.
        JSON -> Shot -> JSON
        """
        json_file = Path("tests/artifacts/shot.json")
        assert json_file.exists(), "Sample JSON file does not exist"

        # Read the JSON file
        with json_file.open() as f:
            input_data = json.load(f)

        # Parse the JSON data into a Shot model
        shot = Shot(**input_data)

        # Verify everything went well
        differences = jsondiff.diff(shot.model_dump(), input_data)
        assert not differences, f"Serialization altered JSON: {differences}"

        # Serialize the model back to JSON
        output_json = json.loads(shot.model_dump_json())
        differences = jsondiff.diff(output_json, input_data)
        assert not differences, f"Serialization altered JSON: {differences}"


class TestSection(unittest.TestCase):
    """
    Test suite for the Section Pydantic model.
    """

    def test_valid_section(self):
        """
        Test creating a valid Section instance.
        """
        data = {
            "date": "2024-12-14 15:20",
            "direction": 1,
            "name": "EA1",
            "shots": [
                {
                    "depth_in": 9.39,
                    "depth_out": 11.03,
                    "down": 0.0,
                    "head_in": 276.1,
                    "head_out": 279.9,
                    "hours": 15,
                    "left": 0.0,
                    "length": 3.29,
                    "marker_idx": 0,
                    "minutes": 20,
                    "pitch_in": -29.9,
                    "pitch_out": -30.9,
                    "right": 0.0,
                    "seconds": 55,
                    "temperature": 25.3,
                    "type": 2,
                    "up": 0.0,
                }
            ],
            "version": 5,
        }
        model_item = Section(**data)

        differences = jsondiff.diff(model_item.model_dump(), data)
        assert not differences, f"Serialization altered JSON: {differences}"

    def test_section_round_trip_SectionJsonSection(self):  # noqa: N802
        """
        Test JSON round trip: serialization and deserialization for Section.
        Section -> JSON -> Section
        """

        data = {
            "date": "2024-12-01 12:03",
            "direction": 1,
            "name": "Example Cave",
            "shots": [
                {
                    "depth_in": 10.0,
                    "depth_out": 12.0,
                    "down": 0.5,
                    "head_in": 30.0,
                    "head_out": 35.0,
                    "hours": 1,
                    "left": 1.0,
                    "length": 5.0,
                    "marker_idx": 2,
                    "minutes": 15,
                    "pitch_in": 10.0,
                    "pitch_out": 12.0,
                    "right": 0.8,
                    "seconds": 45,
                    "temperature": 20.0,
                    "type": 1,
                    "up": 0.4,
                }
            ],
            "version": 1,
        }
        model_item = Section(**data)
        json_data = model_item.model_dump_json()
        recreated_item = Section.model_validate_json(json_data)
        assert recreated_item == model_item

    def test_section_round_trip_JsonSectionJson(self):  # noqa: N802
        """
        Test JSON round trip: serialization and deserialization for Section.
        JSON -> Section -> JSON
        """
        json_file = Path("tests/artifacts/section.json")
        assert json_file.exists(), "Sample JSON file does not exist"

        # Read the JSON file
        with json_file.open() as f:
            input_data = json.load(f)

        # Parse the JSON data into a Shot model
        shot = Section(**input_data)

        # Verify everything went well
        differences = jsondiff.diff(shot.model_dump(), input_data)
        assert not differences, f"Serialization altered JSON: {differences}"

        # Serialize the model back to JSON
        output_json = json.loads(shot.model_dump_json())
        differences = jsondiff.diff(output_json, input_data)
        assert not differences, f"Serialization altered JSON: {differences}"


class TestDMPFile(unittest.TestCase):
    """
    Test suite for the DMPFile Pydantic model.
    """

    def test_valid_dmpfile(self):
        """
        Test creating a valid DMPFile instance.
        """
        survey_data = {
            "date": "2024-12-01 13:03",
            "direction": 1,
            "name": "Example Cave",
            "shots": [
                {
                    "depth_in": 10.0,
                    "depth_out": 12.0,
                    "down": 0.5,
                    "head_in": 30.0,
                    "head_out": 35.0,
                    "hours": 1,
                    "left": 1.0,
                    "length": 5.0,
                    "marker_idx": 2,
                    "minutes": 15,
                    "pitch_in": 10.0,
                    "pitch_out": 12.0,
                    "right": 0.8,
                    "seconds": 45,
                    "temperature": 20.0,
                    "type": 1,
                    "up": 0.4,
                }
            ],
            "version": 1,
        }

        data = [survey_data, survey_data, survey_data]

        instance = DMPFile.model_validate(data)

        # Verify everything went well
        differences = jsondiff.diff(instance.model_dump(), data)
        assert not differences, f"Serialization altered JSON: {differences}"

        # model_data = {"__root__": [model_item_data]}
        # model = Model(**model_data)
        # assert len(model.__root__) == 1
        # assert model.__root__[0].name == "Example Cave"

    def test_dmpfile_round_trip_DMPFileJsonDMPFile(self):  # noqa: N802
        """
        Test JSON round trip: serialization and deserialization for DMPFile.
        DMPfile -> JSON -> DMPfile
        """
        data = [
            {
                "date": "2024-12-01 15:34",
                "direction": 1,
                "name": "Example Cave",
                "shots": [
                    {
                        "depth_in": 10.0,
                        "depth_out": 12.0,
                        "down": 0.5,
                        "head_in": 30.0,
                        "head_out": 35.0,
                        "hours": 1,
                        "left": 1.0,
                        "length": 5.0,
                        "marker_idx": 2,
                        "minutes": 15,
                        "pitch_in": 10.0,
                        "pitch_out": 12.0,
                        "right": 0.8,
                        "seconds": 45,
                        "temperature": 20.0,
                        "type": 1,
                        "up": 0.4,
                    }
                ],
                "version": 1,
            },
            {
                "date": "2024-12-01 06:32",
                "direction": 1,
                "name": "Example Cave",
                "shots": [
                    {
                        "depth_in": 10.0,
                        "depth_out": 12.0,
                        "down": 0.5,
                        "head_in": 30.0,
                        "head_out": 35.0,
                        "hours": 1,
                        "left": 1.0,
                        "length": 5.0,
                        "marker_idx": 2,
                        "minutes": 15,
                        "pitch_in": 10.0,
                        "pitch_out": 12.0,
                        "right": 0.8,
                        "seconds": 45,
                        "temperature": 20.0,
                        "type": 1,
                        "up": 0.4,
                    }
                ],
                "version": 1,
            },
        ]
        model_item = DMPFile(data)
        json_data = model_item.model_dump_json()
        recreated_item = DMPFile.model_validate_json(json_data)
        assert recreated_item == model_item

    def test_dmpfile_round_trip_JsonShotJson(self):  # noqa: N802
        """
        Test JSON round trip: serialization and deserialization for DMPFile.
        JSON -> DMPfile -> JSON
        """
        json_file = Path("tests/artifacts/dmpfile.json")
        assert json_file.exists(), "Sample JSON file does not exist"

        # Read the JSON file
        with json_file.open() as f:
            input_data = json.load(f)

        # Parse the JSON data into a Shot model
        shot = DMPFile(input_data)

        # Verify everything went well
        differences = jsondiff.diff(shot.model_dump(), input_data)
        assert not differences, f"Serialization altered JSON: {differences}"

        # Serialize the model back to JSON
        output_json = json.loads(shot.model_dump_json())
        differences = jsondiff.diff(output_json, input_data)
        assert not differences, f"Serialization altered JSON: {differences}"
