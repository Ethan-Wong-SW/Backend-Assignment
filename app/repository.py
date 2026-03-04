import json
from pathlib import Path
from typing import Iterable

from app.models import Contact, ContactCreate


class ContactRepository:
    def __init__(self, contacts: Iterable[Contact]) -> None:
        self._contacts: dict[int, Contact] = {contact.id: contact for contact in contacts}

    @classmethod
    def from_json_file(cls, file_path: Path) -> "ContactRepository":
        raw_data = json.loads(file_path.read_text(encoding="utf-8"))
        contacts = [Contact.model_validate(item) for item in raw_data]
        return cls(contacts)

    def get_by_id(self, contact_id: int) -> Contact | None:
        return self._contacts.get(contact_id)

    def add(self, contact: ContactCreate) -> Contact:
        next_id = max(self._contacts.keys(), default=0) + 1
        new_contact = Contact(id=next_id, **contact.model_dump())
        self._contacts[new_contact.id] = new_contact
        return new_contact

    def delete(self, contact_id: int) -> Contact | None:
        return self._contacts.pop(contact_id, None)
