import pytest
from unittest.mock import patch
from services.ai_client import AIClient
from models.project import Project
from models.task import Task
from models.user import User


def test_ai_client_summarize_success():
    client = AIClient(model_name="test-model")
    
    mock_response_obj = type("Obj", (object,), {
        "message": type("Msg", (object,), {"content": "Mocked project summary and risks."})
    })()

    with patch("services.ai_client.ollama.chat", return_value=mock_response_obj) as mock_chat:
        project_data = {
            "title": "Test Project",
            "description": "A test description",
            "due_date": "2026-12-31",
            "tasks": [{"title": "Task 1", "status": "Pending", "assigned_to": "Alex"}]
        }
        
        result = client.summarize_project(project_data)
        
        assert result == "Mocked project summary and risks."
        mock_chat.assert_called_once()
        args, kwargs = mock_chat.call_args
        assert kwargs["model"] == "test-model"
        assert len(kwargs["messages"]) == 1


def test_ai_client_summarize_failure():
    client = AIClient()

    with patch("services.ai_client.ollama.chat", side_effect=Exception("Connection refused")):
        with pytest.raises(RuntimeError) as exc_info:
            client.summarize_project({"title": "Broken Project", "tasks": []})
        
        assert "Failed to connect to Ollama" in str(exc_info.value)


def test_cli_summarize_handler_not_found(capsys, monkeypatch):
    import main
    monkeypatch.setattr(main, "users", {})

    class Args:
        project = "Missing Project"

    main.summarize_project(Args())
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_cli_summarize_handler_success(monkeypatch):
    import main
    user = User("Alex", "alex@example.com")
    proj = Project(title="CLI Tool")
    user.add_project(proj)
    
    monkeypatch.setattr(main, "users", {"Alex": user})
    
    with patch("services.ai_client.AIClient.summarize_project", return_value="Summary Output"):
        class Args:
            project = "CLI Tool"
        
        # Should execute successfully without throwing exceptions
        main.summarize_project(Args())