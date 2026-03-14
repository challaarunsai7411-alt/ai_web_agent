class TaskMemory:
    def __init__(self):
        # A list to store the chronological history of actions
        self.history = []

    def add_action(self, step: int, action_dict: dict):
        """Records an action taken by the agent."""
        thought = action_dict.get("thought", "No thought provided.")
        action = action_dict.get("action", "unknown")
        element_id = action_dict.get("element_id", "none")
        value = action_dict.get("value", "")

        # Format the entry into a readable sentence for the LLM
        entry = f"Step {step}: Thought: '{thought}' -> Executed: {action}"
        if element_id and element_id != "null":
            entry += f" on element '{element_id}'"
        if value:
            entry += f" with value '{value}'"

        self.history.append(entry)

    def get_memory_string(self) -> str:
        """Returns the formatted history to be injected into the LLM prompt."""
        if not self.history:
            return "No previous actions taken yet. This is step 1."
        
        return "\n".join(self.history)