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
