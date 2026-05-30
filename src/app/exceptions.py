"""Application exceptions for API / UI boundaries."""


class PreferenceValidationError(Exception):
    """User preference validation failed (HTTP 400)."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        suggestions: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.field = field
        self.suggestions = list(suggestions or [])

    def to_dict(self) -> dict:
        payload: dict = {"message": self.message}
        if self.field:
            payload["field"] = self.field
        if self.suggestions:
            payload["suggestions"] = self.suggestions
        return payload
