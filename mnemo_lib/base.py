from abc import ABCMeta
from abc import abstractmethod
from pathlib import Path


class MnemoMixin(metaclass=ABCMeta):

    def to_json(self, filepath: str | Path | None = None) -> str:

        json_str = self._to_json()

        if filepath is not None:

            if not isinstance(filepath, Path):
                filepath = Path(filepath)

            with filepath.open(mode="w") as file:
                file.write(json_str)

        return json_str

    @abstractmethod
    def _to_json(self) -> str:
        pass


    def to_dmp(self, filepath: str | Path | None = None) -> list[int]:

        data = self._to_dmp()

        if filepath is not None:

            if not isinstance(filepath, Path):
                filepath = Path(filepath)

            with filepath.open(mode="w") as file:
                # always finish with a trailing ";"
                file.write(f"{';'.join([str(nbr) for nbr in data])};")

        return data

    @abstractmethod
    def _to_dmp(self) -> list[int]:
        pass

