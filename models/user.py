from models.person import Person
from models.project import Project

class User(Person):
    """Represents a system user inheriting from Person, managing multiple projects."""
    
    _id_counter = 1

    def __init__(self, name: str, email: str, user_id: int = None, projects=None):
        super().__init__(name, email)
        if user_id is not None:
            self._id = user_id
            User._id_counter = max(User._id_counter, user_id + 1)
        else:
            self._id = User._id_counter
            User._id_counter += 1
        
        self._projects = projects if projects is not None else []

    @property
    def id(self) -> int:
        return self._id

    @property
    def projects(self) -> list:
        return self._projects

    def add_project(self, project: Project):
        """Adds a project to the user's collection."""
        self._projects.append(project)

    def get_project_by_title(self, title: str) -> Project:
        """Retrieves a project by matching its title case-insensitively."""
        for proj in self._projects:
            if proj.title.lower() == title.lower():
                return proj
        return None

    def to_dict(self) -> dict:
        """Serializes user and their nested projects/tasks to a dictionary."""
        return {
            "id": self._id,
            "name": self._name,
            "email": self._email,
            "projects": [proj.to_dict() for proj in self._projects]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Reconstructs a User instance from a dictionary."""
        projects = [Project.from_dict(p_data) for p_data in data.get("projects", [])]
        return cls(
            name=data["name"],
            email=data["email"],
            user_id=data.get("id"),
            projects=projects
        )

    def __str__(self) -> str:
        return f"👤 User: {self._name} <{self._email}> (Projects: {len(self._projects)})"