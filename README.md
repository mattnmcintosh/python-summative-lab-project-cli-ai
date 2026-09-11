# Project Management Tool CLI

A modular, object-oriented Python command-line interface (CLI) application designed to manage users, projects, and tasks with local JSON data persistence, rich terminal output, and local AI-powered project analysis.

## Project Overview

This application provides an administrative system for managing development teams, tracking projects, assigning tasks, and evaluating project health using a local Large Language Model via Ollama. It demonstrates a strict separation of concerns across presentation, business logic, and external services.

## Setup Instructions

1. Ensure Python 3.10 or higher is installed on your system.
2. Clone or download the project repository to your local machine.
3. Open your terminal and navigate to the project root directory.

## Dependency Installation Instructions

Install the required external packages (`rich`, `ollama`, and `pytest`) using pip:

```bash
pip install -r requirements.txt
```

Alternatively, if managing via Pipenv:

```bash
pipenv install
pipenv install --dev pytest
```

## How to Run the CLI

Execute commands from the project root directory by invoking the main script with Python:

```bash
python main.py [command] [options]
```

## Example Commands

### Add a User
```bash
python main.py add-user --name "Alex" --email "alex@example.com"
```

### List All Users
```bash
python main.py list-users
```

### Add a Project to a User
```bash
python main.py add-project --user "Alex" --title "CLI Tool" --description "Build project tracker" --due-date "2026-12-31"
```

### List Projects
```bash
python main.py list-projects --user "Alex"
```

### Add a Task to a Project
```bash
python main.py add-task --project "CLI Tool" --title "Implement add-task command" --assigned-to "Alex"
```

### Complete a Task
```bash
python main.py complete-task --project "CLI Tool" --task-id 1
```

### Generate AI Project Summary
```bash
python main.py summarize-project --project "CLI Tool"
```

## Explanation of the File Structure

* `main.py`: CLI entry point handling argument parsing (`argparse`), subcommand dispatch, and rich tabular output.
* `models/`: Contains core object-oriented domain classes:
  * `person.py`: Base class providing shared attributes and validation.
  * `user.py`: Manages user profiles and project collections (one-to-many relationship).
  * `project.py`: Manages project metadata and task collections (one-to-many relationship).
  * `task.py`: Tracks task assignment, status (`Pending`, `In Progress`, `Completed`), and unique identifiers.
* `services/`: Encapsulates state persistence and external communications:
  * `storage_service.py`: Handles reading, writing, and exception-safe JSON serialization/deserialization.
  * `ai_client.py`: Reusable client class managing communication with the local Ollama LLM.
* `data/`: Stores local persistence files (`project_tracker.json`).
* `testing/`: Houses the Pytest automated unit test suite.

## Overview of Features

* **Object-Oriented Design:** Utilizes class inheritance (`Person` -> `User`), encapsulation via `@property` setters with data validation, and class-level ID counters.
* **Rich Terminal Output:** Renders clean, colorized tables and status indicators using the `rich` library.
* **Local Data Persistence:** Automatically saves system state to JSON and gracefully recovers from missing or malformed data files.
* **Comprehensive Test Coverage:** Unit and mock tests verifying model validations, storage handling, and CLI workflows.

## Description of the External Service or AI Client Feature

The application includes an AI integration layer managed by the `AIClient` class inside `services/ai_client.py`. When a user invokes the `summarize-project` command, the application packages the target project's title, description, due date, and task details into a structured prompt. This payload is transmitted locally to an Ollama LLM instance, which analyzes the data to return an operational summary, risk identification notes, and recommended next steps. Service errors are caught safely and displayed as readable error messages without crashing the application.

## Setup Needed for the External Service

1. Install Ollama locally from [ollama.com](https://ollama.com).
2. Download the default model used by the application:
   ```bash
   ollama pull llama3.2
   ```
3. Ensure the local Ollama background service is active (`ollama serve` or running via the Ollama desktop application) so that local socket connections on port `11434` are accessible.

## Known Issues or Limitations

* The AI summary feature requires an active local Ollama background service; if Ollama is closed or unresponsive, the command will catch the error and output a connection warning rather than crashing.
* Data persistence is handled locally in a single JSON file; concurrent multi-process writes are not supported.