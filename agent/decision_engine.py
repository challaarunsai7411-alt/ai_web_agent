import os
import json
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

class DecisionEngine:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            api_key = "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" # <-- Make sure your Groq key is still here!
            
        self.client = AsyncGroq(api_key=api_key)
        
        self.system_instruction = """You are an autonomous web navigation agent assisting a visually impaired user.
        Your job is to look at the current page elements and decide the very next action to take to achieve the user's objective.
        
        CRITICAL SURVIVAL RULES:
        1. POP-UPS FIRST: If you see a Cookie Consent banner, "Accept All", "Decline", "Close", or a Newsletter pop-up, your FIRST priority is to click it to get it out of the way. 
        2. IF YOU CAN'T FIND IT, SCROLL: If the element you are looking for is not in the 'Available Actionable Elements' list, use the 'scroll' action to look further down the page.
        
        You must respond ONLY in valid JSON format with no markdown formatting or extra text.
        
        Supported Actions:
        - "click": Clicks an element. Requires "element_id".
        - "type": Types text into an element. Requires "element_id" and "value".
        - "scroll": Scrolls down the page. No element_id required.
        - "read_content": Extracts the main text from an element (like an article body) to read to the user. Requires "element_id".
        - "done": The objective is complete.
        
        JSON Schema:
        {
            "thought": "Briefly explain your reasoning. If you see a pop-up, explain that you are closing it.",
            "action": "click" | "type" | "scroll" | "read_content" | "done",
            "element_id": "The exact ID of the target element, e.g., 'e1' (or null if action is scroll/done)",
            "value": "The text to type (only if action is 'type')"
        }"""

    async def get_next_action(self, objective: str, page_state: dict, memory_context: str) -> dict:
        user_prompt = f"""
        Objective: {objective}
        Current URL: {page_state.get('url')}
        Page Title: {page_state.get('title')}
        
        Available Actionable Elements:
        {json.dumps(page_state.get('elements', []), indent=2)}
        
        Past Actions History:
        {memory_context}
        
        CRITICAL RULE: Do not repeat a past action unless the page state indicates the previous action failed.
        """

        try:
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