class Task:
    """Represents an individual task within a project."""
    
    _id_counter = 1

    def __init__(self, title: str, status: str = "Pending", assigned_to: str = None, task_id: int = None):
        if task_id is not None:
            self._id = task_id
            Task._id_counter = max(Task._id_counter, task_id + 1)
        else:
            self._id = Task._id_counter
            Task._id_counter += 1
        
        self._title = title
        self._status = status
        self._assigned_to = assigned_to

    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        valid_statuses = ["Pending", "In Progress", "Completed"]
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        self._status = value

    @property
    def assigned_to(self) -> str:
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value: str):
        self._assigned_to = value

    def mark_complete(self):
        """Marks the task as completed."""
        self._status = "Completed"

    def to_dict(self) -> dict:
        """Serializes task instance to a dictionary for JSON storage."""
        return {
            "id": self._id,
            "title": self._title,
            "status": self._status,
            "assigned_to": self._assigned_to
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Reconstructs a Task instance from a dictionary."""
        return cls(
            title=data["title"],
            status=data.get("status", "Pending"),
            assigned_to=data.get("assigned_to"),
            task_id=data.get("id")
        )

    def __str__(self) -> str:
        status_icon = "✅" if self._status == "Completed" else "⏳"
        assignee = f" (Assigned to: {self._assigned_to})" if self._assigned_to else ""
        return f"[{self._id}] {status_icon} {self._title}{assignee}"