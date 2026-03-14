import os
import io
from PIL import Image
from google import genai
from dotenv import load_dotenv

# Load the API key securely from your .env file
load_dotenv()

class VisionParser:
    def __init__(self):
        # Retrieve the key from the environment
        api_key = os.getenv("GEMINI_API_KEY")
        
        # Initialize the new SDK Client
        self.client = genai.Client(api_key=api_key)

    async def get_visual_guidance(self, page, objective: str) -> str:
        """Takes a screenshot and asks Gemini to visually find the next step."""
        try:
            print("📸 Snapping screenshot for visual analysis...")
            
            # Capture the current browser screen as binary data
            screenshot_bytes = await page.screenshot()
            
            # Convert bytes into an image object
            image = Image.open(io.BytesIO(screenshot_bytes))
            
            prompt = f"""
            You are a visual accessibility assistant. The underlying code for this webpage is broken or missing.
            Look at this screenshot. The user's overarching goal is: "{objective}"
            
            Based ONLY on the visual layout of this screen, what is the very next thing the user needs to click or type into?
            Briefly describe the element, its location, and the exact text on it (e.g., "The blue 'Log In' button in the top right corner").
            """
            
            # The new SDK takes a list of contents, mixing text and images perfectly
            response = await self.client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, image]
            )
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️ Vision parser error: {e}")
            return "Vision analysis failed."