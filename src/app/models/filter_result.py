"""Filter service output (Component Design → 4. Filter Service)."""

from pydantic import BaseModel, Field

from app.models.restaurant import Restaurant


class FilterResult(BaseModel):
    candidates: list[Restaurant] = Field(default_factory=list)
    total_before_cap: int = 0
    applied_filters: list[str] = Field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.candidates) == 0
