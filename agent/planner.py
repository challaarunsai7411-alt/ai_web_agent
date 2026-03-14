import os
import json
from groq import AsyncGroq
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class TaskPlanner:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY") # Load the API key from the .env file
        
        # IF Python can't find it, use this fallback! 
        if not api_key:
            # PASTE YOUR ACTUAL GROQ KEY HERE (Keep the quotes!)
            api_key = "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" 
            
        # Initialize the Groq client
        self.client = AsyncGroq(api_key=api_key)
        self.system_instruction = """You are a strategic planning AI for an autonomous web agent.
        Your job is to take a user's high-level objective and break it down into a logical, sequential checklist of sub-tasks.
        
        You must respond ONLY with a valid JSON array of strings. Do not include markdown formatting like ```json.
        
        Example Input: "Search Wikipedia for Computer Science and click the first result."
        Example Output: [
            "Navigate to wikipedia.org or use a search engine to find Wikipedia.",
            "Locate the search bar and type 'Computer Science'.",
            "Submit the search query.",
            "Identify the first relevant article link in the search results and click it."
        ]
        """

    async def generate_plan(self, objective: str) -> list:
        """Generates a step-by-step plan for the given objective."""
        try:
            # Use the async (aio) version of the new SDK
            response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant", # Blazing fast, free model
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": f"Objective: {objective}"}
                ],
                temperature=0.0
            )
            
            plan_text = response.choices[0].message.content.strip()
            if plan_text.startswith("```json"):
                plan_text = plan_text[7:-3].strip()
            elif plan_text.startswith("```"):
                plan_text = plan_text[3:-3].strip()
                
            return json.loads(plan_text)
            
        except Exception as e:
            print(f"⚠️ Planner failed to generate a structured plan: {e}")
            return [objective]