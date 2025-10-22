from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator, Mapping, Sequence
from reprlib import Repr
from typing import Any

from ..types import Instance


class BaseFieldExtractor(ABC):
    def __init__(
        self,
        *,
        include: Sequence[str] | None = None,
        exclude: Sequence[str] | None = None,
        compute: Mapping[str, Callable[[Instance], Any]] | None = None,
        format_spec: Mapping[str, str] | None = None,
        exclude_private: bool = True,
        skip_missing: bool = False,
        repr_config: Mapping[str, Any] | None = None
    ) -> None:
        self.include = include or []
        self.exclude = exclude or []
        self.compute = compute or {}
        self.format_spec = format_spec or {}
        self.exclude_private = exclude_private
        self.skip_missing = skip_missing

        self._field_value_repr: Repr = Repr(**(repr_config or {}))

    @abstractmethod
    def extract_fields(self, inst: Instance) -> Iterator[tuple[str, str]]:
        ...

    def is_field_allowed(self, field_name: str) -> bool:
        if field_name.startswith("_") and self.exclude_private:
            return False
        if field_name in self.exclude:
            return False

        return True

    def process_field_value(self, inst: Instance, field_name: str, field_value: Any) -> str:
        if field_computer := self.compute.get(field_name):
            field_value = field_computer(inst)

        if format_spec := self.format_spec.get(field_name):
            field_value = format(field_value, format_spec)
        else:
            field_value = self.repr_field_value(field_value)

        return field_value

    def repr_field_value(self, field_value: Any) -> str:
        return self._field_value_repr.repr(field_value)
