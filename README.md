# kwrepr

kwrepr automatically generates keyword-style `__repr__` methods for your Python classes.

It lets you control which fields appear, add computed fields, format output, and handle private fields easily.

Use it as a decorator or inject manually.

---

## Features

- Easily add keyword-style `__repr__` to classes via decorator or manual injection  
- Specify attributes to include or exclude (cannot use both simultaneously)  
- Add computed fields with callables evaluated at repr time  
- Format fields using standard format specifiers  
- Exclude private fields (names starting with `_`) by default, configurable with `exclude_private`  
- Optionally skip missing attributes instead of raising errors  
- Customize output delimiters (default parentheses)  
- Pass `repr_config` to customize how field values are represented using Python’s `reprlib.Repr`

---

## Usage

Basic decorator:

```python
from kwrepr import apply_kwrepr

@apply_kwrepr
class User:
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self._password = password

print(User(1, "Alice", "secret"))
# User(id=1, name='Alice')
```

Private fields excluded by default.

---

## Include private fields:

```python
@apply_kwrepr(exclude_private=False)
class User:
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self._password = password

print(User(1, "Alice", "secret"))
# User(id=1, name='Alice', _password='secret')
```
---

## Using include and exclude

- You cannot use both `include` and `exclude` at the same time.
- By default, private fields (fields starting with `_`) are excluded.
- To include private fields, set `exclude_private=False`.
- If `include` is used, it overrides both `exclude` and `exclude_private`.

### Example using `include`
------------------------

```python
from kwrepr import apply_kwrepr

@apply_kwrepr(include=["id", "name", "_token"])
class User:
    def __init__(self, id, name, password, token):
        self.id = id
        self.name = name
        self._password = password
        self._token = token

print(User(2, "Bob", "hunter2", "xyz789"))
# Output: User(id=2, name='Bob', _token='xyz789')
```

### Example using `exclude`
------------------------

```python
from kwrepr import apply_kwrepr

@apply_kwrepr(exclude=["_password"], exclude_private=False)
class User:
    def __init__(self, id, name, password, token):
        self.id = id
        self.name = name
        self._password = password
        self._token = token

print(User(1, "Alice", "secret", "abc123"))
# Output: User(id=1, name='Alice', _token='abc123')
```
---

## Computed fields:

```python
from pathlib import Path
from datetime import datetime

@apply_kwrepr(
    compute={
        "size": lambda self: f"{self.size:,} bytes",  # self is bound to the instance of FileMeta.
        "created_at": lambda self: self.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
)
class FileMeta:
    def __init__(self, path: Path):
        stat = path.stat()
        self.path = path
        self.size = stat.st_size
        self.created_at = datetime.fromtimestamp(stat.st_ctime)
```

---

## Field formatting:

```python
@apply_kwrepr(format_spec={"score": ".2f"})
class Player:
    def __init__(self, score):
        self.score = score

print(Player(92.756))
# Player(score=92.76)
```

---

## Manual injection:

```python
from kwrepr import KWRepr

class MyClass:
    def __init__(self, x, y, secret):
        self.x = x
        self.y = y
        self._secret = secret

KWRepr.inject_repr(MyClass)

print(MyClass(1, 2, "hidden"))
# MyClass(x=1, y=2)
```

---

## License

MIT
