from __future__ import annotations

from collections.abc import (
    Callable,
    Iterator,
    Iterable,
    Mapping,
    Sequence
)

from typing import Any

from .types import Class, Instance
from .field_extractors import (
    BaseFieldExtractor,
    DictFieldExtractor,
    SlotsFieldExtractor,
    IncludedFieldExtractor
)


class KWRepr:
    """
    Keyword-based representation (__repr__) on objects.
    """

    DELIMITERS: tuple[str, str] = ("(", ")")

    def __init__(
        self,
        class_or_inst: Class | Instance,
        *,
        include: Sequence[str] | None = None,
        exclude: Sequence[str] | None = None,
        compute: Mapping[str, Callable[[Instance], Any]] | None = None,
        format_spec: Mapping[str, str] | None = None,
        exclude_private: bool = True,
        skip_missing: bool = False,
        repr_config: Mapping[str, Any] | None = None,
        delimiters: tuple[str, str] | None = None
    ) -> None:
        """
        Initiate class KWRepr.

        Parameters:
            include: Names of attributes to only include.
            exclude: Names of attributes to only exclude.
            exclude: Whether to exclude private attributes.
            skip_missing: Whether to skip missing attributes.
            repr_config: class reprlib.Repr init parameters.

        Raises:
            ValueError:
                If specified both include and exclude parameters.
        """
        if include is not None and exclude is not None:
            raise ValueError("Cannot specify both 'include' and 'exclude'")

        """self.include = include
        self.exclude = exclude
        self.compute = compute
        self.format_spec = format_spec
        self.exclude_private = exclude_private
        self.skip_missing = skip_missing"""
        self.repr_config = repr_config
        self.delimiters = delimiters or self.DELIMITERS

        field_extractor_cls: BaseFieldExtractor = self.resolve_field_extractor(class_or_inst, include)
        self.field_extractor: BaseFieldExtractor = field_extractor_cls(
            include=include,
            exclude=exclude,
            compute=compute,
            format_spec=format_spec,
            exclude_private=exclude_private,
            skip_missing=skip_missing,
            repr_config=repr_config
        )

    def generate_body(self, fields: Iterable[tuple[str, str]]) -> str:
        return ", ".join(
            f"{field_name}={field_value}"
            for field_name, field_value in fields
        )

    def generate_str(self, inst: Instance, fields: Iterable[tuple[str, str]]) -> str:
        name = type(inst).__qualname__
        start, end = self.delimiters

        body = self.generate_body(fields)

        parts: list[str] = [name, start, body, end]

        return "".join(parts)

    def generate(self, inst: Instance) -> str:
        fields = self.field_extractor.extract_fields(inst)
        repr_str = self.generate_str(inst, fields)
        return repr_str

    @staticmethod
    def resolve_field_extractor(class_or_inst: Class | Instance, include: Sequence[str] | None = None) -> type[BaseFieldExtractor]:
        class_: Class = class_or_inst if isinstance(class_or_inst, type) else type(class_or_inst)

        if include is not None:
            return IncludedFieldExtractor
        if hasattr(class_, "__dict__"):
            return DictFieldExtractor
        if hasattr(class_, "__slots__"):
            return SlotsFieldExtractor

        raise TypeError(
            f"Type {type(class_).__name__} must define either '__dict__' or '__slots__'"
        )

    @classmethod
    def inject_repr(
        cls,
        class_: Class,
        include: Sequence[str] | None = None,
        exclude: Sequence[str] | None = None,
        compute: Mapping[str, Callable[[Instance], Any]] | None = None,
        format_spec: Mapping[str, str] | None = None,
        exclude_private: bool = False,
        skip_missing: bool = False,
        repr_config: Mapping[str, Any] | None = None,
        delimiters: tuple[str, str] | None = None
    ) -> None:
        kwrepr: KWRepr = cls(
            class_or_inst=class_,
            include=include,
            exclude=exclude,
            compute=compute,
            format_spec=format_spec,
            exclude_private=exclude_private,
            skip_missing=skip_missing,
            repr_config=repr_config,
            delimiters=delimiters
        )

        def _repr(self):
            return kwrepr.generate(self)

        _repr.__qualname__ = f"{class_.__name__}.__repr__"

        class_.__repr__ = _repr
