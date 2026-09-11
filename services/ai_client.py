import ollama

class AIClient:
    """Reusable service client for communicating with local Ollama models."""

    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

    def summarize_project(self, project_data: dict) -> str:
        """Sends project and task details to Ollama to generate a summary, risks, and next steps."""
        # Format project details into a clear prompt
        tasks_summary = "\n".join([
            f"- [{t['status']}] {t['title']} (Assigned to: {t['assigned_to'] or 'Unassigned'})"
            for t in project_data.get("tasks", [])
        ]) or "No tasks recorded yet."

        prompt = (
            f"Analyze the following project and provide a concise operational summary, "
            f"highlighting any potential risks and suggesting the next best step:\n\n"
            f"Project Title: {project_data.get('title')}\n"
            f"Description: {project_data.get('description', 'N/A')}\n"
            f"Due Date: {project_data.get('due_date', 'N/A')}\n"
            f"Tasks:\n{tasks_summary}"
        )

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            # Extract content based on response object/dict shape
            if hasattr(response, "message"):
                return response.message.content
            return response["message"]["content"]
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to Ollama. Please check that Ollama is running locally. (Error: {e})"
            )