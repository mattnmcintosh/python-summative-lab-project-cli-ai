class Person:
    """Base class representing a generic person in the system."""

    def __init__(self, name: str, email: str):
        self._name = name
        self._email = email

    @property
    def name(self) -> str:
        """Get the person's name."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the person's name with validation."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def email(self) -> str:
        """Get the person's email."""
        return self._email

    @email.setter
    def email(self, value: str):
        """Set the person's email with basic format validation."""
        if not value or "@" not in value:
            raise ValueError("Invalid email address format.")
        self._email = value.strip()