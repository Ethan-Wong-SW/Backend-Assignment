import re

from pydantic import BaseModel, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$")


class ContactBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(
        min_length=5,
        max_length=255,
        json_schema_extra={"example": "test@mail.com"},
    )
    phone: str = Field(
        min_length=8,
        max_length=20,
        json_schema_extra={"example": "+65 9123 4567"},
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_and_validate_email(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Email must be a string")
        normalized = value.strip().lower()
        if not EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError("Email must follow a template like test@mail.com")
        return normalized

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_and_validate_sg_phone(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Phone must be a string")

        raw_phone = value.strip()
        if not re.fullmatch(r"[0-9+\- ]+", raw_phone):
            raise ValueError("Phone contains invalid characters")

        digits_only = re.sub(r"\D", "", raw_phone)

        # Accept both local and country-code forms, then store as +65 XXXX XXXX.
        if len(digits_only) == 10 and digits_only.startswith("65"):
            digits_only = digits_only[2:]

        if len(digits_only) != 8 or digits_only[0] not in {"8", "9"}:
            raise ValueError(
                "Phone must be a Singapore mobile number with 8 digits starting with 8 or 9"
            )

        return f"+65 {digits_only[:4]} {digits_only[4:]}"


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int = Field(gt=0)
