from models.task import Task

class Project:
    """Represents a project containing a collection of tasks."""
    
    _id_counter = 1

    def __init__(self, title: str, description: str = "", due_date: str = "", project_id: int = None, tasks=None):
        if project_id is not None:
            self._id = project_id
            Project._id_counter = max(Project._id_counter, project_id + 1)
        else:
            self._id = Project._id_counter
            Project._id_counter += 1

        self._title = title
        self._description = description
        self._due_date = due_date
        self._tasks = tasks if tasks is not None else []

    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def due_date(self) -> str:
        return self._due_date

    @property
    def tasks(self) -> list:
        return self._tasks

    def add_task(self, task: Task):
        """Adds a task to the project's task list."""
        self._tasks.append(task)

    def get_task_by_id(self, task_id: int) -> Task:
        """Retrieves a task by its unique ID."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def to_dict(self) -> dict:
        """Serializes project and its nested tasks to a dictionary."""
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "due_date": self._due_date,
            "tasks": [task.to_dict() for task in self._tasks]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Reconstructs a Project instance from a dictionary."""
        tasks = [Task.from_dict(t_data) for t_data in data.get("tasks", [])]
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date", ""),
            project_id=data.get("id"),
            tasks=tasks
        )

    def __str__(self) -> str:
        completed = sum(1 for t in self._tasks if t.status == "Completed")
        total = len(self._tasks)
        return f"📁 Project: {self._title} (Due: {self._due_date or 'N/A'}) - [{completed}/{total} tasks done]"