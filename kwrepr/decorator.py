from collections.abc import Callable, Mapping, Sequence
from typing import Any, overload

from .types import Class, Instance
from .field_extractors import BaseFieldExtractor
from .kwrepr import KWRepr


@overload
def apply_kwrepr(class_: Class) -> Class: ...

@overload
def apply_kwrepr() -> Callable[[Class], Class]: ...

def apply_kwrepr(
    class_: Class | None = None,
    *,
    include: Sequence[str] | None = None,
    exclude: Sequence[str] | None = None,
    compute: Mapping[str, Callable[[Instance], Any]] | None = None,
    format_spec: Mapping[str, str] | None = None,
    exclude_private: bool = True,
    skip_missing: bool = False,
    repr_config: Mapping[str, Any] | None = None,
    delimiters: tuple[str, str] | None = None
) -> Callable[[Class], Class] | Class:
    """
    A decorator (or decorator factory) that injects a custom __repr__ method into a class.

    Can be used with or without parentheses:
        @apply_kwrepr
        class MyClass: ...

        @apply_kwrepr(...)
        class MyClass: ...

    Parameters:
        class_: The class to decorate, if used without parentheses.
        include: List of field names to include in __repr__. If None, all fields are included by default.
        exclude: List of field names to exclude from __repr__.
        compute: Fields to compute dynamically at __repr__ time.
        format_spec: Optional format specifiers (like ".2f", etc) per field name.
        exclude_private: If True, excludes fields starting with an underscore (default: True).
        skip_missing: If True, skips fields that are missing or raise on access (default: False).
        repr_config: Extra configuration passed to KWRepr.
        delimiters: Optional delimiters to wrap the full __repr__ string.

    Returns:
        Callable[[type], type] | type: The decorated class or a decorator function.

    Raises:
        Any exceptions raised by `KWRepr.inject_repr`.

    Notes:
        This is a thin wrapper around `KWRepr.inject_repr`. It exists for syntactic sugar and usability.
    """

    def inject_repr(class_: Class) -> None:
        KWRepr.inject_repr(
            class_=class_,
            include=include,
            exclude=exclude,
            compute=compute,
            format_spec=format_spec,
            exclude_private=exclude_private,
            skip_missing=skip_missing,
            repr_config=repr_config,
            delimiters=delimiters
        )

    def wrapper(class_: Class) -> Class:
        inject_repr(class_)
        return class_

    if class_ is not None:
        inject_repr(class_)
        return class_

    return wrapper
