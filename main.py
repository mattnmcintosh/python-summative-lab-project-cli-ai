import argparse
from rich.console import Console
from rich.table import Table

from models.user import User
from models.project import Project
from models.task import Task
from lib.utils.storage import load_data, save_data

from services.ai_client import AIClient

console = Console()

# Global in-memory storage loaded from JSON
users = load_data()

def add_user(args):
    """CLI handler to add a new user."""
    name = args.name
    email = args.email
    
    if name in users:
        console.print(f"[bold red]Error:[/bold red] User '{name}' already exists.")
        return

    try:
        new_user = User(name=name, email=email)
        users[name] = new_user
        save_data(users)
        console.print(f"[bold green]✔ Success:[/bold green] User '{name}' added successfully.")
    except ValueError as e:
        console.print(f"[bold red]Input Error:[/bold red] {e}")

def list_users(args):
    """CLI handler to list all system users."""
    if not users:
        console.print("[yellow]No users found in the tracker.[/yellow]")
        return

    table = Table(title="System Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="green")
    table.add_column("Projects Count", style="blue")

    for user in users.values():
        table.add_row(str(user.id), user.name, user.email, str(len(user.projects)))

    console.print(table)

def add_project(args):
    """CLI handler to add a project to a specific user."""
    user_name = args.user
    title = args.title
    description = args.description
    due_date = args.due_date

    if user_name not in users:
        console.print(f"[bold red]Error:[/bold red] User '{user_name}' not found.")
        return

    user = users[user_name]
    if user.get_project_by_title(title):
        console.print(f"[bold red]Error:[/bold red] Project '{title}' already exists for user '{user_name}'.")
        return

    project = Project(title=title, description=description, due_date=due_date)
    user.add_project(project)
    save_data(users)
    console.print(f"[bold green]✔ Success:[/bold green] Project '{title}' added to user '{user_name}'.")

def list_projects(args):
    """CLI handler to list projects for a specific user or all users."""
    target_user = args.user

    if target_user:
        if target_user not in users:
            console.print(f"[bold red]Error:[/bold red] User '{target_user}' not found.")
            return
        user_list = [users[target_user]]
    else:
        user_list = list(users.values())

    if not user_list:
        console.print("[yellow]No users or projects found.[/yellow]")
        return

    for user in user_list:
        console.print(f"\n[bold cyan]👤 {user.name}'s Projects:[/bold cyan]")
        if not user.projects:
            console.print("  [dim]No projects assigned.[/dim]")
            continue
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Project ID")
        table.add_column("Title")
        table.add_column("Due Date")
        table.add_column("Tasks")

        for proj in user.projects:
            completed_tasks = sum(1 for t in proj.tasks if t.status == "Completed")
            table.add_row(
                str(proj.id),
                proj.title,
                proj.due_date or "N/A",
                f"{completed_tasks}/{len(proj.tasks)} completed"
            )
        console.print(table)

def add_task(args):
    """CLI handler to add a task to a project."""
    project_title = args.project
    title = args.title
    assigned_to = args.assigned_to

    # Search across all users for the target project
    found_project = None
    for user in users.values():
        proj = user.get_project_by_title(project_title)
        if proj:
            found_project = proj
            break

    if not found_project:
        console.print(f"[bold red]Error:[/bold red] Project '{project_title}' not found.")
        return

    task = Task(title=title, assigned_to=assigned_to)
    found_project.add_task(task)
    save_data(users)
    console.print(f"[bold green]✔ Success:[/bold green] Task '{title}' added to project '{project_title}'.")

def complete_task(args):
    """CLI handler to mark a project task as complete."""
    project_title = args.project
    task_id = args.task_id

    found_project = None
    for user in users.values():
        proj = user.get_project_by_title(project_title)
        if proj:
            found_project = proj
            break

    if not found_project:
        console.print(f"[bold red]Error:[/bold red] Project '{project_title}' not found.")
        return

    task = found_project.get_task_by_id(task_id)
    if not task:
        console.print(f"[bold red]Error:[/bold red] Task with ID {task_id} not found in project '{project_title}'.")
        return

    task.mark_complete()
    save_data(users)
    console.print(f"[bold green]✔ Success:[/bold green] Task ID {task_id} ('{task.title}') marked as completed.")

def summarize_project(args):
    """CLI handler to generate an AI summary for a project."""
    project_title = args.project

    found_project = None
    for user in users.values():
        proj = user.get_project_by_title(project_title)
        if proj:
            found_project = proj
            break

    if not found_project:
        console.print(f"[bold red]Error:[/bold red] Project '{project_title}' not found.")
        return

    console.print(f"[cyan]🤖 Generating AI project summary for '{project_title}' using Ollama...[/cyan]")
    
    ai_client = AIClient()
    try:
        summary = ai_client.summarize_project(found_project.to_dict())
        console.print(f"\n[bold green]Project Summary & Recommendations:[/bold green]\n{summary}")
    except RuntimeError as e:
        console.print(f"[bold red]AI Service Error:[/bold red] {e}")

def main():
    parser = argparse.ArgumentParser(description="Command-Line Project Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Add User Parser
    parser_add_user = subparsers.add_parser("add-user", help="Add a new user")
    parser_add_user.add_argument("--name", required=True, help="User name")
    parser_add_user.add_argument("--email", required=True, help="User email address")
    parser_add_user.set_defaults(func=add_user)

    # List Users Parser
    parser_list_users = subparsers.add_parser("list-users", help="List all system users")
    parser_list_users.set_defaults(func=list_users)

    # Add Project Parser
    parser_add_proj = subparsers.add_parser("add-project", help="Add a project to a user")
    parser_add_proj.add_argument("--user", required=True, help="Username owner")
    parser_add_proj.add_argument("--title", required=True, help="Project title")
    parser_add_proj.add_argument("--description", default="", help="Project description")
    parser_add_proj.add_argument("--due-date", default="", help="Project due date")
    parser_add_proj.set_defaults(func=add_project)

    # List Projects Parser
    parser_list_proj = subparsers.add_parser("list-projects", help="List user projects")
    parser_list_proj.add_argument("--user", help="Filter by specific username")
    parser_list_proj.set_defaults(func=list_projects)

    # Add Task Parser
    parser_add_task = subparsers.add_parser("add-task", help="Add a task to a project")
    parser_add_task.add_argument("--project", required=True, help="Project title")
    parser_add_task.add_argument("--title", required=True, help="Task title")
    parser_add_task.add_argument("--assigned-to", help="Person assigned to task")
    parser_add_task.set_defaults(func=add_task)

    # Complete Task Parser
    parser_complete_task = subparsers.add_parser("complete-task", help="Mark a task as complete")
    parser_complete_task.add_argument("--project", required=True, help="Project title")
    parser_complete_task.add_argument("--task-id", type=int, required=True, help="Task numeric ID")
    parser_complete_task.set_defaults(func=complete_task)

    # Summarize Parser
    parser_summarize = subparsers.add_parser("summarize-project", help="Generate an AI summary for a project")
    parser_summarize.add_argument("--project", required=True, help="Project title")
    parser_summarize.set_defaults(func=summarize_project)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()