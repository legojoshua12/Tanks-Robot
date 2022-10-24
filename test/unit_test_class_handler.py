from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class User:
    id: int
    name: str
