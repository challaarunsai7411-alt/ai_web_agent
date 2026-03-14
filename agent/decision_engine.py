import os
import json
from groq import AsyncGroq
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class DecisionEngine:
    def __init__(self):
        # 1. CORRECT API KEY LOADING
        # It looks for the word "GEMINI_API_KEY" inside your .env file
        api_key = os.getenv("GROQ_API_KEY")
        
        # IF Python can't find it, use this fallback!
        if not api_key:
            # PASTE YOUR ACTUAL GROQ KEY HERE (Keep the quotes!)
            api_key = "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"
            
        self.client = AsyncGroq(api_key=api_key)        
        
        self.system_instruction = """You are an autonomous web navigation agent assisting a visually impaired user.
        Your job is to look at the current page elements and decide the very next action to take to achieve the user's objective.
        
        You must respond ONLY in valid JSON format with no markdown formatting or extra text.
        
        Supported Actions:
        - "click": Clicks an element. Requires "element_id".
        - "type": Types text into an element. Requires "element_id" and "value".
        - "captcha_detected": Use this immediately if you detect a CAPTCHA.
        - "done": The objective is complete.
        
        JSON Schema:
        {
            "thought": "Briefly explain your reasoning for this action.",
            "action": "click" | "type" | "captcha_detected" | "done",
            "element_id": "The exact ID of the target element, e.g., 'e1' (or null if action is done/captcha)",
            "value": "The text to type (only if action is 'type')"
        }"""

    async def get_next_action(self, objective: str, page_state: dict, memory_context: str) -> dict:
        """Asks the LLM to decide the next action based on current state and past memory."""
        
        user_prompt = f"""
        Objective: {objective}
        Current URL: {page_state.get('url')}
        Page Title: {page_state.get('title')}

        Visual System Override Hint (if any):
        {page_state.get('visual_hint', 'None')}
        
        Available Actionable Elements:
        {json.dumps(page_state.get('elements', []), indent=2)}
        
        Past Actions History:
        {memory_context}
        
        CRITICAL RULE: Do not repeat a past action unless the page state indicates the previous action failed.
        """

        try:
            # 3. NEW SDK ASYNC SYNTAX: client.aio.models.generate_content
            response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            
            action_json = response.choices[0].message.content.strip()
            if action_json.startswith("```json"):
                action_json = action_json[7:-3].strip()
            elif action_json.startswith("```"):
                action_json = action_json[3:-3].strip()
                
            return json.loads(action_json)
            
        except Exception as e:
            print(f"Error in Decision Engine: {e}")
            return {"action": "error", "thought": str(e)}