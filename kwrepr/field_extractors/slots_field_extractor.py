from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any

from .base_field_extractor import BaseFieldExtractor
from ..types import Instance


class SlotsFieldExtractor(BaseFieldExtractor):
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
        for field_name in type(inst).__slots__:
            if not self.is_field_allowed(field_name):
                continue

            if field_name.startswith("__") and not field_name.endswith("__"):
                field_name = f"_{type(inst).__name__}{field_name}"

            try:
                field_value = getattr(inst, field_name)
            except AttributeError:
                if self.skip_missing:
                    continue

                raise AttributeError(f"Missing required attribute: {field_name}") from None

            field_value = self.process_field_value(inst, field_name, field_value)

            yield field_name, field_value