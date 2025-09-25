from collections.abc import (
    Callable,
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
    Keyword-based representation (__repr__) generator for objects.

    This class allows dynamic, configurable generation of `__repr__`
    strings based on object attributes, supporting inclusion/exclusion,
    computed fields, formatting, and fallback handling.
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
        Initialize a KWRepr object for the given class or instance.

        Parameters:
            class_or_inst: A class or instance to attach repr generation to.
            include: Explicit list of attribute names to include.
            exclude: List of attribute names to exclude.
            compute: Mapping of computed field names to callables that
                     return their values.
            format_spec: Mapping of attribute names to format spec strings.
            exclude_private: Whether to skip attributes starting with "_".
            skip_missing: Skip missing or inaccessible attributes if True.
            repr_config: Optional config passed to reprlib.Repr.
            delimiters: Tuple of delimiters to wrap around the repr body.

        Raises:
            ValueError: If both `include` and `exclude` are provided.
            TypeError: If the given type does not define `__dict__` or `__slots__`.
        """
        if include is not None and exclude is not None:
            raise ValueError("Cannot specify both 'include' and 'exclude'")

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
        """
        Generate the comma-separated key=value string for the repr body.

        Parameters:
            fields: Iterable of (name, value_str) pairs.

        Returns:
            A string in the form 'x=val, y=val, ...'.
        """
        return ", ".join(
            f"{field_name}={field_value}"
            for field_name, field_value in fields
        )

    def generate_str(self, inst: Instance, fields: Iterable[tuple[str, str]]) -> str:
        """
        Generate the final __repr__ string using provided fields.

        Parameters:
            inst: The instance being represented.
            fields: Iterable of (name, value_str) pairs.

        Returns:
            The full __repr__ string.
        """
        name = type(inst).__qualname__
        start, end = self.delimiters

        body = self.generate_body(fields)

        parts: list[str] = [name, start, body, end]

        return "".join(parts)

    def generate(self, inst: Instance) -> str:
        """
        Compute the __repr__ string for the given instance.

        Parameters:
            inst: The instance to represent.

        Returns:
            The full repr string.
        """
        fields = self.field_extractor.extract_fields(inst)
        repr_str = self.generate_str(inst, fields)
        return repr_str

    @staticmethod
    def resolve_field_extractor(
        class_or_inst: Class | Instance,
        include: Sequence[str] | None = None
    ) -> type[BaseFieldExtractor]:
        """
        Select the appropriate field extractor based on object type.

        Parameters:
            class_or_inst: Class or instance to inspect.
            include: Optional inclusion list to force extractor type.

        Returns:
            A subclass of BaseFieldExtractor.

        Raises:
            TypeError: If the type does not define `__dict__` or `__slots__`.
        """
        if include is not None:
            return IncludedFieldExtractor

        class_: Class = class_or_inst if isinstance(class_or_inst, type) else type(class_or_inst)

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
        """
        Injects a custom __repr__ method into the given class.

        Parameters:
            class_: Target class to inject __repr__ into.
            include: List of attribute names to include in repr.
            exclude: List of attribute names to exclude.
            compute: Mapping of computed field names to callables.
            format_spec: Format strings for attribute values.
            exclude_private: Whether to skip private fields.
            skip_missing: Whether to ignore missing attributes.
            repr_config: Optional config for reprlib.Repr.
            delimiters: A tuple of two strings used to surround the entire `repr` body. For example, `('(', ')')` would produce `ClassName(field=value)` style.
        """
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

        def _repr(inst: Instance):
            return kwrepr.generate(inst)

        _repr.__qualname__ = f"{class_.__name__}.__repr__"

        class_.__repr__ = _repr
