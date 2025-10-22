from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any

from kwrepr.types import Instance

from .base_field_extractor import BaseFieldExtractor


class DictFieldExtractor(BaseFieldExtractor):
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
        super().__init__(
            include=include,
            exclude=exclude,
            compute=compute,
            format_spec=format_spec,
            exclude_private=exclude_private,
            skip_missing=skip_missing,
            repr_config=repr_config
        )

    def extract_fields(self, inst: Instance) -> Iterator[tuple[str, str]]:
        for field_name, field_value in vars(inst).items():
            if not self.is_field_allowed(field_name):
                continue

            field_value = self.process_field_value(inst, field_name, field_value)

            yield field_name, field_value
