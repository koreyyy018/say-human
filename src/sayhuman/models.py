"""Validated records, without runtime dependencies."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Concept:
    term: str
    aliases: tuple[str, ...]
    technical: str
    human: str
    business: str
    caveat: str

    @classmethod
    def from_dict(cls, data: dict) -> "Concept":
        fields = ("term", "technical", "human", "business", "caveat")
        if not all(isinstance(data.get(key), str) and data[key].strip() for key in fields):
            raise ValueError(f"Invalid concept record: {data.get('term', '<unnamed>')}")
        aliases = data.get("aliases", [])
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            raise ValueError("aliases must be a string list")
        return cls(*(data[k] for k in fields[:1]), tuple(aliases), *(data[k] for k in fields[1:]))
