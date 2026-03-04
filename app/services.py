from app.models import ContactCreate


class ContactProcessor:
    """Simple service wired through dependency injection for new contacts."""

    def process(self, contact: ContactCreate) -> ContactCreate:
        return ContactCreate(
            name=" ".join(contact.name.split()),
            email=contact.email,
            phone=contact.phone,
        )
