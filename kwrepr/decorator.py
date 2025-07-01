from collections.abc import Callable, Mapping, Sequence
from typing import Any, overload

from .types import Class
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
    show_private: bool = False,
    skip_missing: bool = False,
    repr_config: Mapping[str, Any] | None = None
) -> Callable[[Class], Class] | Class:

    def inject_repr(class_: Class) -> None:
        KWRepr.inject_repr(
            class_=class_,
            include=include,
            exclude=exclude,
            show_private=show_private,
            skip_missing=skip_missing,
            repr_config=repr_config
        )

    if class_ is not None:
        inject_repr(class_)
        return class_

    def wrapper(class_: Class) -> Class:
        inject_repr(class_)
        return class_

    return wrapper
