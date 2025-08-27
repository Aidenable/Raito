from dataclasses import dataclass

__all__ = ("RoleData",)


@dataclass
class RoleData:
    slug: str
    name: str
    description: str
    emoji: str

    @property
    def label(self) -> str:
        return f"{self.emoji} {self.name}"
