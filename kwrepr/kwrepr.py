from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import reprlib

from types import MethodType
from typing import Any

from .types import Class, Instance


class KWReprDescriptor:
    def __init__(self, generate: Callable[[Instance], str]) -> None:
        self.generate = generate

    def __get__(self, instance: Instance | None, owner: Class) -> Instance | Callable[[], str]:
        if instance is None:
            return self.generate

        return MethodType(self.generate, instance)


class KWRepr:
    """
    Keyword-based representation (__repr__) on objects.
    """
    def __init__(
        self,
        *,
        include: Sequence[str] | None = None,
        exclude: Sequence[str] | None = None,
        show_private: bool = False,
        skip_missing: bool = False,
        repr_config: Mapping[str, Any] | None = None
    ) -> None:
        """
        Initiate class KWRepr.

        Parameters:
            include: Names of attributes to only include.
            exclude: Names of attributes to only exclude.
            show_private: Whether to show private attributes.
            skip_missing: Whether to skip missing attributes.
            repr_config: class reprlib.Repr init parameters.

        Raises:
            ValueError:
                If specified both include and exclude parameters.
        """
        if include is not None and exclude is not None:
            raise ValueError("Cannot specify both 'include' and 'exclude'")

        self.include = include or []
        self.exclude = exclude or []
        self.show_private = show_private
        self.skip_missing = skip_missing

        self._repr = reprlib.Repr(**(repr_config or {}))

    def extract_included_fields(self, inst: Instance) -> list[tuple[str, Any]]:
        fields: list[tuple[str, Any]] = []
        for field in self.include:
            if isinstance(field, tuple):
                name, callback = field
                value = callback(inst)
                if ":" in name:
                    fmt_spec = name.split(":", 1)
                    value = format(value, fmt_spec)
                fields.append((name, value))
            else:
                name = field
                if name.startswith("__") and not name.endswith("__"):
                    name = f"_{type(inst).__name__}{name}"

                if ":" in name:
                    name, fmt_spec = name.split(":", 1)
                try:
                    value = getattr(inst, name)
                except AttributeError:
                    if not self.skip_missing:
                        raise AttributeError(f"Included attribute not found: {name}")
                else:
                    if fmt_spec:
                        value = format(value, fmt_spec)
                    fields.append((name, value))

        return fields

    def extract_dict_fields(self, inst: Instance) -> list[tuple[str, Any]]:
        if self.include:
            return self.extract_included_fields(inst)

        fields: list[tuple[str, Any]] = []
        for name, value in vars(inst).items():
            if name in self.exclude:
                continue
            if name.startswith("_") and not self.show_private:
                continue

            fields.append((name, value))

        return fields

    def extract_slots_fields(self, inst: Instance) -> list[tuple[str, Any]]:
        if self.include:
            return self.extract_included_fields(inst)

        fields: list[tuple[str, Any]] = []
        for name in type(inst).__slots__:
            if name in self.exclude:
                continue
            if name.startswith("_") and not self.show_private:
                continue
            if name.startswith("__") and not name.endswith("__"):
                name = f"_{type(inst).__name__}{name}"

            value = getattr(inst, name)
            fields.append((name, value))

        return fields

    def extract_fields(self, inst: Instance) -> list[tuple[str, Any]]:
        if hasattr(inst, "__dict__"):
            return self.extract_dict_fields(inst)
        elif hasattr(inst, "__slots__"):
            return self.extract_slots_fields(inst)
        else:
            raise TypeError(f"{type(inst).__name__} must define either __dict__ or __slots__")

    def generate_str(self, inst: Instance, fields: Sequence[tuple[str, Any]]) -> str:
        name = type(inst).__qualname__
        body = ", ".join(
            f"{name}={self._repr.repr(value)}"
            for name, value in fields
        )
        kwrepr_str = f"{name}({body})"
        return kwrepr_str

    def generate(self, inst: Instance) -> str:
        fields = self.extract_fields(inst)
        repr_str = self.generate_str(inst, fields)
        return repr_str

    def __call__(self, inst: Instance) -> str:
        return self.generate(inst)

    @classmethod
    def inject_repr(
        cls,
        class_: Class,
        include: Sequence[str] | None = None,
        exclude: Sequence[str] | None = None,
        show_private: bool = False,
        skip_missing: bool = False,
        repr_config: Mapping[str, Any] | None = None
    ) -> None:
        kwrepr: KWRepr = cls(
            include=include,
            exclude=exclude,
            show_private=show_private,
            skip_missing=skip_missing,
            repr_config=repr_config
        )

        class_.__repr__ =  KWReprDescriptor(kwrepr.generate)
