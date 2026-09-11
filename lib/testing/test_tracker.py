import pytest
from models.person import Person
from models.task import Task
from models.project import Project
from models.user import User
from lib.utils import storage


# --- Tests for Person & User Models ---

def test_person_validation():
    person = Person("Alice", "alice@example.com")
    assert person.name == "Alice"
    assert person.email == "alice@example.com"

    # Test invalid setters
    with pytest.raises(ValueError):
        person.name = ""
    with pytest.raises(ValueError):
        person.email = "invalid-email"


def test_user_creation_and_relationships():
    user = User("Bob", "bob@example.com")
    assert user.name == "Bob"
    assert len(user.projects) == 0

    project = Project(title="Backend Migration", description="Migrate API to FastAPI")
    user.add_project(project)

    assert len(user.projects) == 1
    assert user.get_project_by_title("backend migration") == project
    assert user.get_project_by_title("Nonexistent") is None


def test_user_serialization():
    user = User("Charlie", "charlie@example.com")
    proj = Project(title="CLI Tool", due_date="2026-12-31")
    task = Task(title="Write tests", assigned_to="Charlie")
    proj.add_task(task)
    user.add_project(proj)

    data = user.to_dict()
    assert data["name"] == "Charlie"
    assert len(data["projects"]) == 1
    assert data["projects"][0]["title"] == "CLI Tool"
    assert data["projects"][0]["tasks"][0]["title"] == "Write tests"

    # Reconstruct from dict
    reconstructed = User.from_dict(data)
    assert reconstructed.name == "Charlie"
    assert len(reconstructed.projects) == 1
    assert reconstructed.projects[0].title == "CLI Tool"
    assert reconstructed.projects[0].tasks[0].status == "Pending"


# --- Tests for Task & Project Models ---

def test_task_status_and_completion():
    task = Task(title="Fix bug")
    assert task.status == "Pending"

    task.status = "In Progress"
    assert task.status == "In Progress"

    with pytest.raises(ValueError):
        task.status = "InvalidStatus"

    task.mark_complete()
    assert task.status == "Completed"


def test_project_task_management():
    project = Project(title="Alpha", description="Test project")
    task1 = Task(title="Task 1")
    task2 = Task(title="Task 2")

    project.add_task(task1)
    project.add_task(task2)

    assert len(project.tasks) == 2
    assert project.get_task_by_id(task1.id) == task1
    assert project.get_task_by_id(999) is None


# --- Tests for Storage Utilities ---

def test_storage_save_and_load(tmp_path, monkeypatch):
    # Setup temporary storage file path
    d = tmp_path / "data"
    d.mkdir()
    f = d / "project_tracker.json"
    
    monkeypatch.setattr(storage, "DATA_DIR", str(d))
    monkeypatch.setattr(storage, "DATA_FILE", str(f))

    user = User("Diana", "diana@example.com")
    proj = Project(title="Analytics", due_date="2026-10-01")
    user.add_project(proj)

    users_dict = {"Diana": user}
    
    # Save data
    storage.save_data(users_dict)
    assert f.exists()

    # Load data back
    loaded_users = storage.load_data()
    assert "Diana" in loaded_users
    assert loaded_users["Diana"].email == "diana@example.com"
    assert len(loaded_users["Diana"].projects) == 1
    assert loaded_users["Diana"].projects[0].title == "Analytics"


# --- Tests for CLI Functions (via Mocking / Imports) ---

def test_cli_add_user_workflow(monkeypatch):
    import main
    
    # Mock global users dictionary and save_data
    monkeypatch.setattr(main, "users", {})
    saved = []
    monkeypatch.setattr(main, "save_data", lambda u: saved.append(u))

    class Args:
        name = "Eve"
        email = "eve@example.com"

    main.add_user(Args())

    assert "Eve" in main.users
    assert len(saved) == 1
    assert main.users["Eve"].email == "eve@example.com"


def test_cli_add_task_workflow(monkeypatch):
    import main

    user = User("Frank", "frank@example.com")
    proj = Project(title="Dashboard")
    user.add_project(proj)

    monkeypatch.setattr(main, "users", {"Frank": user})
    saved = []
    monkeypatch.setattr(main, "save_data", lambda u: saved.append(u))

    class Args:
        project = "Dashboard"
        title = "Design UI"
        assigned_to = "Frank"

    main.add_task(Args())

    assert len(proj.tasks) == 1
    assert proj.tasks[0].title == "Design UI"
    assert proj.tasks[0].assigned_to == "Frank"
    assert len(saved) == 1